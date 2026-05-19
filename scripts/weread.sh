#!/usr/bin/env bash
# carl-weread API helper. Keep this layer boring: one subcommand maps to one WeRead API.
set -euo pipefail

GATEWAY="https://i.weread.qq.com/api/agent/gateway"
SKILL_VERSION="${WEREAD_SKILL_VERSION:-1.0.3}"

usage() {
  cat <<'EOF'
Usage: scripts/weread.sh <subcommand> [--key=value ...]

Subcommands:
  search --keyword=STR
  shelf
  notebooks [--count=INT] [--lastSort=INT]
  bookmarks --bookId=STR
  chapters --bookId=STR
  progress --bookId=STR
  readdata [--mode=overall]
  book-info --bookId=STR
  recommend
  similar --bookId=STR
  list-apis

Auth: export WEREAD_API_KEY=wrk-...
EOF
}

api_path() {
  case "$1" in
    search) echo "/store/search" ;;
    shelf) echo "/shelf/sync" ;;
    notebooks) echo "/user/notebooks" ;;
    bookmarks) echo "/book/bookmarklist" ;;
    chapters) echo "/book/chapterinfo" ;;
    progress) echo "/book/getprogress" ;;
    readdata) echo "/readdata/detail" ;;
    book-info) echo "/book/info" ;;
    recommend) echo "/book/recommend" ;;
    similar) echo "/book/similar" ;;
    list-apis) echo "/_list" ;;
    *) return 1 ;;
  esac
}

json_quote() {
  python3 -c 'import json,sys; print(json.dumps(sys.argv[1], ensure_ascii=False))' "$1"
}

build_params_json() {
  python3 - "$@" <<'PY'
import json, sys
params = {}
for arg in sys.argv[1:]:
    if not arg.startswith('--') or '=' not in arg:
        raise SystemExit(f"参数格式错误：{arg}，应为 --key=value")
    key, value = arg[2:].split('=', 1)
    if value.isdigit():
        params[key] = int(value)
    else:
        params[key] = value
print(json.dumps(params, ensure_ascii=False))
PY
}

if [[ $# -lt 1 || "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

subcmd="$1"
shift
path="$(api_path "$subcmd")" || { echo "未知子命令：$subcmd" >&2; usage >&2; exit 2; }

if [[ -z "${WEREAD_API_KEY:-}" ]]; then
  echo "缺少 WEREAD_API_KEY。请先 export WEREAD_API_KEY=wrk-..." >&2
  exit 3
fi

params="$(build_params_json "$@")"

python3 - "$GATEWAY" "$path" "$SKILL_VERSION" "$params" <<'PY'
import json, os, sys, urllib.error, urllib.request

gateway, path, skill_version, params_raw = sys.argv[1:]
api_key = os.environ["WEREAD_API_KEY"]
params = json.loads(params_raw)
payload = {
    "api_name": path,
    "skill_version": skill_version,
    "params": params,
}
# Some WeRead gateway endpoints read arguments from the top-level payload rather
# than the nested params object. Keep params for compatibility, and flatten the
# same values so endpoints like /book/chapterinfo can see bookId.
payload.update(params)
req = urllib.request.Request(
    gateway,
    data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "carl-weread/1.0",
    },
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=60) as resp:
        print(resp.read().decode('utf-8'))
except urllib.error.HTTPError as exc:
    body = exc.read().decode('utf-8', 'replace')
    print(f"WeRead API error {exc.code}: {body}", file=sys.stderr)
    raise SystemExit(1)
PY
