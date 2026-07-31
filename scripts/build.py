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
  - src/.claude-plugin/  -> claude ビルドの .claude-plugin/ 配下
  - src/.copilot-plugin/ -> copilot ビルドのパッケージルート直下
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from typing import Iterator

from jinja2 import Environment, FileSystemLoader, StrictUndefined

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
DIST_DIR = PROJECT_ROOT / "dist"

# .github/workflows/package-plugin.yml の matrix.platform と揃える
SUPPORTED_PLATFORMS = ("chatgpt", "claude", "copilot")

# Jinja2 でレンダリングする拡張子。それ以外はそのままコピーする
TEMPLATE_SUFFIXES = {".md"}

# バンドルに含めないファイル / ディレクトリ名
EXCLUDED_NAMES = {".DS_Store", "Thumbs.db", "__pycache__", ".pytest_cache"}

# 特定プラットフォーム専用の src 配下ディレクトリ（キーは src 直下のディレクトリ名）。
# 対象プラットフォーム以外のビルドからは除外し、`dest` の位置に再配置する。
#   - .claude-plugin: Claude Code はマニフェストを .claude-plugin/ 配下に置く仕様のため
#                     ディレクトリ名を保ったまま同梱する。
#   - .copilot-plugin: Copilot (Teams アプリ) のマニフェストは
#                      アイコンや agentSkills をパッケージルート基準の相対パスで参照するため、
#                      中身をパッケージルート直下に展開する（dest = ""）。
PLATFORM_DIRS = {
    ".claude-plugin": {"platform": "claude", "dest": ".claude-plugin"},
    ".copilot-plugin": {"platform": "copilot", "dest": ""},
}

# プラットフォームごとにバンドルから除外するファイル（src からの相対パス）。
# copilot は manifest.json の agentConnectors で MCP サーバーを宣言するため、
# .mcp.json は二重定義になり不要。
PLATFORM_EXCLUDED_FILES = {
    "copilot": {".mcp.json"},
}

# 各プラットフォームのバンドルに必須のファイル（バンドル内の相対パス）
REQUIRED_FILES = {
    "claude": (".claude-plugin/plugin.json",),
    # manifest.json が icons で参照するため PNG も必須
    "copilot": ("manifest.json", "color.png", "outline.png"),
}


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

        if src_path.suffix.lower() in TEMPLATE_SUFFIXES:
            # テンプレートの読み込みは src からの相対パスで行う
            template = env.get_template(source_rel.as_posix())
            dest_path.write_text(
                template.render(platform=platform), encoding="utf-8"
            )
            rendered_count += 1
        else:
            shutil.copy2(src_path, dest_path)
            copied_count += 1

        if source_rel == relative_dest:
            print(f"  {relative_dest.as_posix()}")
        else:
            print(f"  {source_rel.as_posix()} -> {relative_dest.as_posix()}")

    # 必須ファイルの取りこぼしを検知する（例: claude のプラグインマニフェスト）
    for required in REQUIRED_FILES.get(platform, ()):
        if not (out_dir / required).is_file():
            raise SystemExit(
                f"[{platform}] 必須ファイルがバンドルに含まれていません: {required}\n"
                f"  src/ 配下に対応するファイルがあるか、"
                f"PLATFORM_DIRS の再配置設定を確認してください。"
            )

    print(
        f"[{platform}] レンダリング {rendered_count} 件 / コピー {copied_count} 件"
        f" -> {out_dir.relative_to(PROJECT_ROOT)}"
    )
    return out_dir


def main() -> None:
    parser = argparse.ArgumentParser(
        description="src/ からプラットフォーム別のスキルバンドルを生成する"
    )
    parser.add_argument(
        "platform",
        choices=SUPPORTED_PLATFORMS,
        help="ビルド対象のプラットフォーム",
    )
    args = parser.parse_args()
    build(args.platform)


if __name__ == "__main__":
    main()
