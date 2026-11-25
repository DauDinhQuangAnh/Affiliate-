const btnNewProject = document.getElementById("btn-new-project");
const scriptForm = document.getElementById("script-form");
const productNameInput = document.getElementById("product-name-input");
const priceInput = document.getElementById("price-input");
const painInput = document.getElementById("pain-input");
const hookSelect = document.getElementById("hook-select");
const highlightsInput = document.getElementById("highlights-input");
const slugPreview = document.getElementById("slug-preview");
const btnBuildScript = document.getElementById("btn-build-script");

const ttsForm = document.getElementById("tts-form");
const textInput = document.getElementById("text-input");
const wordCounter = document.getElementById("word-counter");
const voiceSelect = document.getElementById("voice-select");
const specificVoicesGroup = document.getElementById("specific-voices-group");
const voiceDesc = document.getElementById("voice-desc");
const speedRange = document.getElementById("speed-range");
const speedValue = document.getElementById("speed-value");
const btnGenerate = document.getElementById("btn-generate");
const btnGenerateText = document.getElementById("btn-generate-text");

const btnCheckBanned = document.getElementById("btn-check-banned");
const btnFixBanned = document.getElementById("btn-fix-banned");
const btnNormalizeTts = document.getElementById("btn-normalize-tts");
const bannedStatus = document.getElementById("banned-status");
const bannedAlert = document.getElementById("banned-alert");

const playerEmpty = document.getElementById("player-empty");
const playerActive = document.getElementById("player-active");
const audioPlayer = document.getElementById("audio-player");
const downloadLink = document.getElementById("download-link");
const resSlug = document.getElementById("res-slug");
const resVoiceDesc = document.getElementById("res-voice-desc");
const resDuration = document.getElementById("res-duration");
const resSize = document.getElementById("res-size");

const shotlistPanel = document.getElementById("shotlist-panel");
const shotlistContent = document.getElementById("shotlist-content");
const btnCopyShotlist = document.getElementById("btn-copy-shotlist");

const projectsList = document.getElementById("projects-list");
const btnRefresh = document.getElementById("btn-refresh");
const toastEl = document.getElementById("toast");

let voicesMap = {};
let activeSlug = "";
let toastTimer = null;

function showToast(message) {
  toastEl.textContent = message;
  toastEl.classList.remove("hidden");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toastEl.classList.add("hidden"), 3200);
}

