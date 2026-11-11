const form = document.getElementById('genForm');
const promptInput = document.getElementById('prompt');
const genBtn = document.getElementById('genBtn');
const placeholder = document.getElementById('placeholder');
const loader = document.getElementById('loader');
const result = document.getElementById('result');
const outImg = document.getElementById('outImg');
const outCaption = document.getElementById('outCaption');
const downloadBtn = document.getElementById('downloadBtn');

// Click a suggestion to fill the prompt
document.getElementById('suggestions').addEventListener('click', (e) => {
  if (e.target.tagName === 'SPAN') { promptInput.value = e.target.textContent; promptInput.focus(); }
});

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const prompt = promptInput.value.trim();
  if (!prompt) return;

  placeholder.hidden = true;
  result.hidden = true;
  loader.hidden = false;
  genBtn.disabled = true;

  try {
    const res = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Generation failed');
    outImg.src = data.image;
    outCaption.textContent = '“' + data.prompt + '”';
    downloadBtn.href = data.image;
    loader.hidden = true;
    result.hidden = false;
  } catch (err) {
    loader.hidden = true;
    placeholder.hidden = false;
    placeholder.textContent = 'Error: ' + err.message;
  } finally {
    genBtn.disabled = false;
  }
});
