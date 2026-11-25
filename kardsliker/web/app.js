const statusEl = document.getElementById("status");
const fileList = document.getElementById("files");
const filter = document.getElementById("filter");
const klCode = document.getElementById("kl-code");
const klHighlight = document.getElementById("kl-highlight");
const klStatus = document.getElementById("kl-status");
const klSuggest = document.getElementById("kl-suggest");
const klDiagnostics = document.getElementById("kl-diagnostics");
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


function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function highlightKl(source) {
  const sectionPattern = /^(\s*)(IMPORT|IMPORTS|DEPEND|DEPENDS|DEPENDENCY|DEPENDENCIES|REQUIRE|REQUIRES|SET_UNIT|SET_PROCEDURES)(\s*:?\s*)$/;
  const keyPattern = /^(\s*)([A-Za-z_][A-Za-z0-9_\/]*)(\s*:)(\s*)(.*)$/;
  const enumKeys = new Set(["TYPE", "COUNTRY", "RARE", "RARITY", "FACTION"]);
  return source.split("\n").map((line) => {
    const section = line.match(sectionPattern);
    if (section) {
      return `${section[1]}<span class="kl-section">${section[2]}</span>${section[3]}`;
    }
    const key = line.match(keyPattern);
    if (key) {
      const keyName = key[2].toUpperCase();
      const value = key[5];
      let valueHtml = escapeHtml(value);
      if (enumKeys.has(keyName)) {
        valueHtml = `<span class="kl-enum">${escapeHtml(value)}</span>`;
      } else if (/^".*"$/.test(value)) {
        valueHtml = `<span class="kl-string">${escapeHtml(value)}</span>`;
      } else if (/^-?\d+$/.test(value.trim())) {
        valueHtml = `<span class="kl-number">${escapeHtml(value)}</span>`;
      }
      return `${key[1]}<span class="kl-key">${key[2]}</span>${key[3]}${key[4]}${valueHtml}`;
    }
    if (/^\s*#/.test(line)) {
      return `<span class="kl-comment">${escapeHtml(line)}</span>`;
    }
    return escapeHtml(line);
  }).join("\n");
}

function updateHighlight() {
  klHighlight.innerHTML = highlightKl(klCode.value);
  klHighlight.scrollTop = klCode.scrollTop;
  klHighlight.scrollLeft = klCode.scrollLeft;
}


function setDiagnostics(error, warnings = []) {
  klDiagnostics.className = "kl-diagnostics";
  if (error) {
    klDiagnostics.classList.add("error");
    klDiagnostics.textContent = `错误：${error}`;
    return;
  }
  if (warnings.length) {
    klDiagnostics.classList.add("warn");
    klDiagnostics.textContent = `警告：${warnings.join("；")}`;
    return;
  }
  klDiagnostics.classList.add("ok");
  klDiagnostics.textContent = "语法与类型检查通过";
}

function setKlStatus(text, kind = "") {
  klStatus.textContent = text;
  klStatus.className = `kl-status ${kind}`.trim();
}

let klCheckTimer = 0;
function scheduleKlCheck() {
  window.clearTimeout(klCheckTimer);
  klCheckTimer = window.setTimeout(async () => {
    try {
      const response = await fetch("/api/kl", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source: klCode.value }),
      });
      const data = await response.json();
      if (response.ok && data.ok) {
        setKlStatus("语法通过", "ok");
        setDiagnostics("", data.warnings || []);
      } else {
        setKlStatus("语法错误", "error");
        setDiagnostics(data.error || "语法错误");
      }
    } catch (error) {
      setKlStatus("无法连接解析器", "error");
      setDiagnostics("无法连接解析器");
    }
  }, 450);
}

function insertText(text) {
  const start = klCode.selectionStart;
  const end = klCode.selectionEnd;
  klCode.setRangeText(text, start, end, "end");
  updateHighlight();
  scheduleKlCheck();
}