function toClientSlug(str) {
  return str
    .replace(/đ/g, "d")
    .replace(/Đ/g, "D")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function updateSlugPreview() {
  const s = toClientSlug(productNameInput.value.trim());
  activeSlug = s;
  slugPreview.textContent = s ? `slug: ${s}` : "slug: chưa nhập";
}

function updateWordCounter() {
  const text = textInput.value.trim();
  const words = text ? text.split(/\s+/).length : 0;
  const speed = parseFloat(speedRange.value) || 1.25;
  const estSeconds = Math.round((words / 3.0) / (speed / 1.25));
  wordCounter.textContent = `${words} từ (~${estSeconds}s)`;
}

function setSpeed(val) {
  const num = parseFloat(val).toFixed(2);
  speedRange.value = num;
  speedValue.textContent = `${num}x`;
  document.querySelectorAll(".chip").forEach((chip) => {
    chip.classList.toggle("active", parseFloat(chip.dataset.speed).toFixed(2) === num);
  });
  updateWordCounter();
}

async function loadHooks() {
  try {
    const res = await fetch("/api/hooks");
    const data = await res.json();
    hookSelect.innerHTML = "";
    data.hooks.forEach((h) => {
      const opt = document.createElement("option");
      opt.value = h.id;
      opt.textContent = `[${h.group}] ${h.label}`;
      hookSelect.appendChild(opt);
    });
  } catch (err) {
    console.error("Không tải được danh sách Hook:", err);
  }
}

async function loadVoices() {
  try {
    const res = await fetch("/api/voices");
    const data = await res.json();
    specificVoicesGroup.innerHTML = "";
    data.voices.forEach((v) => {
      voicesMap[v.key] = v;
      const opt = document.createElement("option");
      opt.value = v.key;
      const icon = v.gender === "female" ? "👩" : "👨";
      opt.textContent = `${icon} ${v.key} (${v.default_speed}x)`;
      specificVoicesGroup.appendChild(opt);
    });
  } catch (err) {
    console.error("Không tải được danh sách giọng:", err);
  }
}

function updateVoiceDesc() {
  const val = voiceSelect.value;
  if (val === "random") {
    voiceDesc.textContent = "Tự động chọn ngẫu nhiên 1 trong 12 giọng để tránh trùng lặp âm thanh.";
  } else if (val === "tiktok") {
    voiceDesc.textContent = "Chọn ngẫu nhiên 1 trong 5 giọng phong cách TikTok Review bắt tai.";
  } else if (val === "nu") {
    voiceDesc.textContent = "Chọn ngẫu nhiên 1 giọng Nữ trong kho giọng.";
  } else if (val === "nam") {
    voiceDesc.textContent = "Chọn ngẫu nhiên 1 giọng Nam trong kho giọng.";
  } else if (voicesMap[val]) {
    voiceDesc.textContent = voicesMap[val].desc;
    setSpeed(voicesMap[val].default_speed);
  }
}

function showAudioResult(data) {
  playerEmpty.classList.add("hidden");
  playerActive.classList.remove("hidden");

  resSlug.textContent = data.slug;
  resVoiceDesc.textContent = data.chosen_voice
    ? `[${data.chosen_voice}] ${data.chosen_desc}`
    : data.chosen_desc;
  resDuration.textContent = data.duration_sec !== "-" ? `${data.duration_sec}s` : "Audio sẵn sàng";
  resSize.textContent = data.size_kb !== "-" ? `${data.size_kb} KB` : "MP3";

  audioPlayer.src = data.audio_url;
  audioPlayer.play().catch(() => {});

  downloadLink.href = data.audio_url;
  downloadLink.download = `${data.slug}-voice.mp3`;
  downloadLink.classList.remove("hidden");
}

async function loadProjects() {
  try {
    const res = await fetch("/api/projects");
    const data = await res.json();
    projectsList.innerHTML = "";

    if (!data.projects.length) {
      projectsList.innerHTML = `<div class="empty-state">Chưa có sản phẩm nào trong <code>output/</code>.</div>`;
      return;
    }

    data.projects.forEach((p) => {
      const row = document.createElement("div");
      row.className = "project-item";

      const info = document.createElement("div");
      info.className = "project-item-info";
      info.innerHTML = `<strong>${p.slug}</strong><span class="hint-text">${p.has_audio ? "Có MP3" : "Chưa có MP3"} ${p.has_shotlist ? "• Có Shotlist" : ""}</span>`;

      const actions = document.createElement("div");
      actions.className = "project-actions";

      const btnOpen = document.createElement("button");
      btnOpen.type = "button";
      btnOpen.className = "btn-secondary";
      btnOpen.textContent = "Mở";
      btnOpen.onclick = () => {
        productNameInput.value = p.slug;
        updateSlugPreview();
        textInput.value = p.text || "";
        updateWordCounter();
        bannedAlert.classList.add("hidden");
        bannedStatus.textContent = "";

        if (p.has_audio) {
          showAudioResult({
            slug: p.slug,
            chosen_desc: "Tải lại từ thư mục output/",
            duration_sec: "-",
            size_kb: "-",
            audio_url: p.audio_url,
          });
        } else {
          playerActive.classList.add("hidden");
          playerEmpty.classList.remove("hidden");
          downloadLink.classList.add("hidden");
        }

        if (p.has_shotlist) {
          shotlistContent.textContent = p.shotlist;
          shotlistPanel.classList.remove("hidden");
        } else {
          shotlistPanel.classList.add("hidden");
        }
        showToast(`Đã mở sản phẩm "${p.slug}".`);
      };

      const btnDel = document.createElement("button");
      btnDel.type = "button";
      btnDel.className = "btn-danger-ghost";
      btnDel.textContent = "Xóa";
      btnDel.onclick = async () => {
        const delRes = await fetch(`/api/projects/${encodeURIComponent(p.slug)}`, { method: "DELETE" });
        if (delRes.ok) {
          if (activeSlug === p.slug) {
            resetWorkspace();
          }
          await loadProjects();
          showToast(`Đã xóa "${p.slug}".`);
        }
      };

      actions.appendChild(btnOpen);
      actions.appendChild(btnDel);
      row.appendChild(info);
      row.appendChild(actions);
      projectsList.appendChild(row);
    });
  } catch (err) {
    console.error("Không tải được danh sách dự án:", err);
  }
}

function resetWorkspace() {
  productNameInput.value = "";
  priceInput.value = "";
  painInput.value = "";
  highlightsInput.value = "";
  textInput.value = "";
  bannedAlert.classList.add("hidden");
  bannedStatus.textContent = "";
  shotlistPanel.classList.add("hidden");
  playerActive.classList.add("hidden");
  playerEmpty.classList.remove("hidden");
  downloadLink.classList.add("hidden");
  audioPlayer.removeAttribute("src");
  updateSlugPreview();
  updateWordCounter();
}

btnNewProject.addEventListener("click", () => {
  resetWorkspace();
  productNameInput.focus();
  showToast("Đã làm mới để nhập sản phẩm mới.");
});

scriptForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const productName = productNameInput.value.trim();
  if (!productName) return;

  btnBuildScript.disabled = true;
  btnBuildScript.textContent = "⏳ Đang tạo kịch bản...";

  const highlights = highlightsInput.value
    .split(/[,\n]+/)
    .map((s) => s.trim())
    .filter(Boolean);

  try {
    const res = await fetch("/api/build-script", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        product_name: productName,
        pain_point: painInput.value.trim(),
        highlights,
        price_text: priceInput.value.trim(),
        hook_id: hookSelect.value || "pain-1",
      }),
    });
    const data = await res.json();
    if (!res.ok) {
      showToast(data.detail || "Không tạo được kịch bản.");
      return;
    }

    activeSlug = data.slug;
    slugPreview.textContent = `slug: ${data.slug}`;
    textInput.value = data.voice_txt;
    shotlistContent.textContent = data.shotlist_md;
    shotlistPanel.classList.remove("hidden");
    bannedAlert.classList.add("hidden");
    bannedStatus.textContent = "✅ Đã lọc từ cấm & chuẩn hóa TTS.";
    updateWordCounter();
    await loadProjects();
    showToast(`Đã tạo kịch bản cho "${data.slug}" (${data.word_count} từ).`);
  } catch (err) {
    showToast("Lỗi kết nối khi tạo kịch bản.");
  } finally {
    btnBuildScript.disabled = false;
    btnBuildScript.textContent = "✨ Tự tạo Kịch bản & Shotlist";
  }
});

