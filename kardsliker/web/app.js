const statusEl = document.getElementById("status");
const fileList = document.getElementById("files");
const filter = document.getElementById("filter");
const code = document.getElementById("code");
const currentFile = document.getElementById("current-file");
const runOutput = document.getElementById("run-output");
const output = document.getElementById("output");
const klCode = document.getElementById("kl-code");
const klOutput = document.getElementById("kl-output");
const cardCode = document.getElementById("card-code");
const forgeFrame = document.getElementById("forge-frame");

let files = [];
let selected = "";
let currentTab = "card";

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
  if (tab === "forge") {
    window.setTimeout(syncForge, 250);
  }
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
  switchTab("python");
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

const TYPE_INDEX = {
  infantry: 1, tank: 2, artillery: 3, fighter: 4, bomber: 5, order: 6, countermeasure: 7,
};
const FACTION_INDEX = {
  germany: 1, britain: 2, japan: 3, soviet: 4, usa: 5, france: 6,
  italy: 7, poland: 8, finland: 9, anzac: 10, neutral: 11,
};
const RARITY_INDEX = { standard: 1, limited: 2, special: 3, elite: 4, none: 5 };

function readCard() {
  return {
    id: document.getElementById("card-id").value.trim() || "card_new_unit",
    name: document.getElementById("card-name").value.trim() || "未命名卡牌",
    country: document.getElementById("card-country").value,
    type: document.getElementById("card-type").value,
    rarity: document.getElementById("card-rarity").value,
    cost: Number(document.getElementById("card-cost").value || 0),
    op: Number(document.getElementById("card-op").value || 0),
    operation_cost: Number(document.getElementById("card-op").value || 0),
    at: Number(document.getElementById("card-at").value || 0),
    df: Number(document.getElementById("card-df").value || 0),
    text: document.getElementById("card-text").value,
    art: document.getElementById("card-art").value.trim(),
  };
}

async function syncForge() {
  const win = forgeFrame.contentWindow;
  if (!win || !win.KardsDIY) {
    setStatus("卡面尚未加载");
    return;
  }
  const card = readCard();
  try {
    await win.KardsDIY.setCard({
      typeIndex: TYPE_INDEX[card.type] || 1,
      factionIndex: FACTION_INDEX[card.country] || 4,
      rarityIndex: RARITY_INDEX[card.rarity] || 1,
      setIndex: 0,
      title: card.name,
      cost: card.cost,
      operationCost: card.op,
      attack: card.at,
      defense: card.df,
      bodyHtml: card.text.replace(/\n/g, "<br>"),
      art: card.art || undefined,
    });
    setStatus("已同步到卡面");
  } catch (error) {
    setStatus(`同步失败: ${error}`);
  }
}

async function generateCode() {
  try {
    const data = await api("/api/card/generate", {
      method: "POST",
      body: JSON.stringify(readCard()),
    });
    cardCode.textContent = `# KL\n${data.kl}\n\n# Python\n${data.python}\n\n# target\n${data.target}`;
    setStatus("代码生成完成");
  } catch (error) {
    cardCode.textContent = String(error);
    setStatus("生成失败");
  }
}

async function saveCard(writePy) {
  try {
    const data = await api("/api/card/save", {
      method: "POST",
      body: JSON.stringify({ ...readCard(), write_py: writePy }),
    });
    cardCode.textContent =
      `project: ${data.project}\npython: ${data.python}\nwritten: ${data.written}`;
    setStatus(writePy ? "已写入 mod" : "卡牌已保存");
  } catch (error) {
    cardCode.textContent = String(error);
    setStatus("保存失败");
  }
}

document.getElementById("sync-forge").addEventListener("click", syncForge);
document.getElementById("generate-code").addEventListener("click", generateCode);
document.getElementById("save-card").addEventListener("click", () => saveCard(false));
document.getElementById("write-card").addEventListener("click", () => saveCard(true));

loadFiles().then(() => {
  output.textContent =
    "KardsLiker 0.2\n\n流程：填写卡牌 -> 同步卡面 -> 生成代码 -> 写入 mod";
}).catch((error) => {
  output.textContent = String(error);
});
