#!/usr/bin/env python3
"""雛形(.docx)のプレースホルダーを差し込み値で置換してドラフトを出力するスクリプト。

方針:
- 雛形の体裁（フォント・段落・表）を維持したままプレースホルダーのみを置換する。
- プレースホルダーは ``{{key}}`` 形式（例: ``{{contract_name}}``）。
- 置換値に含まれない項目は ``※要確認`` として残す運用を推奨（本スクリプトは
  未指定キーを既定で ``※要確認：<key>`` に置換する。--keep-unknown で原文維持も可）。

依存: python-docx (``pip install python-docx``)

使い方:
    python fill_docx.py \
        --template assets/amendment-template.docx \
        --output draft.docx \
        --data data.json

data.json 例:
    {
      "contract_name": "業務委託基本契約書",
      "contract_date": "2024年4月1日",
      "party_a": "株式会社サンプル",
      "party_b": "サンプル合同会社",
      "target_article": "第5条（契約期間）",
      "before_text": "本契約の有効期間は...",
      "after_text": "本契約の有効期間は...（1年間延長）",
      "effective_date": "2025年4月1日"
    }
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from docx import Document  # type: ignore
except ImportError:  # pragma: no cover
    sys.stderr.write(
        "python-docx が必要です。`pip install python-docx` を実行してください。\n"
    )
    raise

PLACEHOLDER_RE = re.compile(r"\{\{\s*([\w.-]+)\s*\}\}")


def _replace_in_runs(paragraph, data: dict, keep_unknown: bool) -> None:
    """段落内のプレースホルダーを置換する。

    プレースホルダーが複数 run にまたがる場合に備え、段落テキストを結合して
    置換したうえで、先頭 run にまとめて書き戻す（体裁は先頭 run のスタイルを踏襲）。
    """
    full_text = "".join(run.text for run in paragraph.runs)
    if "{{" not in full_text:
        return

    def _sub(match: re.Match) -> str:
        key = match.group(1)
        if key in data and data[key] not in (None, ""):
            return str(data[key])
        return match.group(0) if keep_unknown else f"※要確認：{key}"

    new_text = PLACEHOLDER_RE.sub(_sub, full_text)
    if new_text == full_text:
        return

    if paragraph.runs:
        paragraph.runs[0].text = new_text
        for run in paragraph.runs[1:]:
            run.text = ""
    else:  # プレーンな段落
        paragraph.add_run(new_text)


def _iter_paragraphs(document):
    yield from document.paragraphs
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                yield from cell.paragraphs


def fill_template(template: Path, output: Path, data: dict, keep_unknown: bool) -> list[str]:
    """雛形を差し込み、未解決プレースホルダーの一覧を返す。"""
    document = Document(str(template))
    for paragraph in _iter_paragraphs(document):
        _replace_in_runs(paragraph, data, keep_unknown)

    # 未解決（※要確認 または {{...}}）の検出
    unresolved: list[str] = []
    for paragraph in _iter_paragraphs(document):
        text = paragraph.text
        for key in PLACEHOLDER_RE.findall(text):
            unresolved.append(f"{{{{{key}}}}}")
        for m in re.findall(r"※要確認：([A-Za-z0-9_.-]+)", text):
            unresolved.append(f"※要確認：{m}")

    output.parent.mkdir(parents=True, exist_ok=True)
    document.save(str(output))
    return sorted(set(unresolved))


def main() -> int:
    parser = argparse.ArgumentParser(description="法務文書ドラフトの雛形差し込み")
    parser.add_argument("--template", required=True, type=Path, help="雛形 .docx のパス")
    parser.add_argument("--output", required=True, type=Path, help="出力 .docx のパス")
    parser.add_argument("--data", required=True, type=Path, help="差し込み値の JSON パス")
    parser.add_argument(
        "--keep-unknown",
        action="store_true",
        help="未指定キーを ※要確認 に変換せず {{key}} のまま残す",
    )
    args = parser.parse_args()

    data = json.loads(args.data.read_text(encoding="utf-8"))
    unresolved = fill_template(args.template, args.output, data, args.keep_unknown)

    print(f"ドラフトを出力しました: {args.output}")
    if unresolved:
        print("\n【確認事項（未解決プレースホルダー）】")
        for item in unresolved:
            print(f"  - {item}")
        print("\n上記は推測で埋めていません。法務担当者による確認・入力が必要です。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
