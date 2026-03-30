#!/bin/bash
# start.sh - Start CardFeed services
# Usage: ./start.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

echo "╔════════════════════════════════════════════════════════╗"
echo "║           CardFeed Startup                             ║"
echo "╚════════════════════════════════════════════════════════╝"

# Install dependencies if needed
if [ ! -d "$SKILL_DIR/app/node_modules" ]; then
  echo "📦 Installing app dependencies..."
  cd "$SKILL_DIR/app"
  npm install
fi

if [ ! -d "$SKILL_DIR/server/node_modules" ]; then
  echo "📦 Installing server dependencies..."
  cd "$SKILL_DIR/server"
  npm install
fi

# Start services
echo ""
echo "🚀 Starting services..."

# Start WebSocket server in background
cd "$SKILL_DIR/server"
node index.js &
SERVER_PID=$!

# Start Vite dev server
cd "$SKILL_DIR/app"
npm run dev -- --host &
APP_PID=$!

# Get local IP
LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || echo "localhost")

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  CardFeed is running!                                  ║"
echo "╠════════════════════════════════════════════════════════╣"
echo "║  Web App:    http://localhost:5173                     ║"
echo "║  Mobile:     http://${LOCAL_IP}:5173                   ║"
echo "║  WebSocket:  ws://localhost:8080                       ║"
echo "╠════════════════════════════════════════════════════════╣"
echo "║  Press Ctrl+C to stop                                  ║"
echo "╚════════════════════════════════════════════════════════╝"

# Cleanup on exit
cleanup() {
  echo ""
  echo "Stopping services..."
  kill $SERVER_PID 2>/dev/null
  kill $APP_PID 2>/dev/null
  exit 0
}
trap cleanup SIGINT SIGTERM

# Wait
wait
