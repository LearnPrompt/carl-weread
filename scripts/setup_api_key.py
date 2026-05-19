#!/usr/bin/env python3
from __future__ import annotations

import argparse
import getpass
import os
from pathlib import Path
import stat
import sys


def default_key_path() -> Path:
    return Path.home() / ".config" / "carl-weread" / "api_key"


def _read_key_from_stdin() -> str:
    return sys.stdin.readline().strip()


def _read_key_interactively() -> str:
    return getpass.getpass("Paste WEREAD_API_KEY: ").strip()


def _write_private_key(path: Path, api_key: str) -> None:
    output = path.expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.parent.chmod(0o700)

    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(api_key)
            handle.write("\n")
    finally:
        output.chmod(0o600)


def main() -> int:
    parser = argparse.ArgumentParser(description="Store WeRead API key for carl-weread.")
    parser.add_argument("--output", type=Path, default=default_key_path(), help="private API key file path")
    parser.add_argument("--stdin", action="store_true", help="read API key from stdin instead of secure prompt")
    args = parser.parse_args()

    api_key = _read_key_from_stdin() if args.stdin else _read_key_interactively()
    if not api_key:
        print("未写入：API Key 为空。", file=sys.stderr)
        return 2
    if not api_key.startswith("wrk-"):
        print("未写入：WEREAD_API_KEY 应以 wrk- 开头。", file=sys.stderr)
        return 2

    _write_private_key(args.output, api_key)
    mode = stat.S_IMODE(args.output.expanduser().stat().st_mode)
    if mode != 0o600:
        print("写入失败：API Key 文件权限不是 600。", file=sys.stderr)
        return 3

    print(f"已写入私有 API Key 文件：{args.output.expanduser()}")
    print("提示：不会写入 config.toml，也不会打印 API Key。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
