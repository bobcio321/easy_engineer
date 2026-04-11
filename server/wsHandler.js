const { createSession, validateSession, getSession, destroySession } = require('./sessionManager');

function handleDriverConnection(ws) {
  const { code, password } = createSession();
  const session = getSession(code);
  session.driverWs = ws;

  ws._sessionCode = code;

  ws.send(JSON.stringify({ type: 'session:created', code, password }));

  ws.on('message', (raw) => {
    let msg;
    try {
      msg = JSON.parse(raw);
    } catch {
      return;
    }

    if (msg.type === 'telemetry') {
      session.telemetry = msg.data;
      const payload = JSON.stringify({ type: 'telemetry', data: msg.data });
      for (const eng of session.engineers) {
        if (eng.readyState === 1) eng.send(payload);
      }
    }

    if (msg.type === 'pit:update') {
      session.pitStrategy = msg.data;
      for (const eng of session.engineers) {
        if (eng.readyState === 1) eng.send(JSON.stringify({ type: 'pit:driver-update', data: msg.data }));
      }
    }
  });

  ws.on('close', () => {
    destroySession(code);
  });
}

function handleEngineerConnection(ws) {
  let joined = false;
  let sessionCode = null;

  ws.on('message', (raw) => {
    let msg;
    try {
      msg = JSON.parse(raw);
    } catch {
      return;
    }

    if (msg.type === 'engineer:join') {
      const { code, password } = msg;

      if (!validateSession(code, password)) {
        ws.send(JSON.stringify({ type: 'auth:fail', reason: 'Invalid session code or password' }));
        return;
      }

      const session = getSession(code);
      if (!session.driverWs) {
        ws.send(JSON.stringify({ type: 'auth:fail', reason: 'Driver is not connected' }));
        return;
      }

      session.engineers.add(ws);
      sessionCode = code;
      joined = true;

      ws.send(JSON.stringify({ type: 'auth:ok' }));

      if (session.telemetry) {
        ws.send(JSON.stringify({ type: 'telemetry', data: session.telemetry }));
      }

      ws.send(JSON.stringify({ type: 'pit:strategy', data: session.pitStrategy }));
      return;
    }

    if (msg.type === 'pit:update' && joined) {
      const session = getSession(sessionCode);
      if (!session) return;

      session.pitStrategy = msg.data;

      if (session.driverWs && session.driverWs.readyState === 1) {
        session.driverWs.send(JSON.stringify({ type: 'pit:update', data: msg.data }));
      }

      for (const eng of session.engineers) {
        if (eng !== ws) {
          eng.send(JSON.stringify({ type: 'pit:strategy', data: msg.data }));
        }
      }
    }
  });

  ws.on('close', () => {
    if (joined && sessionCode) {
      const session = getSession(sessionCode);
      if (session) {
        session.engineers.delete(ws);
      }
    }
  });
}

module.exports = { handleDriverConnection, handleEngineerConnection };
