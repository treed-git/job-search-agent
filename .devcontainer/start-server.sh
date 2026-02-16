#!/bin/bash
# Start the app server in a fully detached background process.
# Codespaces sets the workspace to /workspaces/<repo>, but fall back
# to the directory containing this script's parent just in case.
echo "[start-server] $(date): script started" > /tmp/app.log

cd /workspaces/job-search-agent 2>/dev/null || cd "$(dirname "$0")/.." || true
echo "[start-server] cwd: $(pwd)" >> /tmp/app.log

nohup python -m app.main >> /tmp/app.log 2>&1 &
disown -h

echo "[start-server] launched PID $!" >> /tmp/app.log
