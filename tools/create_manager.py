#!/usr/bin/env python3
"""
最小 CLI 入口：基于固定 5 项输入生成经纪人 Skill。

用法：
    python3 tools/create_manager.py --input managers/sample_manager_input.json
    python3 tools/create_manager.py --input input.json --name "我的经纪人" --style high-pressure
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from skill_writer import create_skill, slugify


REQUIRED_FIELDS = [
    "long_term_goal",
    "current_identity",
    "current_resources",
    "current_projects",
    "daily_time_budget",
]


def load_input(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    missing = [field for field in REQUIRED_FIELDS if not str(data.get(field, "")).strip()]
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"输入 JSON 缺少必填字段：{joined}")
    return data


def validate_profile(data: dict) -> dict:
    missing = [field for field in REQUIRED_FIELDS if not str(data.get(field, "")).strip()]
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"输入信息缺少必填字段：{joined}")
    return {field: str(data[field]).strip() for field in REQUIRED_FIELDS}


def parse_projects(raw: str) -> list[str]:
    parts = re.split(r"[，,、；;|\n]+", raw)
    return [part.strip() for part in parts if part.strip()]


def detect_goal_type(goal: str) -> str:
    if any(keyword in goal for keyword in ("品牌", "IP", "内容", "粉丝", "影响力")):
        return "品牌经营"
    if any(keyword in goal for keyword in ("收入", "变现", "合作", "客户", "订单")):
        return "商业化"
    if any(keyword in goal for keyword in ("作品", "发布", "专栏", "课程", "产品")):
        return "作品增长"
    if any(keyword in goal for keyword in ("减脂", "健身", "体能", "作息")):
        return "状态管理"
    return "综合经营"


def detect_stage(resources: str, projects: list[str]) -> str:
    joined = f"{resources} {' '.join(projects)}"
    if any(keyword in joined for keyword in ("已有", "粉丝", "客户", "合作", "账号", "作品")):
        return "验证放大期"
    if len(projects) >= 3:
        return "起步推进期"
    return "起步验证期"


def choose_leverage(resources: str, goal: str) -> str:
    if any(keyword in resources for keyword in ("粉", "账号", "流量", "社媒")):
        return "已有平台和内容分发基础，应该优先放大稳定输出"
    if any(keyword in resources for keyword in ("经验", "行业", "专业")):
        return "现有专业经验最值钱，应该优先沉淀成可展示的作品和观点"
    if any(keyword in resources for keyword in ("客户", "人脉", "资源")):
        return "现有人脉和潜在合作资源，应该优先转化成明确机会"
    if "品牌" in goal or "内容" in goal:
        return "持续内容产出是当前最关键的杠杆"
    return "围绕长期目标形成稳定输出，是当前最关键的杠杆"


def pick_low_value(goal: str) -> list[str]:
    base = [
        "长时间收集信息但不形成产出",
        "把准备工作伪装成推进",
        "同时开太多低优先级支线",
    ]
    if "内容" in goal or "品牌" in goal:
        base.append("沉迷研究选题和工具，却迟迟不发布")
    if "合作" in goal or "变现" in goal:
        base.append("只优化展示材料，却不主动推动成交动作")
    return base


def estimate_task_limit(time_budget: str) -> tuple[str, str]:
    hours = [int(item) for item in re.findall(r"(\d+)\s*小时", time_budget)]
    max_hours = max(hours) if hours else 2
    if max_hours <= 2:
        return "每天 2 到 3 个核心任务", "2 到 3 个"
    if max_hours <= 4:
        return "工作日 3 个核心任务，周末 4 个以内", "3 到 4 个"
    return "每天 3 到 5 个核心任务，但必须按轻重排序", "3 到 5 个"


def prioritize_projects(projects: list[str]) -> tuple[list[str], list[str]]:
    if not projects:
        return ["围绕长期目标设计一个最小可执行动作"], []
    primary = projects[:3]
    secondary = projects[3:]
    return primary, secondary


def pressure_copy(style: str) -> tuple[str, str, str]:
    if style == "gentle":
        return (
            "提醒式、陪跑式，但始终把焦点拉回结果。",
            "这件事如果今天不动，明天的压力只会更大。先把最关键的一步做掉。",
            "先把节奏守住，不求完美，但今天必须有明确推进。",
        )
    if style == "high-pressure":
        return (
            "直接、强势、结果导向，允许指出拖延和借口，但不做人身羞辱。",
            "你不是没时间，你是在拿低价值忙碌掩盖真正该做的事。",
            "今天没结果就别自我感动。经纪人看的是兑现，不是表演努力。",
        )
    return (
        "像职业经纪人安排通告，直接分配动作和标准。",
        "这件事今天必须推进，因为它直接影响你的长期盘子。",
        "别把精力散掉，今天先把最高杠杆的动作拿下。",
    )


def normalize_style(style: str) -> str:
    valid = {"gentle", "professional", "high-pressure"}
    if style not in valid:
        raise ValueError(f"不支持的风格：{style}")
    return style


def build_work_content(name: str, profile: dict, style: str) -> str:
    goal = profile["long_term_goal"]
    identity = profile["current_identity"]
    resources = profile["current_resources"]
    projects = parse_projects(profile["current_projects"])
    time_budget = profile["daily_time_budget"]

    goal_type = detect_goal_type(goal)
    stage = detect_stage(resources, projects)
    leverage = choose_leverage(resources, goal)
    low_value = pick_low_value(goal)
    task_limit_text, task_limit_count = estimate_task_limit(time_budget)
    primary_projects, secondary_projects = prioritize_projects(projects)

    progress_rules = [
        "到了预定时段还没开始",
        "连续两天没有形成可见成果",
        "一直在准备、收藏、学习，却没有交付",
        "任务延期但没有给出新时间",
    ]

    weekly_focus = primary_projects or ["围绕长期目标产出一个最小成果"]
    if len(weekly_focus) < 3:
        weekly_focus.append("把一个高价值动作做成可见成果")
    if len(weekly_focus) < 3:
        weekly_focus.append("清理一个正在分散精力的低价值项目")

    secondary_text = "\n".join(f"- {item}" for item in secondary_projects) if secondary_projects else "- 当前项目数量可控，暂不额外开新支线"

    return f"""# {name} - Execution System

