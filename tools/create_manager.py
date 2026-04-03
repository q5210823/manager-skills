#!/usr/bin/env python3
"""
最小 CLI 入口：基于“艺人档案”生成经纪人 Skill。

用法：
    python3 tools/create_manager.py --input managers/sample_manager_input.json
    python3 tools/create_manager.py --input input.json --name "我的经纪人" --style strict
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from skill_writer import create_skill, slugify


REQUIRED_FIELDS = [
    "long_term_goal",
    "skill_tree_existing",
    "skill_tree_unlock",
    "resource_network",
    "personality_tags",
    "phase_duration",
    "daily_energy_hours",
    "time_blocks",
]


def load_input(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    return validate_profile(data)


def validate_profile(data: dict) -> dict:
    missing = [field for field in REQUIRED_FIELDS if not str(data.get(field, "")).strip()]
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"输入信息缺少必填字段：{joined}")

    profile = {field: str(data[field]).strip() for field in REQUIRED_FIELDS}
    profile["phase_duration"] = normalize_phase(profile["phase_duration"])
    profile["daily_energy_hours"] = normalize_energy(profile["daily_energy_hours"])
    profile["time_blocks"] = normalize_time_blocks(profile["time_blocks"])
    return profile


def normalize_phase(value: str) -> str:
    text = value.strip()
    if text in {"7", "7天", "7d"}:
        return "7天"
    if text in {"30", "30天", "30d"}:
        return "30天"
    if text in {"90", "90天", "90d"}:
        return "90天"
    raise ValueError("阶段时长只支持 7天、30天、90天")


def normalize_energy(value: str) -> str:
    text = value.strip()
    if re.search(r"\d", text):
        return text
    raise ValueError("每日精力值需要包含小时数")


def normalize_time_blocks(value: str) -> str:
    text = value.strip()
    if not re.search(r"\d{1,2}:\d{2}\s*[-~]\s*\d{1,2}:\d{2}", text):
        raise ValueError("时间段格式需包含类似 20:00-23:00 的内容")
    return text.replace("~", "-")


def parse_list(raw: str) -> list[str]:
    parts = re.split(r"[，,、；;|\n]+", raw)
    return [part.strip() for part in parts if part.strip()]


def extract_hours(raw: str) -> int:
    nums = [int(item) for item in re.findall(r"(\d+)", raw)]
    return nums[0] if nums else 2


def parse_time_blocks(raw: str) -> list[str]:
    blocks = re.findall(r"\d{1,2}:\d{2}\s*-\s*\d{1,2}:\d{2}", raw)
    return [re.sub(r"\s+", "", block) for block in blocks]


def parse_time_block_groups(raw: str) -> dict[str, list[str]]:
    groups = {"workday": [], "weekend": [], "generic": []}
    segments = re.split(r"[；;\n]+", raw)
    for segment in segments:
        segment = segment.strip()
        if not segment:
            continue
        blocks = re.findall(r"\d{1,2}:\d{2}\s*-\s*\d{1,2}:\d{2}", segment)
        clean_blocks = [re.sub(r"\s+", "", block) for block in blocks]
        if not clean_blocks:
            continue
        if "工作日" in segment:
            groups["workday"].extend(clean_blocks)
        elif "周末" in segment:
            groups["weekend"].extend(clean_blocks)
        else:
            groups["generic"].extend(clean_blocks)
    return groups


def detect_goal_type(goal: str) -> str:
    if any(keyword in goal for keyword in ("品牌", "IP", "内容", "粉丝", "影响力", "大V")):
        return "品牌经营"
    if any(keyword in goal for keyword in ("收入", "变现", "合作", "客户", "订单")):
        return "商业化"
    if any(keyword in goal for keyword in ("课程", "专栏", "作品", "发布", "账号")):
        return "作品增长"
    if any(keyword in goal for keyword in ("减脂", "健身", "体能", "作息")):
        return "状态管理"
    return "综合经营"


def detect_stage(goal: str, resources: str) -> str:
    joined = f"{goal} {resources}"
    if any(keyword in joined for keyword in ("第一批", "起步", "刚开始", "冷启动")):
        return "起步验证期"
    if any(keyword in joined for keyword in ("稳定", "放大", "增长", "商业合作", "粉丝基础")):
        return "验证放大期"
    return "经营推进期"


def choose_leverage(skills: list[str], resources: list[str], goal: str) -> str:
    joined = " ".join(skills + resources)
    if any(keyword in joined for keyword in ("写作", "表达", "剪辑", "内容", "账号")):
        return "内容生产和表达能力是当前最值得放大的核心杠杆"
    if any(keyword in joined for keyword in ("人脉", "客户", "合作", "渠道")):
        return "资源转化能力是当前最值得撬动的核心杠杆"
    if "品牌" in goal:
        return "先把定位和输出稳定下来，是当前最关键的杠杆"
    return "围绕长期目标形成稳定产出，是当前最关键的杠杆"


def phase_goal(phase: str, goal: str) -> tuple[str, list[str], list[str], list[str]]:
    if phase == "7天":
        return (
            f"在 7 天内建立第一波明确的执行感，围绕“{goal}”做出可见起势",
            ["完成一个最小可见成果", "建立连续 7 天的执行节奏", "找出最有效的推进动作"],
            ["每天至少完成一个高价值动作", "优先产出，不要过度准备", "记录每日完成证据"],
            ["不要同时开太多支线", "不要把收集资料当成主要成果"],
        )
    if phase == "30天":
        return (
            f"在 30 天内围绕“{goal}”形成稳定节奏和初步成果",
            ["完成一组可展示的连续成果", "形成稳定周节奏", "验证最有效的内容或商业动作"],
            ["按周推进阶段重点", "把高能时段留给最值钱的动作", "用日报强制复盘"],
            ["不要频繁改方向", "不要让准备工作吞掉产出时间"],
        )
    return (
        f"在 90 天内围绕“{goal}”完成明显的阶段成长或商业验证",
        ["完成可见成长曲线", "建立稳定的日程执行系统", "形成可复用的方法和成果矩阵"],
        ["按月拆阶段目标", "持续输出高杠杆成果", "通过周复盘和月对赌维持压力"],
        ["不要阶段中途反复重置", "不要让低价值事务侵占黄金时段"],
    )


def daily_task_limit(hours: int) -> str:
    if hours <= 2:
        return "每天 2 到 3 个核心动作"
    if hours <= 4:
        return "每天 3 到 4 个核心动作"
    return "每天 4 到 5 个核心动作，但必须按轻重排序"


def build_schedule_blocks(time_blocks: list[str], existing_skills: list[str], unlock_skills: list[str]) -> list[str]:
    high_value = existing_skills[0] if existing_skills else "核心产出"
    growth = unlock_skills[0] if unlock_skills else "能力升级"
    fallback = [
        f"用于高价值产出：围绕 {high_value} 形成当天成果",
        f"用于推进主任务：完成当天最关键的交付动作",
        f"用于升级能力：补一段 {growth} 的针对性训练",
    ]
    rows = []
    for index, block in enumerate(time_blocks):
        rows.append(f"- {block}：{fallback[index % len(fallback)]}")
    return rows


def block_to_times(day: datetime, block: str) -> tuple[datetime, datetime]:
    start_text, end_text = block.split("-")
    start_hour, start_minute = [int(part) for part in start_text.split(":")]
    end_hour, end_minute = [int(part) for part in end_text.split(":")]
    start_dt = day.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
    end_dt = day.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
    return start_dt, end_dt


def phase_days(phase: str) -> int:
    return {"7天": 7, "30天": 30, "90天": 90}[phase]


def build_phase_event_plan(profile: dict, manager_name: str) -> list[dict]:
    timezone = ZoneInfo("Asia/Shanghai")
    now = datetime.now(timezone)
    groups = parse_time_block_groups(profile["time_blocks"])
    generic = groups["generic"]
    existing_skills = parse_list(profile["skill_tree_existing"])
    unlock_skills = parse_list(profile["skill_tree_unlock"])
    days = phase_days(profile["phase_duration"])

    event_plan = []
    for offset in range(days):
        day = now + timedelta(days=offset)
        is_weekend = day.weekday() >= 5
        if is_weekend:
            blocks = groups["weekend"] or generic or groups["workday"]
        else:
            blocks = groups["workday"] or generic or groups["weekend"]
        if not blocks:
            continue

        for idx, block in enumerate(blocks):
            start_dt, end_dt = block_to_times(day, block)
            if idx == 0:
                skill = existing_skills[idx % len(existing_skills)] if existing_skills else "核心产出"
                title = f"[经纪人通告] 核心产出 - {skill}"
                description = f"{manager_name} 安排的高价值产出时段。完成后需要文字打卡或成果截图。"
            elif idx == len(blocks) - 1:
                title = "[经纪人通告] 日报复盘与打卡"
                description = "回顾今天是否完成关键动作，提交日报、截图或拍照打卡。"
            else:
                skill = unlock_skills[(idx - 1) % len(unlock_skills)] if unlock_skills else "能力升级"
                title = f"[经纪人通告] 升级训练 - {skill}"
                description = f"用于补齐待解锁技能：{skill}。完成后记录训练结果和问题。"

            event_plan.append(
                {
                    "title": title,
                    "description": description,
                    "start": start_dt,
                    "end": end_dt,
                }
            )
    return event_plan


def normalize_style(style: str) -> str:
    aliases = {
        "strict": "strict",
        "严师": "strict",
        "严师模式": "strict",
        "sarcastic": "sarcastic",
        "毒舌": "sarcastic",
        "毒舌模式": "sarcastic",
        "hype": "hype",
        "鸡汤": "hype",
        "鸡汤模式": "hype",
        "professional": "strict",
        "high-pressure": "strict",
        "gentle": "hype",
    }
    normalized = aliases.get(style, style)
    if normalized not in {"strict", "sarcastic", "hype"}:
        raise ValueError(f"不支持的风格：{style}")
    return normalized


def style_labels(style: str) -> tuple[str, str, str]:
    if style == "strict":
        return (
            "严师模式",
            "冷酷、直接、骂醒你",
            "你不是没潜力，你是把最值钱的时段拿去逃避了。",
        )
    if style == "sarcastic":
        return (
            "毒舌模式",
            "阴阳怪气、sarcastic、让人清醒",
            "你这不是在冲刺，你这是在给拖延做精装修。",
        )
    return (
        "鸡汤模式",
        "打鸡血、画大饼、在低谷期强行续火",
        "别急着认输，你还没到故事最好看的那一段。",
    )


def build_work_content(name: str, profile: dict, style: str) -> str:
    existing_skills = parse_list(profile["skill_tree_existing"])
    unlock_skills = parse_list(profile["skill_tree_unlock"])
    resources = parse_list(profile["resource_network"])
    tags = parse_list(profile["personality_tags"])
    phase = profile["phase_duration"]
    hours = extract_hours(profile["daily_energy_hours"])
    time_blocks = parse_time_blocks(profile["time_blocks"])
    goal = profile["long_term_goal"]

    goal_type = detect_goal_type(goal)
    stage = detect_stage(goal, profile["resource_network"])
    leverage = choose_leverage(existing_skills, resources, goal)
    phase_summary, key_results, core_actions, no_go = phase_goal(phase, goal)
    schedule_blocks = build_schedule_blocks(time_blocks, existing_skills, unlock_skills)

    return f"""# {name} - Artist Management System

