#!/usr/bin/env python3
"""プラットフォーム別のスキルバンドルを dist/<platform>/ に生成する。

使い方:
    python scripts/build.py <platform>

src/ 配下のファイルツリーをそのまま dist/<platform>/ に写し取る。
Markdown は Jinja2 テンプレートとして `platform` 変数を渡してレンダリングし、
それ以外（.docx / .py / .json など）はバイナリ安全にコピーする。
プラットフォーム固有の差分は、各 Markdown 内で
`{% if platform == "claude" %}` のような条件分岐として表現する。

プラットフォーム専用のマニフェストは PLATFORM_DIRS で制御する。
  - src/.claude-bundle/  -> claude ビルドの .claude-plugin/ 配下
  - src/.copilot-bundle/ -> copilot ビルドのパッケージルート直下
  - src/.chatgpt-bundle/ -> chatgpt ビルドの .codex-plugin/ 配下

マニフェストの version は CHANGELOG.md の最新エントリを唯一の情報源として
ビルド時に埋め込む（VERSION_STAMPED_FILES）。src 側の値は参照しない。

    python scripts/build.py --print-version  # CHANGELOG.md の最新バージョンを出力

配布 ZIP は「アーカイブ直下がプラグインルート」でなければインストーラに拒否される。
その検証は --verify-archive で行う。

    python scripts/build.py chatgpt --verify-archive chatgpt-skill-bundle.zip
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import zipfile
from pathlib import Path
from typing import Iterator

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
DIST_DIR = PROJECT_ROOT / "dist"
CHANGELOG_PATH = PROJECT_ROOT / "CHANGELOG.md"

# .github/workflows/package-plugin.yml の matrix.platform と揃える
SUPPORTED_PLATFORMS = ("chatgpt", "claude", "copilot")

# Jinja2 でレンダリングする拡張子。それ以外はそのままコピーする
TEMPLATE_SUFFIXES = {".md"}

# バンドルに含めないファイル / ディレクトリ名
EXCLUDED_NAMES = {".DS_Store", "Thumbs.db", "__pycache__", ".pytest_cache"}

# 特定プラットフォーム専用の src 配下ディレクトリ（キーは src 直下のディレクトリ名）。
# 対象プラットフォーム以外のビルドからは除外し、`dest` の位置に再配置する。
#   - .claude-bundle: Claude はマニフェストを .claude-plugin/ 配下に置く
#   - .copilot-bundle: Copilot (Teams アプリ) のマニフェストは
#                      アイコンや agentSkills をパッケージルート基準の相対パスで参照するため、
#                      中身をパッケージルート直下に展開する（dest = ""）。
#   - .chatgpt-bundle: ChatGPT はマニフェストを .codex-plugin/ 配下に置く
PLATFORM_DIRS = {
    ".claude-bundle": {"platform": "claude", "dest": ".claude-plugin"},
    ".copilot-bundle": {"platform": "copilot", "dest": ""},
    ".chatgpt-bundle": {"platform": "chatgpt", "dest": ".codex-plugin"},
}

# version を CHANGELOG.md の最新バージョンで上書きする JSON（src からの相対パス）。
# 各プラットフォームのマニフェストでバージョンが食い違うのを防ぐため、
# src 側の値は編集不要（プレースホルダのままでよい）とし、ビルド時に必ず差し替える。
VERSION_STAMPED_FILES = frozenset(
    {
        ".claude-bundle/plugin.json",
        ".chatgpt-bundle/plugin.json",
        ".copilot-bundle/manifest.json",
    }
)

# CHANGELOG.md の見出し（例: `## [1.1.1] - 2026/07/24`）からバージョンを取り出す
CHANGELOG_HEADING_PATTERN = re.compile(r"^##\s*\[\s*v?(?P<version>[^\]\s]+)\s*\]")

# Copilot (Teams アプリ) の manifest.json は version に 3 桁の semver を要求するため、
# CHANGELOG 側の表記もこれに揃える
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")

# プラットフォームごとにバンドルから除外するファイル（src からの相対パス）。
# copilot は manifest.json の agentConnectors で MCP サーバーを宣言するため、
# .mcp.json は二重定義になり不要。
PLATFORM_EXCLUDED_FILES = {
    "copilot": {".mcp.json"},
}

# 各プラットフォームのバンドルに必須のファイル（バンドル内の相対パス）。
# アーカイブ直下にこれらが並んでいることがインストーラの受け入れ条件になる。
REQUIRED_FILES = {
    "claude": (".claude-plugin/plugin.json",),
    "copilot": ("manifest.json", "color.png", "outline.png"),
    "chatgpt": (".codex-plugin/plugin.json",),
}


def resolve_version(changelog_path: Path = CHANGELOG_PATH) -> str:
    """CHANGELOG.md の先頭に現れるバージョン見出しからバージョン文字列を返す。

    「最新版は常に一番上に追記する」という CHANGELOG の運用を前提に、
    最初にマッチした見出しを最新バージョンとして扱う。
    """
    if not changelog_path.is_file():
        raise SystemExit(f"CHANGELOG が見つかりません: {changelog_path}")

    for line in changelog_path.read_text(encoding="utf-8").splitlines():
        match = CHANGELOG_HEADING_PATTERN.match(line)
        if match is None:
            continue

        version = match.group("version")
        if not VERSION_PATTERN.match(version):
            raise SystemExit(
                f"CHANGELOG の最新バージョンが x.y.z 形式ではありません: {version}\n"
                f"  {changelog_path} の見出しを `## [1.2.3] - YYYY/MM/DD` 形式にしてください。"
            )
        return version

    raise SystemExit(
        f"CHANGELOG からバージョンを取得できませんでした: {changelog_path}\n"
        f"  `## [1.2.3] - YYYY/MM/DD` 形式の見出しが必要です。"
    )


def write_versioned_json(src_path: Path, dest_path: Path, version: str) -> None:
    """JSON の version を差し替えて出力する。"""
    try:
        manifest = json.loads(src_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise SystemExit(f"JSON として解析できません: {src_path} ({error})") from error

    if not isinstance(manifest, dict):
        raise SystemExit(f"JSON のトップレベルがオブジェクトではありません: {src_path}")

    # 既存キーの位置を保つため、キーが無い場合のみ末尾に追加される
    manifest["version"] = version
    dest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def verify_archive(platform: str, archive_path: Path) -> None:
    """配布 ZIP の直下がプラグインルートになっているか検証する。

    インストーラは アーカイブ直下の `.codex-plugin/plugin.json` などを見て
    プラグインかどうかを判定するため、以下は受け付けられない。
      - ZIP の中に ZIP が入っている（GitHub Actions のアーティファクトを
        そのままダウンロードすると起きる）
      - 余計なトップレベルディレクトリで包まれている
    """
    if not archive_path.is_file():
        raise SystemExit(f"検証対象の ZIP が見つかりません: {archive_path}")

    with zipfile.ZipFile(archive_path) as archive:
        names = [name for name in archive.namelist() if not name.endswith("/")]

    if not names:
        raise SystemExit(f"[{platform}] ZIP が空です: {archive_path}")

    problems: list[str] = []

    # zip -r で `./` プレフィックスが付くとパス判定に失敗しうるため正規化して比較する
    normalized = {name[2:] if name.startswith("./") else name for name in names}

    missing = [
        required
        for required in REQUIRED_FILES.get(platform, ())
        if required not in normalized
    ]
    if missing:
        problems.append(
            f"アーカイブ直下に必須ファイルがありません: {', '.join(missing)}"
        )

    nested_zips = sorted(
        name for name in normalized if name.lower().endswith(".zip")
    )
    if nested_zips:
        problems.append(
            f"ZIP の中に ZIP が入っています（二重 ZIP）: {', '.join(nested_zips)}\n"
            f"    GitHub Actions のアーティファクトをダウンロードしたものではなく、"
            f"バンドル本体の ZIP を使ってください。"
        )

    # 全ファイルが単一ディレクトリ配下にある場合は、余計な階層で包まれている
    top_levels = {Path(name).parts[0] for name in normalized}
    if len(top_levels) == 1 and not any(
        Path(name).parent == Path(".") for name in normalized
    ):
        problems.append(
            f"余計なトップレベルディレクトリで包まれています: {top_levels.pop()}/\n"
            f"    ZIP はバンドルディレクトリの中で `zip -r <出力> .` として作成してください。"
        )

    if problems:
        detail = "\n".join(f"  - {problem}" for problem in problems)
        raise SystemExit(f"[{platform}] ZIP の構成が不正です: {archive_path}\n{detail}")

    print(
        f"[{platform}] ZIP 構成 OK: {archive_path} "
        f"（{len(names)} ファイル / 必須ファイルはアーカイブ直下）"
    )


def iter_bundle_files(root: Path, platform: str) -> Iterator[tuple[Path, Path]]:
    """(コピー元のパス, バンドル内の相対パス) の組を再帰的に列挙する。

    除外対象の名前を含むパス、当該プラットフォームで除外指定されたファイル、
    他プラットフォーム専用のディレクトリはスキップする。
    プラットフォーム専用ディレクトリの中身は PLATFORM_DIRS の `dest` へ再配置する。
    """
    excluded_files = PLATFORM_EXCLUDED_FILES.get(platform, frozenset())

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue

        relative_path = path.relative_to(root)
        relative_parts = relative_path.parts
        if any(part in EXCLUDED_NAMES for part in relative_parts):
            continue

        if relative_path.as_posix() in excluded_files:
            continue

        entry = PLATFORM_DIRS.get(relative_parts[0])
        if entry is None:
            yield path, Path(*relative_parts)
            continue

        if platform != entry["platform"]:
            continue

        # 専用ディレクトリ名を除いた残りを dest 配下へ移す（dest="" ならルート直下）
        inner_parts = relative_parts[1:]
        dest = entry["dest"]
        yield path, Path(dest, *inner_parts) if dest else Path(*inner_parts)


def build(platform: str) -> Path:
    """指定プラットフォーム向けのバンドルを生成し、出力ディレクトリを返す。"""
    if not SRC_DIR.is_dir():
        raise SystemExit(f"src ディレクトリが見つかりません: {SRC_DIR}")

    # --print-version だけを使う CI ジョブに Jinja2 のインストールを強いないよう遅延 import する
    from jinja2 import Environment, FileSystemLoader, StrictUndefined

    version = resolve_version()
    out_dir = DIST_DIR / platform
    # 前回ビルドの残骸を持ち込まないよう、出力先を作り直す
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    env = Environment(
        loader=FileSystemLoader(str(SRC_DIR)),
        # 制御タグを独立行に書いても余分な空行が残らないようにする。
        # Markdown では空行が箇条書きを分断するため必須。
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
        # platform 以外の未定義変数を静かに空文字へ落とさず、ビルドを失敗させる
        undefined=StrictUndefined,
    )

    rendered_count = 0
    copied_count = 0
    stamped_count = 0
    written: dict[Path, Path] = {}

    for src_path, relative_dest in iter_bundle_files(SRC_DIR, platform):
        source_rel = src_path.relative_to(SRC_DIR)

        # ルート直下への展開があるため、出力先の衝突を検知する
        if relative_dest in written:
            raise SystemExit(
                f"[{platform}] 出力先が衝突しています: {relative_dest.as_posix()}\n"
                f"  {written[relative_dest].as_posix()} と {source_rel.as_posix()}"
            )
        written[relative_dest] = source_rel

        dest_path = out_dir / relative_dest
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        stamped = source_rel.as_posix() in VERSION_STAMPED_FILES

        if stamped:
            # マニフェストのバージョンは CHANGELOG.md を唯一の情報源として埋め込む
            write_versioned_json(src_path, dest_path, version)
            stamped_count += 1
        elif src_path.suffix.lower() in TEMPLATE_SUFFIXES:
            # テンプレートの読み込みは src からの相対パスで行う
            template = env.get_template(source_rel.as_posix())
            dest_path.write_text(
                template.render(platform=platform), encoding="utf-8"
            )
            rendered_count += 1
        else:
            shutil.copy2(src_path, dest_path)
            copied_count += 1

        suffix = f" (version={version})" if stamped else ""
        if source_rel == relative_dest:
            print(f"  {relative_dest.as_posix()}{suffix}")
        else:
            print(f"  {source_rel.as_posix()} -> {relative_dest.as_posix()}{suffix}")

    # 必須ファイルの取りこぼしを検知する（例: claude のプラグインマニフェスト）
    for required in REQUIRED_FILES.get(platform, ()):
        if not (out_dir / required).is_file():
            raise SystemExit(
                f"[{platform}] 必須ファイルがバンドルに含まれていません: {required}\n"
                f"  src/ 配下に対応するファイルがあるか、"
                f"PLATFORM_DIRS の再配置設定を確認してください。"
            )

    # マニフェストのリネーム等でバージョン埋め込みが静かに抜け落ちるのを防ぐ
    expected_stamps = {
        stamped
        for stamped in VERSION_STAMPED_FILES
        if PLATFORM_DIRS.get(Path(stamped).parts[0], {}).get("platform") == platform
    }
    missing_stamps = expected_stamps - {
        source.as_posix() for source in written.values()
    }
    if missing_stamps:
        raise SystemExit(
            f"[{platform}] バージョンを埋め込むマニフェストが見つかりません: "
            f"{', '.join(sorted(missing_stamps))}\n"
            f"  VERSION_STAMPED_FILES のパスが src/ の構成と一致しているか確認してください。"
        )

    print(
        f"[{platform}] バージョン埋め込み {stamped_count} 件"
        f" / レンダリング {rendered_count} 件 / コピー {copied_count} 件"
        f" -> {out_dir.relative_to(PROJECT_ROOT)} (version={version})"
    )
    return out_dir


def main() -> None:
    parser = argparse.ArgumentParser(
        description="src/ からプラットフォーム別のスキルバンドルを生成する"
    )
    parser.add_argument(
        "platform",
        nargs="?",
        choices=SUPPORTED_PLATFORMS,
        help="ビルド対象のプラットフォーム",
    )
    parser.add_argument(
        "--print-version",
        action="store_true",
        help="CHANGELOG.md の最新バージョンを出力して終了する（CI のタグ解決用）",
    )
    parser.add_argument(
        "--verify-archive",
        metavar="ZIP",
        type=Path,
        help="ビルドせず、既存の配布 ZIP の構成だけを検証する",
    )
    args = parser.parse_args()

    if args.print_version:
        print(resolve_version())
        return

    if args.platform is None:
        parser.error("platform を指定してください（--print-version 以外の場合は必須）")

    if args.verify_archive is not None:
        verify_archive(args.platform, args.verify_archive)
        return

    build(args.platform)


if __name__ == "__main__":
    main()
