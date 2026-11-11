const form = document.getElementById('chatForm');
const input = document.getElementById('input');
const messages = document.getElementById('messages');
const themeToggle = document.getElementById('themeToggle');

// ----- Theme (persisted) -----
if (localStorage.getItem('chat_theme') === 'dark') {
  document.body.setAttribute('data-theme', 'dark');
  themeToggle.textContent = '☀️';
}
themeToggle.addEventListener('click', () => {
  const dark = document.body.getAttribute('data-theme') === 'dark';
  if (dark) { document.body.removeAttribute('data-theme'); themeToggle.textContent = '🌙'; localStorage.setItem('chat_theme', 'light'); }
  else { document.body.setAttribute('data-theme', 'dark'); themeToggle.textContent = '☀️'; localStorage.setItem('chat_theme', 'dark'); }
});

// ----- Messaging -----
function addMessage(text, who) {
  const msg = document.createElement('div');
  msg.className = `msg msg--${who}`;
  msg.innerHTML = `<div class="avatar">${who === 'bot' ? '🤖' : '🧑'}</div><div class="bubble"></div>`;
  msg.querySelector('.bubble').textContent = text;
  messages.appendChild(msg);
  messages.scrollTop = messages.scrollHeight;
  return msg;
}

function showTyping() {
  const t = document.createElement('div');
  t.className = 'msg msg--bot typing';
  t.innerHTML = `<div class="avatar">🤖</div><div class="bubble"><span></span><span></span><span></span></div>`;
  messages.appendChild(t);
  messages.scrollTop = messages.scrollHeight;
  return t;
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  addMessage(text, 'user');
  input.value = '';

  const typing = showTyping();
  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text }),
    });
    const data = await res.json();
    // small delay so the typing animation is visible
    setTimeout(() => { typing.remove(); addMessage(data.reply || '…', 'bot'); }, 500);
  } catch (err) {
    typing.remove();
    addMessage('Sorry, something went wrong reaching the server.', 'bot');
  }
});
