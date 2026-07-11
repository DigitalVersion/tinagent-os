#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PORT=${TIN_SMOKE_PORT:-18080}
NAME="tin-smoke-$$"
LOG=/tmp/tin-os-smoke.log

cleanup() {
  kill "${SERVER_PID:-}" 2>/dev/null || true
  tmux kill-session -t "$NAME" 2>/dev/null || true
}
trap cleanup EXIT

command -v python3 >/dev/null
command -v tmux >/dev/null
node --check "$ROOT/tin_os/web/app.js" >/dev/null
python3 -m py_compile "$ROOT/tin_os/server.py"

TIN_WORKSPACE=/tmp TIN_PORT="$PORT" python3 -m tin_os.server --host 127.0.0.1 --port "$PORT" >"$LOG" 2>&1 &
SERVER_PID=$!
cd "$ROOT"
for _ in $(seq 1 30); do curl -fsS "http://127.0.0.1:$PORT/api/status" >/dev/null 2>&1 && break; sleep .2; done
curl -fsS "http://127.0.0.1:$PORT/" | grep -q 'Start OpenCode Web'
curl -fsS "http://127.0.0.1:$PORT/api/status" | python3 -m json.tool >/dev/null
curl -fsS -X POST -H 'Content-Type: application/json' -d "{\"name\":\"$NAME\",\"agent\":\"bash\"}" "http://127.0.0.1:$PORT/api/sessions" | grep -q "$NAME"
curl -fsS "http://127.0.0.1:$PORT/api/sessions" | grep -q "$NAME"
curl -fsS -X DELETE "http://127.0.0.1:$PORT/api/sessions/$NAME" | grep -q 'deleted'
! tmux has-session -t "$NAME" 2>/dev/null

echo "PASS: Tin OS cold-start runtime, static UI, status API, tmux create/list/delete"
