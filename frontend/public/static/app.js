const messages = document.querySelector('#messages');
const form = document.querySelector('#chat-form');
const input = document.querySelector('#message-input');
const sendButton = document.querySelector('#send-button');
const chatPanel = document.querySelector('#chat-panel');
const chatFab = document.querySelector('#chat-fab');
const closeChat = document.querySelector('#close-chat');
const menuButton = document.querySelector('#menu-button');
const siteNav = document.querySelector('#site-nav');
const recentUserQuestions = [];

function setChat(open) {
  chatPanel.classList.toggle('open', open);
  chatPanel.setAttribute('aria-hidden', String(!open));
  chatFab.setAttribute('aria-expanded', String(open));
  if (open) setTimeout(() => input.focus(), 100);
}

function addMessage(text, role, urgent = false) {
  const article = document.createElement('article');
  article.className = `message ${role}${urgent ? ' urgent' : ''}`;
  const label = document.createElement('span');
  label.className = 'message-label';
  label.textContent = role === 'user' ? 'YOU' : 'STRIDE ASSISTANT';
  const body = document.createElement('p');
  body.textContent = text;
  article.append(label, body);
  messages.append(article);
  messages.scrollTop = messages.scrollHeight;
}

async function sendMessage(message) {
  setChat(true);
  const context = recentUserQuestions.slice(-2);
  addMessage(message, 'user');
  recentUserQuestions.push(message);
  input.value = '';
  sendButton.disabled = true;
  const typing = document.createElement('p');
  typing.className = 'typing';
  typing.textContent = 'Stride Assistant is thinking…';
  messages.append(typing);
  messages.scrollTop = messages.scrollHeight;
  try {
    const response = await fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message, context }) });
    if (!response.ok) throw new Error('Chat request failed');
    const data = await response.json();
    console.info(`Stride writer status: ${data.writer_status}`);
    addMessage(data.final_response, 'assistant', data.urgent === true);
  } catch {
    addMessage('I am unable to respond right now. For urgent symptoms, please seek medical care immediately.', 'assistant', true);
  } finally {
    typing.remove();
    sendButton.disabled = false;
    input.focus();
  }
}

chatFab.addEventListener('click', () => setChat(!chatPanel.classList.contains('open')));
closeChat.addEventListener('click', () => setChat(false));
document.querySelectorAll('.open-chat').forEach((element) => element.addEventListener('click', (event) => { event.preventDefault(); setChat(true); }));
form.addEventListener('submit', (event) => { event.preventDefault(); const message = input.value.trim(); if (message) sendMessage(message); });
document.querySelectorAll('[data-prompt]').forEach((button) => button.addEventListener('click', () => sendMessage(button.dataset.prompt)));
menuButton.addEventListener('click', () => { const isOpen = siteNav.classList.toggle('open'); menuButton.setAttribute('aria-expanded', String(isOpen)); });
siteNav.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => siteNav.classList.remove('open')));
document.addEventListener('keydown', (event) => { if (event.key === 'Escape') setChat(false); });
