const form = document.getElementById("manager-form");
const resultBox = document.getElementById("result-box");
const statusText = document.getElementById("status-text");
const fillSampleButton = document.getElementById("fill-sample");
const exportJsonButton = document.getElementById("export-json");
const pageMode = new URLSearchParams(window.location.search).get("mode");

if (pageMode === "tab") {
  document.body.dataset.mode = "tab";
}

const sample = {
  name: "王牌经纪人",
  long_term_goal: "90 天内把自己打造成有明确定位的个人品牌，稳定更新内容，并拿到第一批商业合作",
  skill_tree_existing: "写作、小红书博主、基础剪辑、策展人",
  skill_tree_unlock: "直播表达、商业化销售、社群运营",
  resource_network: "已有少量粉丝基础、行业经验、基础审美、一些潜在合作人脉、工作日晚间时间",
  personality_tags: "冲劲强但容易三分钟热度、自律但会完美主义、容易在低反馈时怀疑自己、需要外部压力",
  phase_duration: "30天",
  daily_energy_hours: "工作日 3 小时，周末 5 小时",
  time_blocks: "工作日 20:00-23:00；周末 10:00-12:00；周末 14:00-17:00",
  style: "strict",
};

const tagState = {
  skill_tree_existing: [],
  personality_tags: [],
  time_blocks: [],
};

function parseList(raw) {
  return raw.split(/[，,、；;|\n]+/).map((item) => item.trim()).filter(Boolean);
}

function uniqueList(items) {
  return [...new Set(items.map((item) => item.trim()).filter(Boolean))];
}

function detectGoalType(goal) {
  if (/(品牌|IP|内容|粉丝|影响力|大V)/.test(goal)) return "品牌经营";
  if (/(收入|变现|合作|客户|订单)/.test(goal)) return "商业化";
  if (/(作品|发布|课程|账号)/.test(goal)) return "作品增长";
  if (/(减脂|健身|体能|作息)/.test(goal)) return "状态管理";
  return "综合经营";
}

function phaseCopy(phase) {
  if (phase === "7天") {
    return "用 7 天起势，重点是把执行感和可见成果做出来。";
  }
  if (phase === "30天") {
    return "用 30 天建立稳定节奏，形成一组连续成果。";
  }
  return "用 90 天做出明显成长曲线，形成经营闭环。";
}

function modeCopy(style) {
  if (style === "sarcastic") return ["毒舌模式", "你这不是冲刺，你是在给拖延做精装修。"];
  if (style === "hype") return ["鸡汤模式", "故事最好看的那一段，通常都在最想放弃的时候。"];
  return ["严师模式", "计划都排到小时了，还躲，就不是能力问题，是执行问题。"];
}

