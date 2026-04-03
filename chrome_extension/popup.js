const form = document.getElementById("manager-form");
const resultBox = document.getElementById("result-box");
const statusText = document.getElementById("status-text");
const fillSampleButton = document.getElementById("fill-sample");
const exportJsonButton = document.getElementById("export-json");

const sample = {
  name: "王牌经纪人",
  long_term_goal: "90 天内把自己打造成有明确定位的个人品牌，稳定更新内容，并拿到第一批商业合作",
  skill_tree_existing: "写作、产品思维、基础剪辑、选题策划",
  skill_tree_unlock: "直播表达、商业化销售、社群运营",
  resource_network: "已有少量粉丝基础、行业经验、基础审美、一些潜在合作人脉、工作日晚间时间",
  personality_tags: "冲劲强但容易三分钟热度、自律但会完美主义、容易在低反馈时怀疑自己",
  phase_duration: "30天",
  daily_energy_hours: "工作日 3 小时，周末 5 小时",
  time_blocks: "工作日 20:00-23:00；周末 10:00-12:00, 14:00-17:00",
  style: "strict",
};

function parseList(raw) {
  return raw.split(/[，,、；;|\n]+/).map((item) => item.trim()).filter(Boolean);
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
    if (index === 0) return `${block}: 核心产出 - ${existing[0] || "高价值成果"}`;
    if (index === blocks.length - 1) return `${block}: 日报复盘与打卡`;
    return `${block}: 升级训练 - ${unlock[0] || "关键能力"}`;
  });

  return [
    `经纪人：${payload.name}`,
    `模式：${modeName}`,
    "",
    "【艺人档案】",
    `基础人设：${profile.long_term_goal}`,
    `目标类型：${detectGoalType(profile.long_term_goal)}`,
    `已有技能：${existing.join(" / ")}`,
    `待解锁技能：${unlock.join(" / ")}`,
    `资源网络：${resources.join(" / ")}`,
    `性格标签：${profile.personality_tags}`,
    "",
    "【阶段冲刺】",
    `阶段：${profile.phase_duration}`,
    phaseCopy(profile.phase_duration),
    `每日精力值：${profile.daily_energy_hours}`,
    `时间段：${profile.time_blocks}`,
    "",
    "【示例日程】",
    ...schedule,
    "",
    "【经纪人一句话】",
    modeLine,
  ].join("\n");
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

function setStatus(text) {
  statusText.textContent = text;
}

function setResult(text) {
  resultBox.textContent = text;
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
  setStatus("插件基础预览已生成。");
  await saveDraft();
});

restoreDraft();