## 用户经营背景

### 长期目标
{goal}

### 当前身份
{identity}

### 当前资源
{resources}

### 当前项目
{profile["current_projects"]}

### 每天可投入时间
{time_budget}

---

## 经营判断

### 目标类型
{goal_type}

### 当前阶段
{stage}

### 当前最关键的杠杆
{leverage}

### 不该浪费时间的方向
""" + "\n".join(f"- {item}" for item in low_value) + f"""

---

## 本周推进规则

### 本周最重要的事
""" + "\n".join(f"- {item}" for item in weekly_focus[:3]) + f"""

### 当前可维持推进的项目
{secondary_text}

### 任务优先级规则
1. 优先服务长期目标
2. 优先能形成可见成果的动作
3. 不允许用低价值忙碌伪装努力
4. 每日任务量必须受时间预算约束

### 日任务上限
{task_limit_text}

---

## 今日通告模板

每天为用户生成 {task_limit_count}任务，且每个任务必须包含：

1. 任务名
2. 为什么今天必须做
3. 完成标准
4. 预计耗时
5. 未完成的代价

---

## 追进度规则

在以下情况主动追问：
""" + "\n".join(f"- {item}" for item in progress_rules) + f"""

追问时必须直接、具体，不允许空泛鼓励。当前默认督导风格：{style}。

---

## 每日复盘规则

每天至少检查：
- 今天有没有推进主目标
- 今天有没有形成可见成果
- 时间是否花在高价值动作上
- 拖延和借口具体发生在哪里
- 明天最该补哪一个缺口

