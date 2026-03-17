const crypto = require('crypto');

const sessions = new Map();

const SAFE_CHARS = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789';

function generateCode(length) {
  let code = '';
  for (let i = 0; i < length; i++) {
    code += SAFE_CHARS[crypto.randomInt(SAFE_CHARS.length)];
  }
  return code;
}

function createSession() {
  const code = generateCode(6);
  const password = generateCode(4);

  sessions.set(code, {
    password,
    driverWs: null,
    engineers: new Set(),
    telemetry: null,
    pitStrategy: {
      fuel: 0,
      tireCompound: 'Medium',
      changeTires: false,
      repairBody: false,
      repairEngine: false,
    },
  });

  return { code, password };
}

function validateSession(code, password) {
  const session = sessions.get(code);
  if (!session) return false;
  return session.password === password;
}

function getSession(code) {
  return sessions.get(code);
}

function destroySession(code) {
  const session = sessions.get(code);
  if (!session) return;

  for (const ws of session.engineers) {
    if (ws.readyState === 1) ws.send(JSON.stringify({ type: 'session:ended' }));
  }

  sessions.delete(code);
}

module.exports = { createSession, validateSession, getSession, destroySession };
