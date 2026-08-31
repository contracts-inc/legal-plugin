#!/usr/bin/env python3
"""レビュー結果から人のフィードバックを抽出する。

2つのレビュー経路に対応する。

  A. Word でレビューした場合（既定）— .docx を渡す
       1. Wordコメント（吹き出し）… 指摘の本文と、コメントが付いた本文箇所
       2. 変更履歴（Track Changes）… 挿入・削除された文字列
       3. 表 … .docx 内にレビューシートを含めた場合の「対応」「コメント」列

  B. Word が使えない場合（フォールバック）— レビューシートの .csv / .xlsx を渡す
       決定事項ごとの「対応」（承認 / 修正 / 保留）と「コメント」列

標準ライブラリのみで動作する。.docx は ZIP + OOXML であり、python-docx は
コメントの読み取りを提供しないため word/comments.xml を直接解析する。

使い方:
    python scripts/extract_review_feedback.py reviewed.docx
    python scripts/extract_review_feedback.py review-sheet.csv
    python scripts/extract_review_feedback.py reviewed.docx --format text

出力（既定は JSON）:
    {
      "source": "docx" | "csv",
      "comments": [{"id", "author", "date", "text", "anchor_text", "paragraph_text"}],
      "tracked_changes": [{"type", "author", "date", "text", "paragraph_text"}],
      "sheets": [{"headers": [...], "rows": [{列名: 値}]}],
      "decisions": [{"row", "item", "action", "comment"}],
      "summary": {...}
    }

`decisions` はレビューシート（「対応」列を持つ表）から抽出した決定事項で、
.docx 内の表と .csv のどちらから読んでも同じ形になる。
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import zipfile
from xml.etree import ElementTree

# WordprocessingML の名前空間。OOXML 仕様で固定されており変更されない。
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

DOCUMENT_PART = "word/document.xml"
COMMENTS_PART = "word/comments.xml"

# レビューシートの列名。review-output.md で定義した見出しと一致させる。
ACTION_COLUMN = "対応"
COMMENT_COLUMN = "コメント"
ITEM_COLUMN = "項目"
SECTION_COLUMN = "節"

# 「対応」列に記入される値の正規化表。キーは小文字・空白除去済みの形で持ち、
# 照合時も同じ正規化をかけるため "OK" / "Ok" / "ok" はすべて一致する。
ACTION_ALIASES = {
    "承認": "approved",
    "承認する": "approved",
    "ok": "approved",
    "可": "approved",
    "問題なし": "approved",
    "修正": "revise",
    "修正する": "revise",
    "要修正": "revise",
    "ng": "revise",
    "不可": "revise",
    "保留": "hold",
    "保留する": "hold",
    "未定": "hold",
    "検討中": "hold",
}


def _normalize_action(raw: str) -> str:
    """「対応」列の記入値を approved / revise / hold / unanswered に正規化する。

    表記揺れ（全角空白、大文字小文字、末尾の句点）を吸収する。
    未記入は unanswered、対応表に無い値は記入値をそのまま返して
    「想定外の記入」として扱えるようにする。
    """
    cleaned = raw.replace("\u3000", " ").strip().rstrip("。.").casefold()
    if not cleaned:
        return "unanswered"
    return ACTION_ALIASES.get(cleaned, raw.strip())


def _attr(element: ElementTree.Element, name: str, default: str = "") -> str:
    """w: 名前空間付き属性を取得する。属性が無い場合は default を返す。"""
    return element.get(W + name, default)


def _text_of(element: ElementTree.Element, tags: tuple[str, ...]) -> str:
    """要素の子孫から、指定タグのテキストを文書順に連結する。"""
    return "".join(node.text or "" for node in element.iter() if node.tag in tags)


def _load_part(archive: zipfile.ZipFile, part_name: str) -> ElementTree.Element | None:
    """ZIP 内の XML パートを読み込む。存在しない場合は None を返す。

    コメントが1件も無い .docx には word/comments.xml が含まれないため、
    欠損は異常ではなく「コメントなし」として扱う。
    """
    try:
        raw = archive.read(part_name)
    except KeyError:
        return None
    try:
        return ElementTree.fromstring(raw)
    except ElementTree.ParseError as error:
        # 破損ファイルでトレースバックを出さず、原因が分かる形で止める
        raise SystemExit(f"{part_name} を解析できません（ファイルが破損している可能性）: {error}")


def _build_parent_map(root: ElementTree.Element) -> dict[ElementTree.Element, ElementTree.Element]:
    """ElementTree に親参照が無いため、親を引くための対応表を作る。"""
    return {child: parent for parent in root.iter() for child in parent}


def _containing_paragraph_text(
    element: ElementTree.Element,
    parents: dict[ElementTree.Element, ElementTree.Element],
) -> str:
    """要素を含む段落（w:p）のテキストを返す。段落が見つからない場合は空文字。"""
    node: ElementTree.Element | None = element
    while node is not None:
        if node.tag == W + "p":
            return _text_of(node, (W + "t",))
        node = parents.get(node)
    return ""


def _sort_key(value: str) -> tuple[int, object]:
    """コメントIDは数値のことが多いが、文字列の場合もあるため両対応にする。"""
    try:
        return (0, int(value))
    except (TypeError, ValueError):
        return (1, value or "")


def extract_comments(
    document: ElementTree.Element,
    comments: ElementTree.Element | None,
) -> list[dict[str, str]]:
    """コメント本文と、コメントが付けられた本文箇所を対応付けて返す。

    コメント本文は word/comments.xml、対象箇所は word/document.xml の
    w:commentRangeStart 〜 w:commentRangeEnd に囲まれた範囲から取得する。
    """
    if comments is None:
        return []

    bodies: dict[str, dict[str, str]] = {}
    for comment in comments.iter(W + "comment"):
        comment_id = _attr(comment, "id")
        bodies[comment_id] = {
            "id": comment_id,
            "author": _attr(comment, "author"),
            "date": _attr(comment, "date"),
            "text": _text_of(comment, (W + "t",)),
        }

    # 対象箇所を文書順に1回走査して収集する。
    # ElementTree.iter() は文書順（先行順）で要素を返すため、
    # commentRangeStart/End の間に現れた w:t を該当コメントに割り当てられる。
    anchors: dict[str, list[str]] = {}
    paragraph_of: dict[str, str] = {}
    open_ids: set[str] = set()
    parents = _build_parent_map(document)

    for node in document.iter():
        tag = node.tag
        if tag == W + "p":
            # 段落をまたぐコメント範囲では、段落境界に改行を入れて語の連結を防ぐ
            for comment_id in open_ids:
                if anchors.get(comment_id):
                    anchors[comment_id].append("\n")
        elif tag == W + "commentRangeStart":
            comment_id = _attr(node, "id")
            open_ids.add(comment_id)
            anchors.setdefault(comment_id, [])
            paragraph_of.setdefault(comment_id, _containing_paragraph_text(node, parents))
        elif tag == W + "commentRangeEnd":
            open_ids.discard(_attr(node, "id"))
        elif tag == W + "commentReference":
            # 範囲指定のないコメント（挿入位置のみ）でも段落を記録する
            comment_id = _attr(node, "id")
            anchors.setdefault(comment_id, [])
            paragraph_of.setdefault(comment_id, _containing_paragraph_text(node, parents))
        elif tag == W + "t" and open_ids:
            for comment_id in open_ids:
                anchors[comment_id].append(node.text or "")

    results = [
        {
            **body,
            "anchor_text": "".join(anchors.get(comment_id, [])).strip(),
            "paragraph_text": paragraph_of.get(comment_id, ""),
        }
        for comment_id, body in bodies.items()
    ]
    results.sort(key=lambda item: _sort_key(item["id"]))
    return results


def extract_tracked_changes(document: ElementTree.Element) -> list[dict[str, str]]:
    """変更履歴を返す。

    対応する種別:
      w:ins      挿入
      w:del      削除
      w:moveTo   移動先（移動された文字列の挿入側）
      w:moveFrom 移動元（移動された文字列の削除側）

    Word の「文字列の移動」は w:ins / w:del ではなく w:moveTo / w:moveFrom として
    記録されるため、これを見ないと移動の指摘を取りこぼす。
    """
    # タグ -> (種別名, テキストを持つタグ)
    change_kinds = {
        W + "ins": ("insertion", (W + "t",)),
        W + "del": ("deletion", (W + "delText",)),
        W + "moveTo": ("move_to", (W + "t",)),
        W + "moveFrom": ("move_from", (W + "delText", W + "t")),
    }

    parents = _build_parent_map(document)
    changes = []

    for node in document.iter():
        kind = change_kinds.get(node.tag)
        if kind is None:
            continue
        change_type, tags = kind

        text = _text_of(node, tags)
        if not text:
            # 書式のみの変更（テキストを伴わない）は指摘として扱わない
            continue
        changes.append(
            {
                "type": change_type,
                "author": _attr(node, "author"),
                "date": _attr(node, "date"),
                "text": text,
                "paragraph_text": _containing_paragraph_text(node, parents),
            }
        )
    return changes


def extract_docx_tables(document: ElementTree.Element) -> list[dict[str, object]]:
    """.docx 内の表を抽出する。先頭行を見出しとして各行を辞書化する。"""
    tables = []
    for table in document.iter(W + "tbl"):
        rows = []
        for row in table.findall(W + "tr"):
            cells = [_text_of(cell, (W + "t",)).strip() for cell in row.findall(W + "tc")]
            rows.append(cells)
        if not rows:
            continue
        tables.append(_rows_to_sheet(rows[0], rows[1:]))
    return tables


def _rows_to_sheet(headers: list[str], body_rows: list[list[str]]) -> dict[str, object]:
    """見出し行とデータ行から、列名で引ける表を作る。"""
    normalized_headers = [header.strip() for header in headers]
    rows = []
    for cells in body_rows:
        # 見出しより列が少ない行は空文字で補い、多い行は余剰を捨てる
        padded = (cells + [""] * len(normalized_headers))[: len(normalized_headers)]
        rows.append({header: value.strip() for header, value in zip(normalized_headers, padded)})
    return {"headers": normalized_headers, "rows": rows}


def read_csv_sheet(path: str) -> dict[str, object]:
    """レビューシートの CSV を読み込む。

    Excel が UTF-8 BOM を付けて保存するため utf-8-sig で開く。
    デコードできない場合は Shift_JIS（cp932）で読み直す。
    """
    for encoding in ("utf-8-sig", "utf-16", "cp932"):
        try:
            with open(path, newline="", encoding=encoding) as handle:
                rows = [row for row in csv.reader(handle)]
            break
        except UnicodeDecodeError:
            continue
        except UnicodeError:
            # utf-16 は BOM が無いと UnicodeError になることがある
            continue
    else:
        raise SystemExit(
            f"文字コードを判別できませんでした（UTF-8 / UTF-16 / Shift_JIS のいずれでもない）: {path}"
        )

    rows = [row for row in rows if any(cell.strip() for cell in row)]
    if not rows:
        raise SystemExit(f"レビューシートが空です: {path}")
    return _rows_to_sheet(rows[0], rows[1:])


# xlsx（SpreadsheetML）の名前空間。OOXML 仕様で固定。
X = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def _column_index(cell_reference: str) -> int:
    """セル参照（"B3"）から 0 始まりの列番号を返す。空欄セルの詰まりを防ぐために使う。"""
    letters = "".join(ch for ch in cell_reference if ch.isalpha())
    index = 0
    for ch in letters:
        index = index * 26 + (ord(ch.upper()) - ord("A") + 1)
    return index - 1


def read_xlsx_sheet(path: str) -> dict[str, object]:
    """レビューシートの .xlsx を読み込む（先頭シートのみ）。

    Excel の既定の保存形式が .xlsx であるため、CSV に変換せず渡された場合にも
    対応する。xlsx は ZIP + SpreadsheetML なので、標準ライブラリだけで読める。
    """
    try:
        archive = zipfile.ZipFile(path)
    except zipfile.BadZipFile:
        raise SystemExit(
            f".xlsx として読めません（ZIP形式ではありません）。"
            f"拡張子だけを変更したファイルではないか確認してください: {path}"
        )

    with archive:
        # 共有文字列（セルの文字列は多くがここに集約される）
        shared: list[str] = []
        try:
            shared_root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
        except KeyError:
            shared_root = None
        except ElementTree.ParseError as error:
            raise SystemExit(f"xl/sharedStrings.xml を解析できません: {path}（{error}）")
        if shared_root is not None:
            for item in shared_root.findall(X + "si"):
                shared.append("".join(node.text or "" for node in item.iter(X + "t")))

        # 先頭シートを読む。シート名は問わない（レビューシートは単一シート前提）。
        sheet_names = sorted(
            name for name in archive.namelist() if name.startswith("xl/worksheets/sheet")
        )
        if not sheet_names:
            raise SystemExit(f"ワークシートが見つかりません: {path}")
        try:
            sheet_root = ElementTree.fromstring(archive.read(sheet_names[0]))
        except ElementTree.ParseError as error:
            raise SystemExit(f"{sheet_names[0]} を解析できません: {path}（{error}）")

    rows = []
    for row_node in sheet_root.iter(X + "row"):
        cells: list[str] = []
        for cell in row_node.findall(X + "c"):
            position = _column_index(cell.get("r", ""))
            # 空欄セルは XML から省略されるため、位置を見て埋める
            while len(cells) < position:
                cells.append("")
            cell_type = cell.get("t", "")
            if cell_type == "s":
                value_node = cell.find(X + "v")
                index = int(value_node.text) if value_node is not None and value_node.text else -1
                cells.append(shared[index] if 0 <= index < len(shared) else "")
            elif cell_type == "inlineStr":
                cells.append("".join(node.text or "" for node in cell.iter(X + "t")))
            else:
                value_node = cell.find(X + "v")
                cells.append(value_node.text or "" if value_node is not None else "")
        rows.append(cells)

    rows = [row for row in rows if any(cell.strip() for cell in row)]
    if not rows:
        raise SystemExit(f"レビューシートが空です: {path}")
    return _rows_to_sheet(rows[0], rows[1:])


def extract_decisions(sheets: list[dict[str, object]]) -> list[dict[str, str]]:
    """「対応」列を持つ表を決定事項として取り出し、記入値を正規化する。

    `action` は approved / revise / hold / unanswered、または想定外の記入値になる。
    `row` は表をまたいで通し番号を振る（表ごとに1から振り直すと重複して参照できない）。
    """
    decisions = []
    row_number = 0
    for sheet in sheets:
        headers = sheet["headers"]
        if ACTION_COLUMN not in headers:
            continue
        # 項目名の列を決める。「項目」が無ければ「対応」「コメント」以外の最初の列を使う。
        label_column = ITEM_COLUMN if ITEM_COLUMN in headers else next(
            (header for header in headers if header not in (ACTION_COLUMN, COMMENT_COLUMN)),
            "",
        )
        for row in sheet["rows"]:
            row_number += 1
            decisions.append(
                {
                    "row": str(row_number),
                    "section": row.get(SECTION_COLUMN, ""),
                    "item": row.get(label_column, ""),
                    "action": _normalize_action(row.get(ACTION_COLUMN, "")),
                    "comment": row.get(COMMENT_COLUMN, ""),
                }
            )
    return decisions


def extract(path: str) -> dict[str, object]:
    """.docx / .csv / .xlsx からフィードバックを抽出する。"""
    if not os.path.exists(path):
        raise SystemExit(f"ファイルが見つかりません: {path}")

    extension = os.path.splitext(path)[1].lower()
    comments: list[dict[str, str]] = []
    tracked_changes: list[dict[str, str]] = []

    if extension == ".csv":
        sheets = [read_csv_sheet(path)]
        source = "csv"
    elif extension == ".xlsx":
        sheets = [read_xlsx_sheet(path)]
        source = "xlsx"
    elif extension == ".docx":
        try:
            archive = zipfile.ZipFile(path)
        except zipfile.BadZipFile:
            raise SystemExit(f".docx として読めません（ZIP形式ではありません）: {path}")
        with archive:
            document = _load_part(archive, DOCUMENT_PART)
            if document is None:
                raise SystemExit(
                    f"{DOCUMENT_PART} が含まれていません。.docx ではない可能性があります: {path}"
                )
            comments_part = _load_part(archive, COMMENTS_PART)
        comments = extract_comments(document, comments_part)
        tracked_changes = extract_tracked_changes(document)
        sheets = extract_docx_tables(document)
        source = "docx"
    else:
        raise SystemExit(
            f"対応していない拡張子です（.docx / .csv / .xlsx を指定してください）: {path}"
        )

    decisions = extract_decisions(sheets)
    return {
        "source": source,
        "comments": comments,
        "tracked_changes": tracked_changes,
        "sheets": sheets,
        "decisions": decisions,
        "summary": {
            "comments": len(comments),
            "insertions": sum(1 for change in tracked_changes if change["type"] == "insertion"),
            "deletions": sum(1 for change in tracked_changes if change["type"] == "deletion"),
            "moves": sum(1 for change in tracked_changes if change["type"].startswith("move")),
            "sheets": len(sheets),
            "decisions": len(decisions),
            "approved": sum(1 for item in decisions if item["action"] == "approved"),
            "revise": sum(1 for item in decisions if item["action"] == "revise"),
            "hold": sum(1 for item in decisions if item["action"] == "hold"),
            "unanswered": sum(1 for item in decisions if item["action"] == "unanswered"),
            "unrecognized": sum(
                1
                for item in decisions
                if item["action"] not in ("approved", "revise", "hold", "unanswered")
            ),
        },
    }


def render_text(result: dict[str, object]) -> str:
    """人が読める形に整形する（確認用。反映処理には JSON を使う）。"""
    summary = result["summary"]
    lines = [
        "取得元: {source}".format(**result),
        "コメント {comments}件 / 挿入 {insertions}件 / 削除 {deletions}件 / 移動 {moves}件".format(
            **summary
        ),
    ]
    if summary["decisions"]:
        lines.append(
            "決定事項 {decisions}件（承認 {approved} / 修正 {revise} / 保留 {hold} / 未記入 {unanswered} / 判別不能 {unrecognized}）".format(
                **summary
            )
        )

    for comment in result["comments"]:
        lines.append("")
        lines.append(f"[コメント {comment['id']}] {comment['author']}")
        if comment["anchor_text"]:
            lines.append(f"  対象: {comment['anchor_text']}")
        elif comment["paragraph_text"]:
            lines.append(f"  対象段落: {comment['paragraph_text']}")
        lines.append(f"  指摘: {comment['text']}")

    for change in result["tracked_changes"]:
        label = {
            "insertion": "挿入",
            "deletion": "削除",
            "move_to": "移動先",
            "move_from": "移動元",
        }.get(change["type"], change["type"])
        lines.append("")
        lines.append(f"[{label}] {change['author']}: {change['text']}")

    for decision in result["decisions"]:
        if decision["action"] == "approved" and not decision["comment"]:
            continue  # 承認かつコメントなしは対応不要
        lines.append("")
        label = f"{decision['section']} {decision['item']}".strip()
        lines.append(f"[決定 {decision['row']}] {label} → {decision['action']}")
        if decision["comment"]:
            lines.append(f"  コメント: {decision['comment']}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="レビュー済みの .docx（コメント・変更履歴）または レビューシートの .csv からフィードバックを抽出する"
    )
    parser.add_argument(
        "path", help="レビュー済みの .docx、またはレビューシートの .csv / .xlsx"
    )
    parser.add_argument(
        "--format",
        choices=("json", "text"),
        default="json",
        help="出力形式（既定: json）",
    )
    args = parser.parse_args()

    result = extract(args.path)
    if args.format == "text":
        print(render_text(result))
    else:
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        print()


if __name__ == "__main__":
    main()