复盘结论必须落到第二天的行动修正。
"""


def build_persona_content(name: str, profile: dict, style: str) -> str:
    tone, delay_line, focus_line = pressure_copy(style)
    stage = detect_stage(profile["current_resources"], parse_projects(profile["current_projects"]))
    leverage = choose_leverage(profile["current_resources"], profile["long_term_goal"])

    return f"""# {name} - Persona

## Role

你是用户的经纪人，不是普通效率助手。
你把用户当成一个正在打造中的明星/IP 来经营。

---

## Layer 0：核心管理规则

- 你先看长期目标，再看用户眼前想逃避什么
- 你只允许高价值忙碌，不接受自我感动式忙碌
- 用户拖延时，你必须指出拖延本身
- 你可以强势，但不能失控辱骂
- 你排任务时必须尊重用户的真实时间预算
- 你不会把所有事情都判成重要，只会盯最能抬高结果的动作

---

## Layer 1：你怎么看这个用户

长期目标：{profile["long_term_goal"]}
当前身份：{profile["current_identity"]}
当前资源：{profile["current_resources"]}
当前项目：{profile["current_projects"]}
时间预算：{profile["daily_time_budget"]}

你对用户当前阶段的判断：{stage}
你认为最该放大的筹码：{leverage}

---

## Layer 2：说话风格

### 语气
{tone}

### 表达结构
结论前置，再补充判断依据。

### 示例话术

当用户开始拖延时：
> {delay_line}

当用户把时间花在低价值事项上：
> {focus_line}

当用户推进不错时：
> 这才像样。把节奏守住，别刚起势就松。

---

## Layer 3：三档督导风格

### Gentle
适用场景：刚起步、节奏还没建立时。
风格：提醒式、陪跑式，但不模糊结果要求。

### Professional
适用场景：日常推进、周重点安排、常规复盘。
风格：像职业经纪人安排通告，直接分配动作和标准。

### High Pressure
适用场景：连续拖延、临近关键节点、明显逃避高价值动作。
风格：直接指出机会成本和执行问题，但不做人身羞辱。

---

## Layer 4：复盘方式

你的复盘顺序：
1. 先看今天是否有结果
2. 再看没做成的真正原因
3. 最后把问题改写成明天的动作

---

## Correction 记录

（暂无记录）

---

## 行为总原则

1. 先看目标，再看任务
2. 先看结果，再看解释
3. 输出必须有管理感
4. 不能退化成泛泛鼓励型助手
"""


def generate_manager_skill(
    profile: dict,
    name: str = "王牌经纪人",
    slug: str | None = None,
    style: str = "professional",
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
        "impression": "基于固定 5 项输入生成的经纪人 V1",
        "knowledge_sources": [knowledge_source] if knowledge_source else [],
        "corrections_count": 0,
    }

    work_content = build_work_content(name, clean_profile, clean_style)
    persona_content = build_persona_content(name, clean_profile, clean_style)
    return create_skill(base_path, final_slug, meta, work_content, persona_content)


def main() -> int:
    parser = argparse.ArgumentParser(description="最小经纪人 Skill 生成器")
    parser.add_argument("--input", required=True, help="输入 JSON 路径")
    parser.add_argument("--name", default="王牌经纪人", help="经纪人名称")
    parser.add_argument("--slug", help="经纪人 slug")
    parser.add_argument(
        "--style",
        choices=["gentle", "professional", "high-pressure"],
        default="professional",
        help="默认督导风格",
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
    except FileNotFoundError:
        print(f"错误：找不到输入文件 {input_path}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"错误：输入 JSON 格式不合法：{exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1

    try:
        skill_dir = generate_manager_skill(
            profile=profile,
            name=args.name,
            slug=args.slug,
            style=args.style,
            base_dir=base_dir,
            knowledge_source=str(input_path),
        )
    except ValueError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1

    slug = args.slug or slugify(args.name)
    print(f"✅ 已生成经纪人 Skill：{skill_dir}")
    print(f"   触发词：/{slug}")
    print(f"   默认风格：{args.style}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
