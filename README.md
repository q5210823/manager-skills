<div align="center">

# 经纪人.skills

> 不是陪你记待办，而是把你当成正在打造中的明星来经营。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)

<br>

先建立“艺人档案”，再生成阶段冲刺、按小时通告、PUA 提醒、日报和打卡区。<br>
支持 OpenClaw / Claude Code 的 skill 工作流，也提供可直接测试的 Chrome 插件原型。

[安装](#安装) · [使用](#使用) · [效果示例](#效果示例) · [功能特性](#功能特性) · [项目结构](#项目结构) · [English](README_EN.md)

</div>

---

## 产品定位

很多人不是没有目标，而是没有一个持续盯着自己的人。

`经纪人.skills` 不是普通待办工具，也不是泛泛而谈的聊天助手。它更像一个把用户当成“艺人 / 个人 IP”来经营的系统：

1. 先建立艺人档案
2. 再做 7 天 / 30 天 / 90 天阶段冲刺
3. 生成按小时的每日通告
4. 在拖延、低落、自满时切换不同 PUA 模式
5. 用日报、打卡、复盘和问责维持节奏

如果用一句话概括：

**它不是帮你记事，而是帮你上升。**

---

## 当前能力

当前版本已经支持：

1. `艺人档案录入`
   长期目标、已有技能、待解锁技能、资源网络、性格标签、阶段时长、精力值、时间段
2. `阶段冲刺`
   支持 `7天 / 30天 / 90天`
3. `通告生成`
   按时间块生成更像经纪人通告单的预览
4. `PUA 引擎`
   支持 `严师模式 / 毒舌模式 / 鸡汤模式`
5. `日报区 / 打卡区`
   在插件预览中直接体现
6. `OpenClaw 飞书同步工具`
   通过本地脚本接入飞书日程同步

---

## 安装

### OpenClaw

```bash
git clone https://github.com/q5210823/manager-skills.git ~/.openclaw/workspace/skills/create-manager
```

### Claude Code

```bash
mkdir -p .claude/skills
git clone https://github.com/q5210823/manager-skills.git .claude/skills/create-manager
```

### 依赖

```bash
pip3 install -r requirements.txt
```

---

## 使用

### 1. Skill 入口

在支持 AgentSkills 的环境里调用：

```text
/create-manager
```

新版流程会先建立“艺人档案”，再生成阶段计划和通告系统。

### 2. Chrome 插件测试

根目录已经带有 `manifest.json`，可以直接在 Chrome 里加载整个仓库目录：

1. 打开 `chrome://extensions/`
2. 开启开发者模式
3. 点击“加载已解压的扩展程序”
4. 选择仓库根目录

点击插件图标后，会直接打开新标签页进行测试。

### 3. OpenClaw 飞书同步

飞书同步不放在 Chrome 插件里，而是通过本地工具提供：

```bash
python3 tools/feishu_calendar_sync.py --setup
python3 tools/feishu_calendar_sync.py --list-calendars
python3 tools/feishu_calendar_sync.py --input managers/sample_manager_input.json --manager-name "王牌经纪人"
```

---

## 效果示例

> 输入：
>
> `90 天内把自己打造成有明确定位的个人品牌，稳定更新内容，并拿到第一批商业合作`
>
> `已有技能：写作、小红书博主、基础剪辑`
>
> `待解锁技能：直播表达、商业化销售、社群运营`

**场景一：今日通告单**

```text
经纪人.skills ❯ 今天别摊大饼，只排 3 个时间块：

             20:00-22:00  核心产出 - 写作
             22:00-23:00  升级训练 - 直播表达
             23:00-23:30  日报复盘与打卡

             没有可见成果，就不算推进。
```

**场景二：拖延纠偏**

```text
用户             ❯ 我今天都在看资料，也不算完全没做事吧

经纪人.skills ❯ 你是在准备，不是在推进。
             如果资料没有变成作品、发布或成交动作，它就只是延迟执行的体面借口。
```

**场景三：日报**

```text
经纪人.skills ❯ 今天最大的错误不是没做完，而是把最值钱的动作放到了最后。
             明天先做产出，再做整理。顺序错了，节奏就废了。
```

---

## 功能特性

### 生成的 Skill 结构

每个经纪人 Skill 由两部分组成，共同驱动输出：

| 部分 | 内容 |
|------|------|
| **Part A — Artist Management System** | 艺人档案、阶段冲刺、按小时通告、日报与打卡、问责与奖励 |
| **Part B — Persona / PUA Engine** | 角色定位、说话风格、严师 / 毒舌 / 鸡汤模式、复盘语气 |

运行逻辑：

`收到目标或问题 -> 经营系统判断最该推进什么 -> Persona 决定语气和压力 -> 输出经纪人式回应`

### Chrome 插件交互能力

当前插件原型已经支持：

1. 标签可搜索
2. 标签多选 + 手动补充
3. 工作日 / 周末时间段分组
4. 新标签页打开测试页
5. 通告单式预览
6. 日报区和打卡区展示

### PUA 引擎

支持三种模式：

1. `严师模式`
   冷酷、直接、骂醒你
2. `毒舌模式`
   阴阳怪气、sarcastic
3. `鸡汤模式`
   打鸡血、画大饼

### 飞书同步能力

飞书同步在 OpenClaw / 工具链中实现，而不是 Chrome 插件中：

1. 配置飞书日历凭证
2. 列出现有日历
3. 基于艺人档案生成时间块并同步到飞书日程
4. 同步失败时给出更明确的错误提示

---

## 项目结构

本项目遵循 AgentSkills 风格，整个仓库根目录本身就是一个可安装 skill：

```text
manager-skills/
├── manifest.json
├── SKILL.md
├── README.md
├── README_EN.md
├── INSTALL.md
├── prompts/
│   ├── intake.md
│   ├── work_analyzer.md
│   ├── work_builder.md
│   ├── persona_analyzer.md
│   ├── persona_builder.md
│   ├── merger.md
│   └── correction_handler.md
├── tools/
│   ├── create_manager.py
│   ├── manager_web.py
│   ├── feishu_calendar_sync.py
│   ├── skill_writer.py
│   └── version_manager.py
├── chrome_extension/
│   ├── background.js
│   ├── popup.html
│   ├── popup.css
│   └── popup.js
├── managers/
│   ├── example_artist_manager/
│   └── sample_manager_input.json
├── docs/
├── web/
└── LICENSE
```
