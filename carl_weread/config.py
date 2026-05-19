from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


VALID_MODES = {"obsidian", "folder", "chat", "weread-only"}
PATH_REQUIRED_MODES = {"obsidian", "folder"}


@dataclass(frozen=True)
class ContextConfig:
    mode: str
    path: Path | None = None

    def validate(self) -> None:
        if self.mode not in VALID_MODES:
            raise ValueError(f"unsupported mode: {self.mode}")
        if self.mode in PATH_REQUIRED_MODES and self.path is None:
            raise ValueError(f"path is required for {self.mode} mode")


def _escape_toml_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def write_config(config: ContextConfig, output_path: str | Path) -> None:
    config.validate()
    output = Path(output_path).expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)

    lines = ["[context]", f'mode = "{_escape_toml_string(config.mode)}"']
    if config.path is not None:
        lines.append(f'path = "{_escape_toml_string(str(Path(config.path).expanduser()))}"')
    lines.append("")
    output.write_text("\n".join(lines), encoding="utf-8")


def _parse_simple_toml_context(text: str) -> dict[str, str]:
    in_context = False
    values: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            in_context = line == "[context]"
            continue
        if not in_context or "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        value = raw_value.strip()
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        values[key.strip()] = value
    return values


def load_config(config_path: str | Path) -> ContextConfig:
    path = Path(config_path).expanduser()
    values = _parse_simple_toml_context(path.read_text(encoding="utf-8"))
    mode = values.get("mode")
    if mode is None:
        raise ValueError("config missing context.mode")
    context_path = Path(values["path"]).expanduser() if values.get("path") else None
    config = ContextConfig(mode=mode, path=context_path)
    config.validate()
    return config