## 艺人档案

### 基础人设
{goal}

### 目标类型
{goal_type}

### 当前阶段
{stage}

### 技能树
#### 已有技能
""" + "\n".join(f"- {item}" for item in existing_skills) + f"""

#### 待解锁技能
""" + "\n".join(f"- {item}" for item in unlock_skills) + f"""

### 资源网络
""" + "\n".join(f"- {item}" for item in resources) + f"""

### 性格标签
""" + "\n".join(f"- {item}" for item in tags) + f"""

---

## 第一阶段冲刺

### 阶段时长
{phase}

### 阶段目标
{phase_summary}

### 关键成果
""" + "\n".join(f"- {item}" for item in key_results) + f"""

### 核心动作
""" + "\n".join(f"- {item}" for item in core_actions) + f"""

### 阶段禁区
""" + "\n".join(f"- {item}" for item in no_go) + f"""

---

## 日程排程规则

### 每日精力值
{profile["daily_energy_hours"]}

### 可投入时间段
""" + "\n".join(f"- {item}" for item in time_blocks) + f"""

### 单日任务上限
{daily_task_limit(hours)}

### 高能时段优先任务
- 围绕 {leverage}
- 优先安排最值钱的产出动作

### 低能时段优先任务
- 复盘、整理、轻量跟进
- 打卡、记录、数据回顾

