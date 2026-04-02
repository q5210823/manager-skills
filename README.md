<div align="center">

# 经纪人.skills

> 不是陪你记待办，是把你当成正在打造中的明星来经营。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)

<br>

输入你的长期目标、当前身份、当前资源、当前项目和每天可投入时间，<br>
生成一个真正会拆任务、盯进度、做复盘、必要时上压力的 AI 经纪人 Skill。

[安装](#安装) · [使用](#使用) · [功能特性](#功能特性) · [项目结构](#项目结构) · [发布说明](#发布说明) · [English](README_EN.md)

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

## 适合谁

更适合这类用户：

1. 有明确长期目标的人
2. 想做个人品牌、作品或事业增长的人
3. 执行节奏不稳定，需要外部压力的人
4. 希望被“管理”，而不是只想记任务的人

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

---

## 示例与隐私说明

仓库当前只保留示例数据：

1. `managers/example_artist_manager/`
2. `managers/sample_manager_input.json`

这两个文件都用于演示结构，不应替换为你的真实个人数据后直接提交。

真实使用时生成的其他 `managers/{slug}/` 目录默认会被 `.gitignore` 排除。

---

## 发布说明

推荐仓库名：

1. `manager-skills`
2. `manager.skills`

对外展示名建议保持：

1. 中文：`经纪人.skills`
2. 英文：`manager.skills`

这个仓库根目录本身就是可安装目录，发布后可以直接被 OpenClaw / AgentSkills 体系按目录安装。

---

## 注意事项

1. 当前 V1 重点验证的是“经纪人角色 + 执行推进”是否成立，不是完整任务平台
2. 仓库里仍保留少量通用数据采集工具，它们在 V1 中不是主链路
3. 原始输入越具体，生成结果越接近真实可用

---

## 下一步

如果要继续往产品化推进，推荐顺序是：

1. 先把 prompt 生成链路跑通
2. 再接一个简单 CLI 或 Web 表单
3. 最后接日历或 Chrome 插件
