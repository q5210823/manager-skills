const form = document.getElementById("manager-form");
const resultBox = document.getElementById("result-box");
const statusText = document.getElementById("status-text");
const submitButton = document.getElementById("submit-button");
const fillSampleButton = document.getElementById("fill-sample");

const sample = {
  name: "王牌经纪人",
  slug: "",
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

function setStatus(text) {
  statusText.textContent = text;
}

function setResult(value) {
  resultBox.textContent = value;
}

function fillForm(data) {
  Object.entries(data).forEach(([key, value]) => {
    const node = form.elements.namedItem(key);
    if (!node) {
      return;
    }
    if (node instanceof RadioNodeList) {
      node.value = value;
      return;
    }
    node.value = value;
  });
}

fillSampleButton.addEventListener("click", () => {
  fillForm(sample);
  setStatus("示例已填好，现在可以直接生成。");
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  submitButton.disabled = true;
  setStatus("经纪人正在整理通告。");
  setResult("生成中…");

  const data = new FormData(form);
  const payload = {
    name: data.get("name") || "王牌经纪人",
    slug: data.get("slug") || "",
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

  try {
    const response = await fetch("/api/create", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const result = await response.json();
    if (!response.ok || !result.ok) {
      throw new Error(result.error || "生成失败");
    }

    setStatus("经纪人已入职。");
    setResult(
      [
        `name: ${result.name}`,
        `slug: ${result.slug}`,
        `skill_dir: ${result.skill_dir}`,
        `base_dir: ${result.base_dir}`,
        "",
        "下一步：",
        `1. 在 skills 环境里用 /${result.slug} 调用`,
        "2. 打开生成目录查看 meta.json / work.md / persona.md / SKILL.md",
      ].join("\n"),
    );
  } catch (error) {
    setStatus("生成失败。");
    setResult(String(error.message || error));
  } finally {
    submitButton.disabled = false;
  }
});