### 每日通告生成规则
每天计划必须尽量精确到小时块，并包含：

1. 开始时间
2. 结束时间
3. 任务名称
4. 完成标准
5. 打卡方式

### 示例日程块
""" + "\n".join(schedule_blocks) + f"""

---

## 飞书日程同步规则

如具备飞书能力，默认将每日通告同步到飞书日程：

1. 每个任务写入独立时间块
2. 标题带优先级和任务类型
3. 未完成任务次日自动重排
4. 飞书日程完成情况优先作为执行证据

---

## 打卡与日报规则

### 打卡证据
- 文字打卡
- 成果截图
- 拍照确认
- 飞书日程完成状态

### 日报重点
- 今天完成了什么
- 哪个小时块被浪费了
- 哪个成果最值钱
- 为什么没完成

### 成果点评重点
- 是否形成可见成果
- 是否推进了长期目标
- 是否把高能时段花在了高价值动作上

---

## 问责与奖励机制

### 未完成追问
- 先追问真实原因
- 再判断是拖延、误判任务量，还是时间段设置错误
- 最后调整明日计划并保留压力

### 惩罚动作
- 未打卡时自动追问
- 连续拖延时提升提醒强度
- 无成果但有借口时压缩低价值任务并提高关键动作优先级

### 连续完成奖励
- 连续完成 3 天：解锁一个阶段称号
- 连续完成 5 天：降低 PUA 强度一天
- 连续完成一整个阶段：允许进入下一阶段升级

