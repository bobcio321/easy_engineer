const form = document.getElementById('loginForm');
const codeInput = document.getElementById('sessionCode');
const passInput = document.getElementById('password');
const errorMsg = document.getElementById('errorMsg');
const connectBtn = document.getElementById('connectBtn');

codeInput.addEventListener('input', () => {
  codeInput.value = codeInput.value.toUpperCase();
});

passInput.addEventListener('input', () => {
  passInput.value = passInput.value.toUpperCase();
});

form.addEventListener('submit', (e) => {
  e.preventDefault();

  const code = codeInput.value.trim();
  const password = passInput.value.trim();

  if (code.length < 1 || password.length < 1) {
    errorMsg.textContent = 'Please enter both session code and password';
    return;
  }

  errorMsg.textContent = '';
  connectBtn.disabled = true;
  connectBtn.textContent = 'Connecting...';

  const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
  const ws = new WebSocket(`${protocol}//${location.host}/ws/engineer`);

  ws.onopen = () => {
    ws.send(JSON.stringify({ type: 'engineer:join', code, password }));
  };

  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);

    if (msg.type === 'auth:ok') {
      sessionStorage.setItem('ee_code', code);
      sessionStorage.setItem('ee_password', password);
      ws.close();
      window.location.href = '/dashboard.html';
    } else if (msg.type === 'auth:fail') {
      errorMsg.textContent = msg.reason || 'Connection failed';
      connectBtn.disabled = false;
      connectBtn.textContent = 'Connect';
      ws.close();
    }
  };

  ws.onerror = () => {
    errorMsg.textContent = 'Unable to connect to server';
    connectBtn.disabled = false;
    connectBtn.textContent = 'Connect';
  };

  ws.onclose = () => {
    connectBtn.disabled = false;
    connectBtn.textContent = 'Connect';
  };
});
