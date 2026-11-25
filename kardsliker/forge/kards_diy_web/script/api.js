/*
 * Kards DIY local API.
 * Exposes window.KardsDIY.setCard(spec) and window.KardsDIY.render(spec).
 * The UI remains the original editor; this only drives the existing DOM.
 */
(function () {
  const bText = document.getElementById("b-text");
  const title = document.getElementById("title");
  const kredit = document.getElementById("kredit");
  const opredit = document.getElementById("opredit");
  const attack = document.getElementById("attack");
  const defense = document.getElementById("defense");
  const pictureImg = document.getElementById("picture-img");
  const picture = document.getElementById("picture");

  function setIndex(fn, index) {
    const next = typeof index === "number" ? index : 0;
    if (fn === window.onTypeClick) {
      window.cur_type = next - 1;
      window.onTypeClick();
      return;
    }
    if (fn === window.onRarityClick) {
      window.cur_rarity = next - 1;
      window.onRarityClick();
      return;
    }
    if (fn === window.onSetClick) {
      window.cur_set = next - 1;
      window.onSetClick();
      return;
    }
    window.cur_faction = next - 1;
    window.onFactionClick();
  }

  function waitForImage(src) {
    return new Promise((resolve, reject) => {
      pictureImg.onload = () => resolve();
      pictureImg.onerror = () => reject(new Error("card art failed to load"));
      pictureImg.src = src;
      pictureImg.style.display = "block";
    });
  }

  function fitArtwork() {
    if (!pictureImg.naturalWidth || !pictureImg.naturalHeight) return;
    const box = picture.getBoundingClientRect();
    const scale = Math.max(
      box.width / pictureImg.naturalWidth,
      box.height / pictureImg.naturalHeight,
    );
    const x = (box.width - pictureImg.naturalWidth * scale) / 2;
    const y = (box.height - pictureImg.naturalHeight * scale) / 2;
    pictureImg.style.transform = `translate(${x}px, ${y}px) scale(${scale})`;
  }

  async function setCard(spec) {
    setIndex(window.onTypeClick, spec.typeIndex ?? 0);
    setIndex(window.onRarityClick, spec.rarityIndex ?? 0);
    setIndex(window.onSetClick, spec.setIndex ?? 0);
    setIndex(window.onFactionClick, spec.factionIndex ?? 3);

    title.innerText = spec.title ?? "";
    if (spec.titleSize) title.style.fontSize = `${spec.titleSize}px`;
    kredit.innerText = String(spec.cost ?? 0);
    window.onKreditInput();
    opredit.innerText = String(spec.operationCost ?? 0);
    window.onOpeditInput();
    attack.innerText = String(spec.attack ?? 0);
    window.onAttackInput();
    defense.innerText = String(spec.defense ?? 0);
    window.onDefenseInput();
    bText.innerHTML = spec.bodyHtml ?? spec.body ?? "";
    if (spec.bodySize) bText.style.fontSize = `${spec.bodySize}px`;

    if (spec.art) {
      await waitForImage(spec.art);
      fitArtwork();
    }
    await document.fonts.ready;
    await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
    return true;
  }

  async function render(spec) {
    await setCard(spec);
    await new Promise((resolve) => setTimeout(resolve, 120));
    const canvas = await window.html2canvas(document.getElementById("main"), {
      useCORS: true,
      backgroundColor: null,
      scale: 1,
    });
    return canvas.toDataURL("image/png");
  }

  window.KardsDIY = { setCard, render };
})();
