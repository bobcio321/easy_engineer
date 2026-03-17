const path = require('path');
const express = require('express');
const http = require('http');
const { WebSocketServer } = require('ws');
const { handleDriverConnection, handleEngineerConnection } = require('./wsHandler');

const app = express();
const server = http.createServer(app);

app.use(express.static(path.join(__dirname, '..', 'public')));

const driverWss = new WebSocketServer({ noServer: true });
const engineerWss = new WebSocketServer({ noServer: true });

server.on('upgrade', (request, socket, head) => {
  const { pathname } = new URL(request.url, `http://${request.headers.host}`);

  if (pathname === '/ws/driver') {
    driverWss.handleUpgrade(request, socket, head, (ws) => {
      driverWss.emit('connection', ws, request);
    });
  } else if (pathname === '/ws/engineer') {
    engineerWss.handleUpgrade(request, socket, head, (ws) => {
      engineerWss.emit('connection', ws, request);
    });
  } else {
    socket.destroy();
  }
});

driverWss.on('connection', handleDriverConnection);
engineerWss.on('connection', handleEngineerConnection);

const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || '0.0.0.0';
server.listen(PORT, HOST, () => {
  console.log(`Easy Engineer server running on http://${HOST}:${PORT}`);
});
