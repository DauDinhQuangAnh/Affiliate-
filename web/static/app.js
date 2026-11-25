const form = document.getElementById("tts-form");
const slugInput = document.getElementById("slug-input");
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

const projectsList = document.getElementById("projects-list");
const btnRefresh = document.getElementById("btn-refresh");
const shotlistPreview = document.getElementById("shotlist-preview");
const shotlistContent = document.getElementById("shotlist-content");
const btnCloseShotlist = document.getElementById("btn-close-shotlist");

let voicesMap = {};

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
    voiceDesc.textContent = "Tự động chọn ngẫu nhiên 1 trong 12 giọng để tránh trùng lặp âm thanh giữa các video.";
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

      const btnLoad = document.createElement("button");
      btnLoad.type = "button";
      btnLoad.className = "btn-secondary";
      btnLoad.textContent = "Mở";
      btnLoad.onclick = () => {
        slugInput.value = p.slug;
        textInput.value = p.text || "";
        updateWordCounter();
        if (p.has_audio) {
          showAudioResult({
            slug: p.slug,
            chosen_desc: "Tải lại từ thư mục output/",
            duration_sec: "-",
            size_kb: "-",
            audio_url: p.audio_url,
          });
        }
        if (p.has_shotlist) {
          shotlistContent.textContent = p.shotlist;
          shotlistPreview.classList.remove("hidden");
        } else {
          shotlistPreview.classList.add("hidden");
        }
      };

      actions.appendChild(btnLoad);
      row.appendChild(info);
      row.appendChild(actions);
      projectsList.appendChild(row);
    });
  } catch (err) {
    console.error("Không tải được danh sách dự án:", err);
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
        .map((m) => `• <strong>${m.word}</strong> <em>(${m.group})</em>`)
        .join("<br>");
      bannedAlert.classList.remove("hidden");
    }
  } catch (err) {
    bannedStatus.textContent = "Lỗi kiểm tra từ cấm.";
  }
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  btnGenerate.disabled = true;
  btnGenerateText.textContent = "⏳ Đang tạo giọng đọc & Mastering...";

  try {
    const res = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        slug: slugInput.value,
        text: textInput.value,
        voice: voiceSelect.value,
        speed: parseFloat(speedRange.value),
      }),
    });

    const data = await res.json();
    if (!res.ok) {
      alert(data.detail || "Không thể tạo file âm thanh.");
      return;
    }

    showAudioResult(data);
    await loadProjects();
  } catch (err) {
    alert("Lỗi kết nối tới server Python.");
  } finally {
    btnGenerate.disabled = false;
    btnGenerateText.textContent = "🎙️ Tạo Giọng Đọc MP3";
  }
});

voiceSelect.addEventListener("change", updateVoiceDesc);
speedRange.addEventListener("input", (e) => setSpeed(e.target.value));
document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => setSpeed(chip.dataset.speed));
});
textInput.addEventListener("input", updateWordCounter);
btnRefresh.addEventListener("click", loadProjects);
btnCloseShotlist.addEventListener("click", () => shotlistPreview.classList.add("hidden"));

loadVoices();
loadProjects();
updateWordCounter();