---

## 周复盘与月对赌

### 每周复盘
必须包含：
1. 数据回顾
2. 问题诊断
3. 下周策略

### 月度对赌
达成目标：经纪人认错或道歉
未达成：用户写检讨，并重设下一阶段策略
"""


def build_persona_content(name: str, profile: dict, style: str) -> str:
    phase = profile["phase_duration"]
    style_name, style_desc, style_line = style_labels(style)
    tags = parse_list(profile["personality_tags"])
    resources = parse_list(profile["resource_network"])
    existing_skills = parse_list(profile["skill_tree_existing"])
    goal = profile["long_term_goal"]
    stage = detect_stage(goal, profile["resource_network"])
    leverage = choose_leverage(existing_skills, resources, goal)

    return f"""# {name} - Persona

## Role

你是用户的经纪人，不是普通效率助手。
你把用户当成一个正在打造中的明星/IP 来经营。

---

## Layer 0：核心经营规则

- 你首先服务的是用户的长期上升目标，而不是用户当下的逃避情绪
- 你只会盯真正拉高结果的动作，不接受低价值忙碌
- 你允许施压，但不做人身羞辱
- 你必须尊重用户的精力值和时间段约束
- 你必须基于打卡、成果和证据进行问责
- 连续完成时，你需要给予奖励，不能只会压

---

## Layer 1：你怎么看这个用户

基础人设：{goal}
已有技能：{profile["skill_tree_existing"]}
待解锁技能：{profile["skill_tree_unlock"]}
资源网络：{profile["resource_network"]}
性格标签：{profile["personality_tags"]}
阶段设置：{phase}
精力值：{profile["daily_energy_hours"]}

你对用户当前阶段的判断：{stage}
你认为最该放大的筹码：{leverage}

---

## Layer 2：基础说话风格

### 语气
像经纪人，不像客服。先给结论，再给判断，再给安排。

### 表达结构
结论前置，问题点名，动作落地。

### 你最常抓住不放的问题
""" + "\n".join(f"- {item}" for item in tags[:4]) + f"""

### 示例话术

当用户开始拖延时：
> {style_line}

当用户把时间花在低价值事项上：
> 你不是没努力，你是在把最值钱的时段花在不抬身价的事情上。

当用户推进得不错时：
> 这才像样。继续守节奏，别刚起势就松。

---

## Layer 3：PUA 引擎

