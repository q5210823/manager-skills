<div align="center">

# 经纪人.skills

> 不是陪你记待办，是把你当成正在打造中的明星来经营。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)

<br>

输入你的长期目标、当前身份、当前资源、当前项目和每天可投入时间，<br>
生成一个真正会拆任务、盯进度、做复盘、必要时上压力的 AI 经纪人 Skill。

[安装](#安装) · [使用](#使用) · [效果示例](#效果示例) · [功能特性](#功能特性) · [项目结构](#项目结构) · [English](README_EN.md)

</div>

---

## 产品定位

很多人不是没有目标，而是没有一个持续盯着自己的人。

`经纪人.skills` 不是普通待办工具，也不是泛泛而谈的聊天助手。它做的是另一件事：

1. 帮你判断什么最值得推进
2. 把长期目标拆成每周和每天的动作
3. 在你拖延时给出直接反馈
4. 每天做复盘，持续修正节奏

如果用一句话概括：

**它不是帮你记事，而是帮你上升。**

---

## V1 范围

V1 先做最小闭环：

1. 录入 5 项基础信息
2. 生成经纪人人设
3. 生成阶段策略、周重点、今日通告
4. 生成三档督促风格
5. 生成每日复盘规则

V1 暂不包含：

1. 日历同步
2. Chrome 插件 UI
3. 外部平台自动抓取
4. 多角色协作

---

## 用户输入

V1 固定只收这 5 项：

1. `长期目标`
2. `当前身份`
3. `当前资源`
4. `当前正在做的项目`
5. `每天可投入时间`

建议把输入写得尽量具体，因为最终任务强度会直接受这些字段约束。

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

在支持 AgentSkills 的环境里调用：

```text
/create-manager
```

随后根据提示输入：

1. 长期目标
2. 当前身份
3. 当前资源
4. 当前正在做的项目
5. 每天可投入时间

生成的经纪人 Skill 默认写入：

```text
./managers/{slug}/
```

---

## 本地入口

### 1. CLI

如果你想先不接 AgentSkills，直接从 JSON 生成最小版本：

```bash
python3 tools/create_manager.py --input managers/sample_manager_input.json
```

### 2. 本地网页

如果你想用表单版本地网页：

```bash
python3 tools/manager_web.py
```

然后打开 [http://127.0.0.1:8765](http://127.0.0.1:8765)。

---

## 输出内容

经纪人 Skill 会稳定输出以下内容：

1. `艺人经营档案`
2. `本周重点`
3. `今日通告`
4. `催进度反馈`
5. `每日复盘`

高压模式允许更尖锐，但依然有边界：

1. 可以指出拖延和借口
2. 可以强调机会成本
3. 不做人身羞辱
4. 不持续失控攻击

---

## 效果示例

> 输入：
>
> `6个月内把自己打造成有明确定位的个人品牌，并获得第一批商业合作`
>
> `上班中的产品经理，正在做自媒体起步`
>
> `有行业经验，会写内容，会基础剪辑，已有少量粉丝基础`

**场景一：今日通告**

```text
经纪人.skills ❯ 今天别摊大饼，只做 3 件能抬高结果的事：

             1. 定一句话定位，写完就定稿
             2. 完成 1 条内容并发布，不准只停留在草稿
             3. 把咨询服务介绍页补到能发给别人看

             今天如果没有可见产出，就不算推进。
```

**场景二：拖延纠偏**

```text
用户             ❯ 我今天都在看资料，也不算完全没做事吧

经纪人.skills ❯ 你是在准备，不是在推进。
             如果资料没有变成作品、发布或成交动作，它就只是延迟执行的体面借口。
```

**场景三：复盘**

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
| **Part A — Execution System** | 阶段判断、周重点、日任务规则、复盘规则 |
| **Part B — Persona** | 角色定位、说话风格、督导强度、行为边界 |

运行逻辑：

`收到目标或问题 -> Execution System 判断最该推进什么 -> Persona 决定语气和压力 -> 输出经纪人式回应`

### 支持的督导风格

1. `Gentle`
   刚起步时建立节奏
2. `Professional`
   像职业经纪人安排通告
3. `High Pressure`
   连续拖延或临近关键节点时上强度

### 进化机制

1. 追加信息 -> 用 `merger.md` 生成增量
2. 对话纠正 -> 写入 `Correction` 层，立即生效
3. 版本管理 -> 支持更新与回滚

---

## 项目结构

本项目遵循 AgentSkills 风格，整个仓库根目录本身就是一个可安装 skill：

```text
manager-skills/
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
│   ├── skill_writer.py
│   └── version_manager.py
├── managers/
│   ├── example_artist_manager/
│   └── sample_manager_input.json
├── docs/
│   ├── PRD.md
│   └── RELEASE_CHECKLIST.md
├── web/
└── LICENSE
```
