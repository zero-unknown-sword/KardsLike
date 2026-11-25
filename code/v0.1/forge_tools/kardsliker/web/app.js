const statusEl = document.getElementById("status");
const fileList = document.getElementById("files");
const filter = document.getElementById("filter");
const code = document.getElementById("code");
const currentFile = document.getElementById("current-file");
const runOutput = document.getElementById("run-output");
const output = document.getElementById("output");
const klCode = document.getElementById("kl-code");
const klOutput = document.getElementById("kl-output");

let files = [];
let selected = "";
let currentTab = "project";

function setStatus(text) {
  statusEl.textContent = text;
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await response.json();
  if (!response.ok || data.ok === false) {
    throw new Error(data.error || `HTTP ${response.status}`);
  }
  return data;
}

function switchTab(tab) {
  currentTab = tab;
  document.querySelectorAll(".tabs button").forEach((button) => {
    button.classList.toggle("active", button.dataset.tab === tab);
  });
  document.querySelectorAll(".panel").forEach((panel) => {
    panel.classList.toggle("active", panel.id === `panel-${tab}`);
  });
}

document.querySelectorAll(".tabs button").forEach((button) => {
  button.addEventListener("click", () => switchTab(button.dataset.tab));
});

function renderFiles() {
  const needle = filter.value.trim().toLowerCase();
  fileList.innerHTML = "";
  for (const path of files) {
    if (needle && !path.toLowerCase().includes(needle)) continue;
    const button = document.createElement("button");
    button.textContent = path;
    button.title = path;
    button.classList.toggle("active", path === selected);
    button.addEventListener("click", () => openFile(path));
    fileList.appendChild(button);
  }
}

async function loadFiles() {
  const data = await api("/api/files");
  files = data.files || [];
  renderFiles();
}

async function openFile(path) {
  selected = path;
  renderFiles();
  currentFile.textContent = path;
  const data = await api(`/api/file?path=${encodeURIComponent(path)}`);
  code.value = data.content;
  if (!path.endsWith(".py") && !path.endsWith(".json") && !path.endsWith(".kl")) {
    switchTab("project");
  } else {
    switchTab("python");
  }
  setStatus(`已打开 ${path}`);
}

document.getElementById("save").addEventListener("click", async () => {
  if (!selected) return;
  try {
    await api("/api/file", {
      method: "POST",
      body: JSON.stringify({ path: selected, content: code.value }),
    });
    setStatus(`已保存 ${selected}`);
  } catch (error) {
    setStatus(String(error));
  }
});

document.getElementById("run").addEventListener("click", async () => {
  if (!selected) {
    runOutput.textContent = "请先选择一个 .py 文件";
    return;
  }
  try {
    setStatus("运行中...");
    const data = await api("/api/run", {
      method: "POST",
      body: JSON.stringify({ path: selected }),
    });
    runOutput.textContent =
      `returncode: ${data.returncode}\n\n[stdout]\n${data.stdout}\n[stderr]\n${data.stderr}`;
    setStatus(data.returncode === 0 ? "运行完成" : "运行失败");
  } catch (error) {
    runOutput.textContent = String(error);
    setStatus("运行失败");
  }
});

document.getElementById("parse-kl").addEventListener("click", async () => {
  try {
    const data = await api("/api/kl", {
      method: "POST",
      body: JSON.stringify({ source: klCode.value }),
    });
    klOutput.textContent = JSON.stringify(data.ast, null, 2);
    setStatus("KL 解析成功");
  } catch (error) {
    klOutput.textContent = String(error);
    setStatus("KL 解析失败");
  }
});

filter.addEventListener("input", renderFiles);

loadFiles().then(() => {
  output.textContent =
    "KardsLiker 0.1\n\n左侧选择文件开始编辑。\n卡面页使用原版 KARDS DIY 页面。";
}).catch((error) => {
  output.textContent = String(error);
});