btnCheckBanned.addEventListener("click", async () => {
  const text = textInput.value.trim();
  if (!text) return;

  bannedStatus.textContent = "Đang kiểm tra...";
  bannedAlert.classList.add("hidden");

  try {
    const res = await fetch("/api/check-banned", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const data = await res.json();
    if (data.count === 0) {
      bannedStatus.textContent = "✅ Sạch từ cấm TikTok/Shopee!";
    } else {
      bannedStatus.textContent = `⚠️ Phát hiện ${data.count} cụm từ cần thay thế.`;
      bannedAlert.innerHTML = data.matches
        .map((m) => `• <strong>${m.word}</strong> → gợi ý: <em>"${m.replacement}"</em> (${m.group})`)
        .join("<br>");
      bannedAlert.classList.remove("hidden");
    }
  } catch (err) {
    bannedStatus.textContent = "Lỗi kiểm tra từ cấm.";
  }
});

btnFixBanned.addEventListener("click", async () => {
  const text = textInput.value.trim();
  if (!text) return;
  try {
    const res = await fetch("/api/fix-banned", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const data = await res.json();
    textInput.value = data.text;
    updateWordCounter();
    bannedAlert.classList.add("hidden");
    bannedStatus.textContent = data.fixed_count > 0
      ? `✅ Đã tự thay ${data.fixed_count} từ cấm.`
      : "✅ Không có từ cấm nào cần thay.";
    showToast(`Đã xử lý xong (${data.fixed_count} từ được thay thế).`);
  } catch (err) {
    showToast("Lỗi khi sửa từ cấm.");
  }
});

btnNormalizeTts.addEventListener("click", async () => {
  const text = textInput.value.trim();
  if (!text) return;
  try {
    const res = await fetch("/api/normalize-tts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const data = await res.json();
    textInput.value = data.text;
    updateWordCounter();
    showToast("Đã chuẩn hóa văn bản cho TTS.");
  } catch (err) {
    showToast("Lỗi chuẩn hóa TTS.");
  }
});

ttsForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const targetSlug = activeSlug || toClientSlug(productNameInput.value.trim());
  if (!targetSlug) {
    showToast("Vui lòng nhập Tên sản phẩm ở bước 1 trước.");
    productNameInput.focus();
    return;
  }

  btnGenerate.disabled = true;
  btnGenerateText.textContent = "⏳ Đang tạo giọng đọc & Mastering...";

  try {
    const res = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        slug: targetSlug,
        text: textInput.value,
        voice: voiceSelect.value,
        speed: parseFloat(speedRange.value),
      }),
    });

    const data = await res.json();
    if (!res.ok) {
      showToast(data.detail || "Không thể tạo file âm thanh.");
      return;
    }

    showAudioResult(data);
    await loadProjects();
    showToast(`Đã tạo xong voice.mp3 (${data.duration_sec}s)!`);
  } catch (err) {
    showToast("Lỗi kết nối tới server Python.");
  } finally {
    btnGenerate.disabled = false;
    btnGenerateText.textContent = "🎙️ Tạo Giọng Đọc MP3";
  }
});

btnCopyShotlist.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(shotlistContent.textContent);
    showToast("Đã sao chép Shotlist.");
  } catch {
    showToast("Không sao chép được.");
  }
});

productNameInput.addEventListener("input", updateSlugPreview);
voiceSelect.addEventListener("change", updateVoiceDesc);
speedRange.addEventListener("input", (e) => setSpeed(e.target.value));
document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => setSpeed(chip.dataset.speed));
});
textInput.addEventListener("input", updateWordCounter);
btnRefresh.addEventListener("click", loadProjects);

loadHooks();
loadVoices();
loadProjects();
updateSlugPreview();
updateWordCounter();
