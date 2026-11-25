const statusEl = document.getElementById("status");
const fileList = document.getElementById("files");
const filter = document.getElementById("filter");
const klCode = document.getElementById("kl-code");
const cardCode = document.getElementById("card-code");
const fileView = document.getElementById("file-view");
const forgeFrame = document.getElementById("forge-frame");
const targetEl = document.getElementById("declaration-target");
const metaEl = document.getElementById("declaration-meta");
const resourceCount = document.getElementById("resource-count");

let files = [];
let selectedFile = "";
let selectedCard = null;

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

document.querySelectorAll(".zone-tabs button").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".zone-tabs button").forEach((item) => {
      item.classList.toggle("active", item === button);
    });
    document.querySelectorAll(".zone").forEach((zone) => {
      zone.classList.toggle("active", zone.id === `zone-${button.dataset.zone}`);
    });
  });
});

document.querySelectorAll(".workspace-tabs button").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".workspace-tabs button").forEach((item) => {
      item.classList.toggle("active", item === button);
    });
    document.querySelectorAll(".workspace-panel").forEach((panel) => {
      panel.classList.toggle("active", panel.id === `workspace-${button.dataset.workspace}`);
    });
  });
});

function renderFiles() {
  const needle = filter.value.trim().toLowerCase();
  fileList.innerHTML = "";
  for (const path of files) {
    if (needle && !path.toLowerCase().includes(needle)) continue;
    const button = document.createElement("button");
    button.textContent = path;
    button.title = path;
    button.classList.toggle("active", path === selectedFile);
    button.addEventListener("click", () => openFile(path));
    fileList.appendChild(button);
  }
  resourceCount.textContent = `${files.length} 个文件`;
}

async function loadFiles() {
  const data = await api("/api/files");
  files = data.files || [];
  renderFiles();
}

async function openFile(path) {
  selectedFile = path;
  renderFiles();
  try {
    const data = await api(`/api/file?path=${encodeURIComponent(path)}`);
    fileView.textContent = data.content;
    setStatus(`已打开资源 ${path}`);
  } catch (error) {
    fileView.textContent = String(error);
    setStatus("资源读取失败");
  }
}

const TYPE_INDEX = {
  infantry: 1, tank: 2, artillery: 3, fighter: 4, bomber: 5, order: 6, countermeasure: 7,
};
const FACTION_INDEX = {
  germany: 1, britain: 2, japan: 3, soviet: 4, usa: 5, france: 6,
  italy: 7, poland: 8, finland: 9, anzac: 10, neutral: 11,
};
const RARITY_INDEX = { standard: 1, limited: 2, special: 3, elite: 4, none: 5 };

function cardFromAst(card) {
  const fields = card.fields || {};
  const rawId = String(fields.id || "").trim();
  const fallback = String(card.name || "custom")
    .toLowerCase()
    .replace(/\s+/g, "_")
    .replace(/[^a-z0-9_-]/g, "");
  const id = rawId || `card_${fallback || "custom"}`;
  return {
    id,
    name: card.name || "未命名卡牌",
    country: fields.country || "soviet",
    type: fields.type || "infantry",
    rarity: fields.rarity || "standard",
    cost: Number(fields.cost ?? 0),
    op: Number(fields.operation_cost ?? fields.op ?? 0),
    operation_cost: Number(fields.operation_cost ?? fields.op ?? 0),
    at: Number(fields.at ?? 0),
    df: Number(fields.df ?? 0),
    text: fields.text || "",
    art: fields.art || "",
    keywords: fields.keywords || [],
    procedures: card.procedures || "",
    imports: card.imports || [],
    dependencies: card.dependencies || [],
  };
}

function updateMeta(card) {
  metaEl.innerHTML = "";
  for (const [label, value] of [
    ["名称", card.name],
    ["ID", card.id],
    ["国家 / 类型", `${card.country} / ${card.type}`],
  ]) {
    const row = document.createElement("div");
    const key = document.createElement("b");
    key.textContent = label;
    const text = document.createElement("span");
    text.textContent = value;
    row.append(key, text);
    metaEl.append(row);
  }
}

