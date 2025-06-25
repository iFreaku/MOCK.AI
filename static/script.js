let messages = []; // Assuming you have this for session messages

const editor = CodeMirror.fromTextArea(document.getElementById("code"), {
  mode: "application/json",
  theme: "default",
  lineNumbers: true,
  autoCloseBrackets: true,
  value: "chinese only menu" // Your default input
});

async function fetchData() {
  const generateButton = document.querySelector('.editor-header button'); // Adjust selector if needed
  const loadingBar = document.getElementById('loading-bar');
  const outputElement = document.getElementById("output");

  // Disable button and show loading bar
  generateButton.disabled = true;
  loadingBar.style.display = 'flex';

  try {
    const input = editor.getValue();
    const res = await fetch('/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-MockType': 'json'
      },
      body: JSON.stringify({
        prompt: input,
        messages: messages
      })
    });
    const data = await res.json();

    // Update messages (assuming this is part of your logic)
    if (data && Object.keys(data).length > 0 && !data.error) {
      messages.push({ role: "assistant", content: JSON.stringify(data) });
    }
    messages.push({ role: "user", content: input });

    // Display output with syntax highlighting
    const jsonOutput = JSON.stringify(data, null, 2);
    outputElement.innerHTML = hljs.highlight(jsonOutput, { language: 'json' }).value;
  } catch (e) {
    const errorOutput = JSON.stringify({ error: e.message }, null, 2);
    outputElement.innerHTML = hljs.highlight(errorOutput, { language: 'json' }).value;
  } finally {
    // Re-enable button and hide loading bar
    generateButton.disabled = false;
    loadingBar.style.display = 'none';
  }
}

function copyOutput() {
  const outputElement = document.getElementById("output");
  const text = outputElement.textContent;
  navigator.clipboard.writeText(text).then(() => {
    alert("Output copied to clipboard!");
  }).catch(err => {
    alert("Failed to copy: " + err);
  });
}