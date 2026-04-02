const form = document.getElementById("manager-form");
const resultBox = document.getElementById("result-box");
const statusText = document.getElementById("status-text");
const submitButton = document.getElementById("submit-button");
const fillSampleButton = document.getElementById("fill-sample");

const sample = {
  name: "王牌经纪人",
  slug: "",
  long_term_goal: "6 个月内把自己打造成有明确定位的个人品牌，并获得第一批商业合作",
  current_identity: "上班中的产品经理，正在做自媒体起步",
  current_resources: "有行业经验，会写内容，会基础剪辑，已有少量粉丝基础",
  current_projects: "内容选题、账号更新、咨询服务打磨",
  daily_time_budget: "工作日晚上 2 小时，周末每天 4 小时",
  style: "professional",
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
    style: data.get("style") || "professional",
    profile: {
      long_term_goal: data.get("long_term_goal") || "",
      current_identity: data.get("current_identity") || "",
      current_resources: data.get("current_resources") || "",
      current_projects: data.get("current_projects") || "",
      daily_time_budget: data.get("daily_time_budget") || "",
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