async function parseCard() {
  const data = await api("/api/kl", {
    method: "POST",
    body: JSON.stringify({ source: klCode.value }),
  });
  if (!data.ast || data.ast.length === 0) {
    throw new Error("KL 中没有 card 声明");
  }
  const card = cardFromAst(data.ast[0]);
  selectedCard = card;
  updateMeta(card);
  const generated = await api("/api/card/generate", {
    method: "POST",
    body: JSON.stringify(card),
  });
  cardCode.textContent = generated.python;
  targetEl.textContent = generated.target;
  setStatus("KL 解析完成");
  return card;
}

async function syncForge() {
  try {
    const card = selectedCard || await parseCard();
    const win = forgeFrame.contentWindow;
    if (!win || !win.KardsDIY) {
      setStatus("卡面尚未加载");
      return;
    }
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
      bodyHtml: String(card.text).replace(/\n/g, "<br>"),
      art: card.art || undefined,
    });
    setStatus("已同步到卡面");
  } catch (error) {
    setStatus(`同步失败: ${error}`);
  }
}


async function pullFromForge() {
  try {
    const doc = forgeFrame.contentDocument;
    if (!doc) {
      setStatus("卡面尚未加载");
      return;
    }
    const textOf = (id) => (doc.getElementById(id)?.innerText || "").trim();
    const number = (id) => Number.parseInt(textOf(id), 10) || 0;
    const card = {
      ...(selectedCard || {
        id: "card_custom",
        country: "soviet",
        type: "infantry",
        rarity: "standard",
        keywords: [],
        procedures: "",
        imports: [],
        dependencies: [],
      }),
      name: textOf("title") || "未命名卡牌",
      cost: number("kredit"),
      op: number("opredit"),
      operation_cost: number("opredit"),
      at: number("attack"),
      df: number("defense"),
      text: textOf("b-text"),
    };
    selectedCard = card;
    updateMeta(card);
    let source = klCode.value;
    const setField = (pattern, value) => {
      source = source.replace(pattern, `$1${value}`);
    };
    setField(/^(\s*NAME\s*:\s*).*$/im, JSON.stringify(card.name));
    setField(/^(\s*(?:CT|COST)\s*:\s*).*$/im, String(card.cost));
    setField(/^(\s*(?:OC|OPERATION_COST|OP)\s*:\s*).*$/im, String(card.op));
    setField(/^(\s*AT\s*:\s*).*$/im, String(card.at));
    setField(/^(\s*DF\s*:\s*).*$/im, String(card.df));
    if (/DESCRIPTION\s*:\s*"""/i.test(source)) {
      source = source.replace(/DESCRIPTION\s*:\s*"""[\s\S]*?"""/i, `DESCRIPTION: ${JSON.stringify(card.text)}`);
    } else {
      setField(/^(\s*DESCRIPTION\s*:\s*).*$/im, JSON.stringify(card.text));
    }
    klCode.value = source;
    setStatus("已从卡面读取");
  } catch (error) {
    setStatus(`读取失败: ${error}`);
  }
}

async function saveCard(writePy) {
  try {
    const card = selectedCard || await parseCard();
    const data = await api("/api/card/save", {
      method: "POST",
      body: JSON.stringify({ ...card, write_py: writePy }),
    });
    cardCode.textContent =
      `project: ${data.project}\npython: ${data.python}\nwritten: ${data.written}`;
    targetEl.textContent = data.python;
    setStatus(writePy ? "已写入 mod" : "声明已保存");
  } catch (error) {
    setStatus(`保存失败: ${error}`);
  }
}

document.getElementById("parse-card").addEventListener("click", () => {
  parseCard().catch((error) => setStatus(`解析失败: ${error}`));
});
document.getElementById("sync-card").addEventListener("click", syncForge);
document.getElementById("pull-card").addEventListener("click", pullFromForge);
document.getElementById("save-card").addEventListener("click", () => saveCard(false));
document.getElementById("write-card").addEventListener("click", () => saveCard(true));
filter.addEventListener("input", renderFiles);

loadFiles()
  .then(() => setStatus("就绪"))
  .catch((error) => setStatus(String(error)));