function buildPreview(payload) {
  const profile = payload.profile;
  const existing = parseList(profile.skill_tree_existing);
  const unlock = parseList(profile.skill_tree_unlock);
  const resources = parseList(profile.resource_network);
  const [modeName, modeLine] = modeCopy(payload.style);
  const blocks = profile.time_blocks.match(/\d{1,2}:\d{2}\s*-\s*\d{1,2}:\d{2}/g) || [];

  const schedule = blocks.slice(0, 3).map((block, index) => {
    if (index === 0) {
      return {
        time: block,
        title: `核心产出 - ${existing[0] || "高价值成果"}`,
        note: "必须形成可见成果，并完成打卡。",
      };
    }
    if (index === blocks.length - 1) {
      return {
        time: block,
        title: "日报复盘与打卡",
        note: "提交截图 / 拍照 / 文字总结，准备明日通告。",
      };
    }
    return {
      time: block,
      title: `升级训练 - ${unlock[0] || "关键能力"}`,
      note: "针对待解锁技能做刻意训练，不许空练。",
    };
  });

  const skillsMarkup = existing.map((item) => `<span class="selected-tag"><span>${item}</span></span>`).join("");
  const tagsMarkup = parseList(profile.personality_tags).map((item) => `<span class="selected-tag"><span>${item}</span></span>`).join("");
  const scheduleMarkup = schedule.map((item) => `
    <div class="call-sheet-row">
      <div class="call-sheet-time">${item.time}</div>
      <div class="call-sheet-task">
        <strong>${item.title}</strong>
        <span>${item.note}</span>
      </div>
    </div>
  `).join("");
  const reportChecklist = [
    "今天完成了哪 1 个最值钱的动作？",
    "哪个时间块被浪费了，为什么？",
    "有没有形成可见成果或截图证据？",
    "明天第一件事必须是什么？",
  ];
  const checkinChecklist = [
    "文字打卡",
    "成果截图或拍照",
    "飞书日程完成状态",
    "当日一句复盘",
  ];

  return `
    <div class="call-sheet-header">
      <div>
        <span class="call-sheet-label">经纪人</span>
        <span class="call-sheet-value">${payload.name}</span>
      </div>
      <div>
        <span class="call-sheet-label">模式</span>
        <span class="call-sheet-value">${modeName}</span>
      </div>
      <div>
        <span class="call-sheet-label">阶段</span>
        <span class="call-sheet-value">${profile.phase_duration}</span>
      </div>
      <div>
        <span class="call-sheet-label">精力值</span>
        <span class="call-sheet-value">${profile.daily_energy_hours}</span>
      </div>
    </div>

    <div class="call-sheet-board">
      <section class="call-sheet-card">
        <h3>艺人档案</h3>
        <p><strong>基础人设：</strong>${profile.long_term_goal}</p>
        <p><strong>目标类型：</strong>${detectGoalType(profile.long_term_goal)}</p>
        <p><strong>阶段策略：</strong>${phaseCopy(profile.phase_duration)}</p>
      </section>
      <section class="call-sheet-card">
        <h3>经纪人判断</h3>
        <p><strong>资源网络：</strong>${resources.join(" / ")}</p>
        <p><strong>经纪人一句话：</strong>${modeLine}</p>
      </section>
      <section class="call-sheet-card">
        <h3>已有技能</h3>
        <div class="selected-tags">${skillsMarkup || '<span class="call-sheet-placeholder">暂未选择</span>'}</div>
      </section>
      <section class="call-sheet-card">
        <h3>性格标签</h3>
        <div class="selected-tags">${tagsMarkup || '<span class="call-sheet-placeholder">暂未选择</span>'}</div>
      </section>
    </div>

    <section class="call-sheet-schedule">
      <h3>今日通告单</h3>
      ${scheduleMarkup || '<p class="call-sheet-placeholder">请先选择时间段，才能生成通告单。</p>'}
    </section>

    <div class="call-sheet-board call-sheet-secondary">
      <section class="call-sheet-card">
        <h3>日报区</h3>
        <ul>
          ${reportChecklist.map((item) => `<li>${item}</li>`).join("")}
        </ul>
      </section>
      <section class="call-sheet-card">
        <h3>打卡区</h3>
        <ul>
          ${checkinChecklist.map((item) => `<li>${item}</li>`).join("")}
        </ul>
      </section>
    </div>

    <div class="call-sheet-footer">
      <div><strong>时间段总览：</strong>${profile.time_blocks}</div>
      <div><strong>待解锁技能：</strong>${unlock.join(" / ") || "暂无"}</div>
      <div><strong>执行要求：</strong>完成关键动作后及时打卡，未打卡默认视为未完成。</div>
    </div>
  `;
}

function collectPayload() {
  const data = new FormData(form);
  return {
    name: data.get("name") || "王牌经纪人",
    style: data.get("style") || "strict",
    profile: {
      long_term_goal: data.get("long_term_goal") || "",
      skill_tree_existing: data.get("skill_tree_existing") || "",
      skill_tree_unlock: data.get("skill_tree_unlock") || "",
      resource_network: data.get("resource_network") || "",
      personality_tags: data.get("personality_tags") || "",
      phase_duration: data.get("phase_duration") || "30天",
      daily_energy_hours: data.get("daily_energy_hours") || "",
      time_blocks: data.get("time_blocks") || "",
    },
  };
}

function syncHiddenField(target) {
  const hidden = form.elements.namedItem(target);
  if (!hidden) return;
  hidden.value = tagState[target].join("、");
}

