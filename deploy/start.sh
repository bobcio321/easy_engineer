#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SERVER_DIR="${PROJECT_ROOT}/server"

if [ ! -d "${SERVER_DIR}" ]; then
  echo "[ERROR] Folder server not found: ${SERVER_DIR}"
  exit 1
fi

cd "${SERVER_DIR}"

echo "[INFO] Checking Node.js dependencies..."
if [ ! -d node_modules ]; then
  if [ -f package-lock.json ]; then
    npm ci --omit=dev
  else
    npm install --omit=dev
  fi
fi

echo "[INFO] Starting Easy Engineer server..."
npm start
