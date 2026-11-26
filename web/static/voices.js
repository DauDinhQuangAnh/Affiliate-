const sampleTextInput = document.getElementById("sample-text");
const voicesGrid = document.getElementById("voices-grid");
const btnTestAll = document.getElementById("btn-test-all");
const testProgress = document.getElementById("test-progress");
const useDefaultSpeed = document.getElementById("use-default-speed");
const toastEl = document.getElementById("toast");

let allVoices = [];
let currentFilter = "all";
let isBatchRunning = false;
let toastTimer = null;

function showToast(msg) {
  toastEl.textContent = msg;
  toastEl.classList.remove("hidden");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toastEl.classList.add("hidden"), 3000);
}

function getFilteredVoices() {
  if (currentFilter === "tiktok") {
    return allVoices.filter((v) => v.key.includes("tiktok") || v.key.includes("adam"));
  }
  if (currentFilter === "male") {
    return allVoices.filter((v) => v.gender === "male");
  }
  if (currentFilter === "female") {
    return allVoices.filter((v) => v.gender === "female");
  }
  return allVoices;
}

function renderVoices() {
  const list = getFilteredVoices();
  voicesGrid.innerHTML = "";

  list.forEach((v) => {
    const card = document.createElement("article");
    card.className = "panel voice-card";
    card.dataset.voice = v.key;

    const genderLabel = v.gender === "male" ? "👨 Nam" : "👩 Nữ";
    const isHot = v.key.includes("adam") || v.key.includes("tiktok");

    card.innerHTML = `
      <div class="voice-card-head">
        <div>
          <strong class="voice-title">${v.key}</strong>
          <div class="voice-badges">
            <span class="meta-badge">${genderLabel}</span>
            <span class="meta-badge">${v.default_speed}x</span>
            ${isHot ? '<span class="meta-badge hot-badge">Trending</span>' : ""}
          </div>
        </div>
        <a href="/?voice=${encodeURIComponent(v.key)}" class="btn-ghost">Dùng giọng này →</a>
      </div>
      <p class="hint-text voice-card-desc">${v.desc}</p>
      <div class="voice-card-actions">
        <button type="button" class="btn-secondary-accent btn-preview" data-voice="${v.key}">
          ▶️ Tạo &amp; Nghe thử
        </button>
        <span class="meta-badge duration-badge hidden">0s</span>
      </div>
      <audio class="card-audio hidden" controls preload="none"></audio>
    `;

    card.querySelector(".btn-preview").addEventListener("click", () => previewSingleVoice(card, v));
    voicesGrid.appendChild(card);
  });
}

async function previewSingleVoice(card, voiceObj, autoPlay = true) {
  const btn = card.querySelector(".btn-preview");
  const audioEl = card.querySelector(".card-audio");
  const durBadge = card.querySelector(".duration-badge");
  const text = sampleTextInput.value.trim();

  if (!text) {
    showToast("Vui lòng nhập câu thoại test.");
    return false;
  }

  btn.disabled = true;
  btn.textContent = "⏳ Đang tạo...";

  try {
    const res = await fetch("/api/preview-voice", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        voice: voiceObj.key,
        text,
        speed: useDefaultSpeed.checked ? voiceObj.default_speed : 1.25,
      }),
    });
    const data = await res.json();
    if (!res.ok) {
      showToast(data.detail || `Lỗi giọng ${voiceObj.key}`);
      return false;
    }

    durBadge.textContent = `${data.duration_sec}s`;
    durBadge.classList.remove("hidden");
    audioEl.src = data.audio_url;
    audioEl.classList.remove("hidden");
    if (autoPlay) {
      audioEl.play().catch(() => {});
    }
    return true;
  } catch {
    showToast(`Lỗi kết nối khi tạo giọng ${voiceObj.key}`);
    return false;
  } finally {
    btn.disabled = false;
    btn.textContent = "🔄 Nghe lại / Tạo mới";
  }
}

btnTestAll.addEventListener("click", async () => {
  if (isBatchRunning) return;
  isBatchRunning = true;
  btnTestAll.disabled = true;

  const cards = Array.from(voicesGrid.querySelectorAll(".voice-card"));
  for (let i = 0; i < cards.length; i++) {
    const card = cards[i];
    const key = card.dataset.voice;
    const vObj = allVoices.find((x) => x.key === key);
    if (!vObj) continue;

    testProgress.textContent = `Đang tạo ${i + 1}/${cards.length}: ${key}...`;
    await previewSingleVoice(card, vObj, false);
  }

  testProgress.textContent = `✅ Hoàn tất ${cards.length}/${cards.length} giọng`;
  isBatchRunning = false;
  btnTestAll.disabled = false;
  showToast("Đã tạo xong toàn bộ audio nghe thử! Bấm play từng thẻ để so sánh.");
});

document.querySelectorAll(".filter-chips .chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    document.querySelectorAll(".filter-chips .chip").forEach((c) => c.classList.remove("active"));
    chip.classList.add("active");
    currentFilter = chip.dataset.filter;
    renderVoices();
  });
});

localStorage.removeItem("affiliate_elevenlabs_key");

async function init() {
  try {
    const res = await fetch("/api/voices");
    const data = await res.json();
    allVoices = data.voices || [];
    renderVoices();
  } catch {
    showToast("Không tải được danh sách giọng.");
  }
}

init();
