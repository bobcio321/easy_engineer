#!/bin/bash
cd "$(dirname "$0")/server"
if [ ! -d node_modules ]; then
    echo "Installing dependencies..."
    npm install --production
fi
echo "Starting Easy Engineer server..."
node server.js
