#!/bin/sh
# 容器启动入口：同时启动 Flask API 与 MCP 服务端
# - Flask: gunicorn 多进程多线程 (127.0.0.1:5000，仅供 nginx 反向代理)
# - MCP:   uvicorn 多 worker，支持多人/多 Agent 并发调用 (0.0.0.0:8080)

set -u

echo "[entrypoint] starting nginx..."
nginx

cd /app/backend || exit 1

echo "[entrypoint] starting Flask API (gunicorn, 4 workers x 8 threads)..."
gunicorn --workers 4 --threads 8 --timeout 60 --keep-alive 5 \
  --access-logfile - --error-logfile - -b 127.0.0.1:5000 app:app &
GUNICORN_PID=$!

echo "[entrypoint] starting MCP server (uvicorn, 4 workers) on 0.0.0.0:8080..."
uvicorn mcp_server:create_app --factory --host 0.0.0.0 --port 8080 \
  --workers 4 --timeout-keep-alive 5 --log-level info &
UVICORN_PID=$!

echo "[entrypoint] gunicorn pid=$GUNICORN_PID, uvicorn pid=$UVICORN_PID"

# 任一服务退出则终止容器，交由 Docker restart=unless-stopped 自动拉起
while kill -0 "$GUNICORN_PID" 2>/dev/null && kill -0 "$UVICORN_PID" 2>/dev/null; do
  sleep 2
done

echo "[entrypoint] one of the services exited, shutting down container..."
kill "$GUNICORN_PID" "$UVICORN_PID" 2>/dev/null || true

exit 1