function renderSelected(target) {
  const container = document.querySelector(`.selected-tags[data-target="${target}"]`);
  if (!container) return;
  container.innerHTML = "";
  tagState[target].forEach((value) => {
    const chip = document.createElement("span");
    chip.className = "selected-tag";
    chip.innerHTML = `<span>${value}</span><button type="button" data-target="${target}" data-value="${value}">×</button>`;
    container.appendChild(chip);
  });
  document.querySelectorAll(`.tag-picker[data-target="${target}"] .tag-chip`).forEach((button) => {
    button.classList.toggle("is-active", tagState[target].includes(button.dataset.value));
  });
  syncHiddenField(target);
}

function setTagValues(target, values) {
  tagState[target] = uniqueList(values);
  renderSelected(target);
}

function addTagValue(target, value) {
  if (!value.trim()) return;
  setTagValues(target, [...tagState[target], value.trim()]);
}

function setStatus(text) {
  statusText.textContent = text;
}

function setResult(text) {
  resultBox.innerHTML = text;
}

function fillForm(data) {
  Object.entries(data).forEach(([key, value]) => {
    const node = form.elements.namedItem(key);
    if (!node) return;
    if (node instanceof RadioNodeList) {
      node.value = value;
      return;
    }
    node.value = value;
  });
  setTagValues("skill_tree_existing", parseList(data.skill_tree_existing || ""));
  setTagValues("personality_tags", parseList(data.personality_tags || ""));
  setTagValues("time_blocks", parseList((data.time_blocks || "").replace(/；/g, "、")));
}

async function saveDraft() {
  const payload = collectPayload();
  await chrome.storage.local.set({ managerDraft: payload });
}

async function restoreDraft() {
  const result = await chrome.storage.local.get("managerDraft");
  if (result.managerDraft) {
    fillForm({
      name: result.managerDraft.name,
      style: result.managerDraft.style,
      ...result.managerDraft.profile,
    });
    setStatus("已恢复上次草稿。");
  }
}

document.querySelectorAll(".tag-picker").forEach((picker) => {
  picker.addEventListener("click", async (event) => {
    const chip = event.target.closest(".tag-chip");
    if (!chip) return;
    const target = picker.dataset.target;
    const value = chip.dataset.value;
    if (tagState[target].includes(value)) {
      setTagValues(target, tagState[target].filter((item) => item !== value));
    } else {
      addTagValue(target, value);
    }
    await saveDraft();
  });
});

document.querySelectorAll(".tag-search-input").forEach((input) => {
  input.addEventListener("input", () => {
    const target = input.dataset.target;
    const keyword = input.value.trim();
    document.querySelectorAll(`.tag-picker[data-target="${target}"] .tag-chip`).forEach((chip) => {
      const matched = !keyword || chip.dataset.value.includes(keyword);
      chip.hidden = !matched;
    });
  });
});

document.querySelectorAll(".custom-tag-input").forEach((input) => {
  input.addEventListener("keydown", async (event) => {
    if (event.key !== "Enter") return;
    event.preventDefault();
    const target = input.dataset.target;
    addTagValue(target, input.value);
    input.value = "";
    await saveDraft();
  });
});

document.querySelectorAll(".selected-tags").forEach((container) => {
  container.addEventListener("click", async (event) => {
    const button = event.target.closest("button[data-target]");
    if (!button) return;
    const { target, value } = button.dataset;
    setTagValues(target, tagState[target].filter((item) => item !== value));
    await saveDraft();
  });
});

fillSampleButton.addEventListener("click", async () => {
  fillForm(sample);
  await saveDraft();
  setStatus("示例已填好，可以直接测试。");
});

exportJsonButton.addEventListener("click", async () => {
  const payload = collectPayload();
  const blob = new Blob([JSON.stringify(payload.profile, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "manager_profile.json";
  link.click();
  URL.revokeObjectURL(url);
  setStatus("已导出 JSON。");
  await saveDraft();
});

form.addEventListener("input", async () => {
  await saveDraft();
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = collectPayload();
  setResult(buildPreview(payload));
  setStatus("通告单已生成。你现在看到的是更接近真实排程的预览。");
  await saveDraft();
});

restoreDraft();