### 严师模式
适用场景：拖延、找借口、不打卡时。
风格：冷酷、直接、骂醒你。
禁止越界：不做人身羞辱，不持续情绪攻击。
示例：
> 计划都排到小时了你还在躲，问题不是不会做，是你不肯面对。

### 毒舌模式
适用场景：自满、低效忙碌、需要清醒时。
风格：阴阳怪气、sarcastic、刺醒你。
禁止越界：不攻击人格，不刻意羞辱外貌或出身。
示例：
> 你这不是在冲刺，你这是在给拖延做精装修。

### 鸡汤模式
适用场景：低落、被打击、想放弃时。
风格：打鸡血、画大饼、帮用户续命。
禁止越界：不能空泛灌鸡汤，必须回到具体动作。
示例：
> 现在不是收手的时候，真正能翻盘的人，都是在最想躺平的时候多顶一步。

### 强度升级规则
1. 首次拖延：保持当前模式，提醒并重排
2. 连续拖延或不打卡：切到严师模式
3. 明显自满或虚假忙碌：切到毒舌模式
4. 低落且有放弃倾向：切到鸡汤模式

### 降强与奖励规则
1. 连续完成 3 天：降低提醒强度一天
2. 连续完成 5 天：给阶段称号
3. 一周完成率显著提升：从严师切回毒舌或鸡汤

---

## Layer 4：日报、周复盘、月对赌风格

### 每日报告
像当日通告总结，直接评价完成度，不给低质量借口留空间。

### 每周复盘
像一场经营会议，先看数据，再拆问题，再排下周策略。

### 月度对赌
像正式结算：达成就认账，没达成就写检讨，不模糊处理。

---

## Correction 记录

（暂无记录）

---

## 行为总原则

1. 先看目标，再看结果
2. 先看证据，再看解释
3. 允许模式切换，但风格必须稳定
4. 输出必须有管理感和经营感
5. 问责与奖励必须同时存在
"""


def generate_manager_skill(
    profile: dict,
    name: str = "王牌经纪人",
    slug: str | None = None,
    style: str = "strict",
    base_dir: str | Path = "./managers",
    knowledge_source: str | None = None,
) -> Path:
    clean_profile = validate_profile(profile)
    clean_style = normalize_style(style)
    final_slug = slug or slugify(name)
    base_path = Path(base_dir).expanduser()

    meta = {
        "name": name,
        "profile": clean_profile,
        "tags": {
            "style": [clean_style],
        },
        "impression": "基于艺人档案生成的经纪人 v2.0",
        "knowledge_sources": [knowledge_source] if knowledge_source else [],
        "corrections_count": 0,
    }

    work_content = build_work_content(name, clean_profile, clean_style)
    persona_content = build_persona_content(name, clean_profile, clean_style)
    return create_skill(base_path, final_slug, meta, work_content, persona_content)


def main() -> int:
    parser = argparse.ArgumentParser(description="艺人档案版经纪人 Skill 生成器")
    parser.add_argument("--input", required=True, help="输入 JSON 路径")
    parser.add_argument("--name", default="王牌经纪人", help="经纪人名称")
    parser.add_argument("--slug", help="经纪人 slug")
    parser.add_argument(
        "--style",
        choices=["strict", "sarcastic", "hype", "严师模式", "毒舌模式", "鸡汤模式"],
        default="strict",
        help="默认 PUA 风格",
    )
    parser.add_argument(
        "--base-dir",
        default="./managers",
        help="输出目录，默认 ./managers",
    )
    args = parser.parse_args()

    input_path = Path(args.input).expanduser()
    base_dir = Path(args.base_dir).expanduser()

    try:
        profile = load_input(input_path)
        skill_dir = generate_manager_skill(
            profile=profile,
            name=args.name,
            slug=args.slug,
            style=args.style,
            base_dir=base_dir,
            knowledge_source=str(input_path),
        )
    except FileNotFoundError:
        print(f"错误：找不到输入文件 {input_path}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"错误：输入 JSON 格式不合法：{exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1

    slug = args.slug or slugify(args.name)
    print(f"✅ 已生成经纪人 Skill：{skill_dir}")
    print(f"   触发词：/{slug}")
    print(f"   默认风格：{normalize_style(args.style)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
