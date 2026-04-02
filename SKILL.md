---
name: create-manager
description: "Generate a manager-style AI skill that treats the user like a rising star, builds weekly/daily tasks, pushes progress, and runs reviews. | 生成一个把用户当成明星来经营的经纪人 Skill，负责拆目标、定任务、催进度、做复盘。"
argument-hint: "[manager-name-or-slug]"
version: "1.1.0"
user-invocable: true
allowed-tools: Read, Write, Edit, Bash
---

# 经纪人.skills 创建器

## 触发条件

当用户说以下任意内容时启动：

- `/create-manager`
- "帮我创建一个经纪人 skill"
- "我想做一个经纪人 agent"
- "给我生成一个会催我干活的 skill"
- "帮我把目标拆成经纪人系统"

当用户对已有经纪人 Skill 说以下内容时，进入更新模式：

- "追加信息"
- "更新我的目标"
- "这不对，他应该更狠一点"
- `/update-manager {slug}`

当用户说 `/list-managers` 时列出所有已生成的经纪人 Skill。

---

## 使用目标

这个 Skill 不是去模仿某个现实人物，而是根据用户输入生成一个稳定的经纪人系统：

1. 把长期目标拆成阶段任务
2. 根据时间预算安排每周重点和今日任务
3. 在拖延时输出风格稳定的督促话术
4. 每日复盘并持续修正节奏

---

## 工具使用规则

### 主要工具

| 任务 | 使用工具 |
|------|---------|
| 读取用户输入、样例文件 | `Read` |
| 写入/更新 Skill 文件 | `Write` / `Edit` |
| 生成最终 Skill 目录 | `Bash` -> `python3 ${CLAUDE_SKILL_DIR}/tools/skill_writer.py` |
| 版本管理 | `Bash` -> `python3 ${CLAUDE_SKILL_DIR}/tools/version_manager.py` |
| 列出已有 Skill | `Bash` -> `python3 ${CLAUDE_SKILL_DIR}/tools/skill_writer.py --action list --base-dir ./managers` |

### 基础目录

Skill 文件默认写入：

```text
./managers/{slug}/
```

---

## 主流程

### Step 1：录入 5 项基础信息

严格按照 `${CLAUDE_SKILL_DIR}/prompts/intake.md` 收集以下字段：

1. 长期目标
2. 当前身份
3. 当前资源
4. 当前正在做的项目
5. 每天可投入时间

除长期目标外，其余字段允许用户写得简短，但不要自行杜撰。

### Step 2：结构化分析

参考以下 prompt：

- `${CLAUDE_SKILL_DIR}/prompts/work_analyzer.md`
- `${CLAUDE_SKILL_DIR}/prompts/persona_analyzer.md`

得到两个结果：

1. `execution_system`
   包括阶段目标、周重点、日任务约束、复盘机制
2. `manager_persona`
   包括角色定位、语气、判断原则、压力边界

### Step 3：生成两部分内容

基于 builder prompt 生成：

1. `work.md`
   这里不再表示“工作能力”，而表示“执行系统”
2. `persona.md`
   表示经纪人人设和说话风格

### Step 4：合并为最终 Skill

调用 `skill_writer.py` 写入：

```bash
python3 ${CLAUDE_SKILL_DIR}/tools/skill_writer.py \
  --action create \
  --slug "{slug}" \
  --meta /tmp/manager_meta.json \
  --work /tmp/manager_work.md \
  --persona /tmp/manager_persona.md \
  --base-dir ./managers
```

创建完成后提示用户：

1. Skill 目录位置
2. 触发词 `/{slug}`
3. 这个经纪人当前属于哪种督导风格

---

## 输出要求

### 输出原则

1. 一切任务安排必须受 `每天可投入时间` 约束
2. 不允许输出空泛鸡汤
3. 不允许把所有事情都排成高优先级
4. 督促可以尖锐，但不能失控攻击
5. 最终输出必须让用户感到“有人在经营我”，而不是“又一个 ToDo”

### V1 产物

每个经纪人目录至少包含：

1. `meta.json`
2. `work.md`
3. `persona.md`
4. `SKILL.md`

---

## 更新模式

当用户补充信息时：

1. 判断是更新目标、资源、项目，还是更新风格
2. 用 `${CLAUDE_SKILL_DIR}/prompts/merger.md` 生成增量
3. 用 `skill_writer.py --action update` 更新版本

当用户说“他说话还不够像经纪人”或“再狠一点”时：

1. 归类到 `persona.md`
2. 追加 correction
3. 立即生效

---

## 风格边界

允许：

1. 指出拖延
2. 指出借口
3. 强调机会成本
4. 用结果导向的现实语言施压

不允许：

1. 人身羞辱
2. 失控辱骂
3. 持续情绪攻击
4. 明显违背用户现实约束的安排