function handleKlKeydown(event) {
  if (event.key === "Escape") {
    hideSuggestions();
    return;
  }
  if (!klSuggest.hidden && (event.key === "Tab" || event.key === "Enter")) {
    const first = klSuggest.querySelector("button");
    if (first) {
      event.preventDefault();
      applySuggestion(first.textContent || "");
      return;
    }
  }
  if (event.key === "Tab") {
    event.preventDefault();
    insertText("    ");
    return;
  }
  if (event.key !== "Enter") return;
  event.preventDefault();
  const position = klCode.selectionStart;
  const before = klCode.value.slice(0, position);
  const lineStart = before.lastIndexOf("\n") + 1;
  const currentLine = before.slice(lineStart);
  const indentMatch = currentLine.match(/^\s*/);
  let indent = indentMatch ? indentMatch[0] : "";
  if (/^\s*(IMPORT|IMPORTS|DEPEND|DEPENDS|DEPENDENCY|DEPENDENCIES|REQUIRE|REQUIRES|SET_UNIT|SET_PROCEDURES)\s*$/.test(currentLine)) {
    indent += "    ";
  } else if (/[\{\[]\s*$/.test(currentLine)) {
    indent += "    ";
  }
  insertText(`\n${indent}`);
}

klCode.addEventListener("input", () => {
  updateHighlight();
  scheduleKlCheck();
  updateSuggestions();
});
klCode.addEventListener("click", updateSuggestions);
klCode.addEventListener("blur", () => window.setTimeout(hideSuggestions, 120));
klCode.addEventListener("scroll", updateHighlight);
klCode.addEventListener("keydown", handleKlKeydown);


const SUGGEST_SECTIONS = ["IMPORT", "DEPENDENCIES", "SET_UNIT", "SET_PROCEDURES"];
const SUGGEST_FIELDS = [
  "NAME", "ID", "TYPE", "COUNTRY", "RARE", "CT/COST", "OC/OPERATION_COST",
  "AT", "DF", "KEYWORDS", "DESCRIPTION",
];
const SUGGEST_ENUMS = {
  TYPE: ["infantry", "tank", "artillery", "fighter", "bomber", "order", "countermeasure"],
  COUNTRY: ["SovietUnion/SU", "Britain/UK", "Germany/GER", "Japan/JP", "USA/US", "France/FR", "Italy/IT", "Poland/PL", "Finland/FI", "Anzac", "Neutral"],
  RARE: ["STANDARD", "LIMITED", "SPECIAL", "ELITE", "NONE"],
};

let suggestionRange = null;

function hideSuggestions() {
  klSuggest.hidden = true;
  klSuggest.innerHTML = "";
  suggestionRange = null;
}

function applySuggestion(value) {
  if (!suggestionRange) return;
  const [start, end] = suggestionRange;
  klCode.setRangeText(value, start, end, "end");
  klCode.focus();
  hideSuggestions();
  updateHighlight();
  scheduleKlCheck();
}

function showSuggestions(items, start) {
  if (!items.length) {
    hideSuggestions();
    return;
  }
  suggestionRange = [start, klCode.selectionStart];
  klSuggest.innerHTML = "";
  for (const item of items) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = item;
    button.addEventListener("mousedown", (event) => {
      event.preventDefault();
      applySuggestion(item);
    });
    klSuggest.appendChild(button);
  }
  klSuggest.hidden = false;
}

function updateSuggestions() {
  const position = klCode.selectionStart;
  const before = klCode.value.slice(0, position);
  const lineStart = before.lastIndexOf("\n") + 1;
  const line = before.slice(lineStart);
  const indent = line.match(/^\s*/)?.[0] || "";
  const rest = line.slice(indent.length);
  const enumMatch = rest.match(/^(TYPE|COUNTRY|RARE)\s*:\s*(.*)$/i);
  if (enumMatch) {
    const key = enumMatch[1].toUpperCase();
    const needle = enumMatch[2].trim().toLowerCase();
    const items = (SUGGEST_ENUMS[key] || []).filter((item) => item.toLowerCase().startsWith(needle));
    const colonIndex = rest.indexOf(":");
    let valueStart = lineStart + indent.length + colonIndex + 1;
    while (klCode.value[valueStart] === " ") valueStart += 1;
    showSuggestions(items, valueStart);
    return;
  }
  const keyMatch = rest.match(/^([A-Za-z_\/]+)$/);
  if (keyMatch) {
    const needle = keyMatch[1].toLowerCase();
    const items = SUGGEST_FIELDS.filter((item) => item.toLowerCase().startsWith(needle));
    showSuggestions(items, lineStart + indent.length);
    return;
  }
  if (!rest.trim()) {
    const items = indent.length === 0 ? SUGGEST_SECTIONS : SUGGEST_FIELDS;
    showSuggestions(items, lineStart + indent.length);
    return;
  }
  hideSuggestions();
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
  const rawId = typeof fields.id === "string" ? fields.id.trim() : "";
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
  setKlStatus("语法通过", "ok");
  setDiagnostics("", data.warnings || []);
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


const PULL_TYPE_MAP = {
  "步兵": "infantry", "坦克": "tank", "炮兵": "artillery", "火炮": "artillery",
  "战斗机": "fighter", "轰炸机": "bomber", "指令": "order", "反制": "countermeasure",
};
const PULL_RARITY_MAP = {
  "普通": "standard", "限定": "limited", "特殊": "special", "精英": "elite", "衍生": "none",
};

function fileStem(element) {
  const source = element?.getAttribute("src") || "";
  const name = source.split("/").pop() || "";
  try {
    return decodeURIComponent(name).replace(/\.[^.]+$/, "");
  } catch (error) {
    return name.replace(/\.[^.]+$/, "");
  }
}

function setKlValue(source, pattern, value, keyLine) {
  if (pattern.test(source)) {
    return source.replace(pattern, `$1${value}`);
  }
  const anchor = /^(\s*)SET_UNIT\s*$/im.exec(source);
  if (!anchor) return source;
  const insertAt = anchor.index + anchor[0].length;
  return `${source.slice(0, insertAt)}\n${anchor[1]}    ${keyLine}${source.slice(insertAt)}`;
}

async function pullFromForge() {
  try {
    const doc = forgeFrame.contentDocument || forgeFrame.contentWindow?.document;
    if (!doc) {
      setDiagnostics("卡面尚未加载，请先切换到卡面并等待加载");
      setStatus("卡面尚未加载");
      return;
    }
    const textOf = (id) => {
      const element = doc.getElementById(id);
      return (element?.innerText || element?.textContent || "").trim();
    };
    const number = (id) => Number.parseInt(textOf(id), 10) || 0;
    const typeName = PULL_TYPE_MAP[fileStem(doc.getElementById("type"))] || selectedCard?.type || "infantry";
    const countryName = fileStem(doc.getElementById("faction")).toLowerCase() || selectedCard?.country || "soviet";
    const rarityName = PULL_RARITY_MAP[fileStem(doc.getElementById("rarity"))] || selectedCard?.rarity || "standard";
    const keywords = selectedCard?.keywords || [];
    const card = {
      ...(selectedCard || {
        id: "card_custom",
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
      type: typeName,
      country: countryName,
      rarity: rarityName,
      text: textOf("b-text"),
      keywords,
    };
    selectedCard = card;
    updateMeta(card);
    let source = klCode.value;
    source = setKlValue(source, /^(\s*NAME\s*:\s*).*$/im, JSON.stringify(card.name), `NAME: ${JSON.stringify(card.name)}`);
    source = setKlValue(source, /^(\s*ID\s*:\s*).*$/im, card.id, `ID: ${card.id}`);
    source = setKlValue(source, /^(\s*TYPE\s*:\s*).*$/im, card.type, `TYPE: ${card.type}`);
    source = setKlValue(source, /^(\s*COUNTRY\s*:\s*).*$/im, card.country, `COUNTRY: ${card.country}`);
    source = setKlValue(source, /^(\s*RARE\s*:\s*).*$/im, card.rarity, `RARE: ${card.rarity}`);
    source = setKlValue(source, /^(\s*(?:CT\/COST|CT|COST)\s*:\s*).*$/im, String(card.cost), `CT/COST: ${card.cost}`);
    source = setKlValue(source, /^(\s*(?:OC\/OPERATION_COST|OC|OPERATION_COST|OP)\s*:\s*).*$/im, String(card.op), `OC/OPERATION_COST: ${card.op}`);
    source = setKlValue(source, /^(\s*AT\s*:\s*).*$/im, String(card.at), `AT: ${card.at}`);
    source = setKlValue(source, /^(\s*DF\s*:\s*).*$/im, String(card.df), `DF: ${card.df}`);
    const keywordLine = `[${keywords.join(", ")}]`;
    source = setKlValue(source, /^(\s*KEYWORDS\s*:\s*).*$/im, keywordLine, `KEYWORDS: ${keywordLine}`);
    if (/DESCRIPTION\s*:\s*"""/i.test(source)) {
      source = source.replace(/DESCRIPTION\s*:\s*"""[\s\S]*?"""/i, `DESCRIPTION: ${JSON.stringify(card.text)}`);
    } else {
      source = setKlValue(source, /^(\s*DESCRIPTION\s*:\s*).*$/im, JSON.stringify(card.text), `DESCRIPTION: ${JSON.stringify(card.text)}`);
    }
    klCode.value = source;
    updateHighlight();
    scheduleKlCheck();
    setDiagnostics("", [`已从卡面读取全部字段：${card.name}`]);
    setStatus("已从卡面读取");
  } catch (error) {
    setDiagnostics(`读取卡面失败：${error}`);
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
  parseCard().catch((error) => {
    setKlStatus(String(error), "error");
    setStatus(`解析失败: ${error}`);
  });
});
document.getElementById("sync-card").addEventListener("click", syncForge);
document.getElementById("pull-card").addEventListener("click", pullFromForge);
document.getElementById("save-card").addEventListener("click", () => saveCard(false));
document.getElementById("write-card").addEventListener("click", () => saveCard(true));
filter.addEventListener("input", renderFiles);

updateHighlight();
loadFiles()
  .then(() => setStatus("就绪"))
  .catch((error) => setStatus(String(error)));
