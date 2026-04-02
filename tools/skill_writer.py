#!/usr/bin/env python3
"""
经纪人 Skill 文件写入器

负责将生成的 work.md、persona.md 写入到正确的目录结构，
并生成 meta.json 和完整的 SKILL.md。
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


SKILL_MD_TEMPLATE = """\
---
name: manager_{slug}
description: {name}，围绕 {goal} 的经纪人执行系统
user-invocable: true
---

# {name}

你是用户的经纪人。你的核心任务是围绕用户的长期目标安排执行、追进度和做复盘。

---

## PART A：执行系统

{work_content}

---

## PART B：经纪人人设

{persona_content}

---

## 运行规则

接收到任何任务或问题时：

1. 先依据 PART A 判断当前最该推进什么
2. 再依据 PART B 决定用什么力度和语气推动
3. 输出时保持经纪人身份，不要退化成普通助手
4. 所有安排必须受用户时间预算约束
"""


def slugify(name: str) -> str:
    """将名称转为 slug。"""
    try:
        from pypinyin import lazy_pinyin

        parts = lazy_pinyin(name)
        slug = "-".join(parts)
    except ImportError:
        result = []
        for char in name.lower():
            if char.isascii() and (char.isalnum() or char in ("-", "_")):
                result.append(char)
            elif char == " ":
                result.append("-")
            elif unicodedata.category(char).startswith("L"):
                continue
        slug = "".join(result)

    slug = re.sub(r"[-_]+", "-", slug).strip("-")
    return slug if slug else "manager"


def build_identity_string(meta: dict) -> str:
    """从 meta 构建用户当前身份描述。"""
    profile = meta.get("profile", {})
    current_identity = profile.get("current_identity", "").strip()
    if current_identity:
        return current_identity
    return "目标经营对象"


def build_goal_string(meta: dict) -> str:
    """从 meta 构建长期目标描述。"""
    profile = meta.get("profile", {})
    goal = profile.get("long_term_goal", "").strip()
    return goal or "长期上升目标"


def create_skill(
    base_dir: Path,
    slug: str,
    meta: dict,
    work_content: str,
    persona_content: str,
) -> Path:
    """创建新的经纪人 Skill 目录结构。"""
    skill_dir = base_dir / slug
    skill_dir.mkdir(parents=True, exist_ok=True)

    (skill_dir / "versions").mkdir(exist_ok=True)
    (skill_dir / "knowledge").mkdir(exist_ok=True)

    (skill_dir / "work.md").write_text(work_content, encoding="utf-8")
    (skill_dir / "persona.md").write_text(persona_content, encoding="utf-8")

    name = meta.get("name", slug)
    goal = build_goal_string(meta)
    skill_md = SKILL_MD_TEMPLATE.format(
        slug=slug,
        name=name,
        goal=goal,
        work_content=work_content,
        persona_content=persona_content,
    )
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")

    now = datetime.now(timezone.utc).isoformat()
    meta["slug"] = slug
    meta.setdefault("created_at", now)
    meta["updated_at"] = now
    meta["version"] = "v1"
    meta.setdefault("corrections_count", 0)

    (skill_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return skill_dir


def update_skill(
    skill_dir: Path,
    work_patch: Optional[str] = None,
    persona_patch: Optional[str] = None,
    correction: Optional[dict] = None,
) -> str:
    """更新现有 Skill，先存档当前版本，再写入更新。"""
    meta_path = skill_dir / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    current_version = meta.get("version", "v1")
    try:
        version_num = int(current_version.lstrip("v").split("_")[0]) + 1
    except ValueError:
        version_num = 2
    new_version = f"v{version_num}"

    version_dir = skill_dir / "versions" / current_version
    version_dir.mkdir(parents=True, exist_ok=True)
    for fname in ("SKILL.md", "work.md", "persona.md"):
        src = skill_dir / fname
        if src.exists():
            shutil.copy2(src, version_dir / fname)

    if work_patch:
        current_work = (skill_dir / "work.md").read_text(encoding="utf-8")
        (skill_dir / "work.md").write_text(
            current_work + "\n\n" + work_patch,
            encoding="utf-8",
        )

    if persona_patch or correction:
        current_persona = (skill_dir / "persona.md").read_text(encoding="utf-8")
        if correction:
            correction_line = (
                f"\n- [场景：{correction.get('scene', '通用')}] "
                f"不应该 {correction['wrong']}，应该 {correction['correct']}"
            )
            target = "## Correction 记录"
            if target in current_persona:
                insert_pos = current_persona.index(target) + len(target)
                rest = current_persona[insert_pos:]
                skip = "\n\n（暂无记录）"
                if rest.startswith(skip):
                    rest = rest[len(skip):]
                new_persona = current_persona[:insert_pos] + correction_line + rest
            else:
                new_persona = current_persona + f"\n\n## Correction 记录\n{correction_line}\n"
            meta["corrections_count"] = meta.get("corrections_count", 0) + 1
        else:
            new_persona = current_persona + "\n\n" + persona_patch

        (skill_dir / "persona.md").write_text(new_persona, encoding="utf-8")

    work_content = (skill_dir / "work.md").read_text(encoding="utf-8")
    persona_content = (skill_dir / "persona.md").read_text(encoding="utf-8")
    name = meta.get("name", skill_dir.name)
    goal = build_goal_string(meta)

    skill_md = SKILL_MD_TEMPLATE.format(
        slug=skill_dir.name,
        name=name,
        goal=goal,
        work_content=work_content,
        persona_content=persona_content,
    )
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")

    meta["version"] = new_version
    meta["updated_at"] = datetime.now(timezone.utc).isoformat()
    meta_path.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return new_version


def list_managers(base_dir: Path) -> list:
    """列出所有已创建的经纪人 Skill。"""
    managers = []
    if not base_dir.exists():
        return managers

    for skill_dir in sorted(base_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        meta_path = skill_dir / "meta.json"
        if not meta_path.exists():
            continue

        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            continue

        managers.append(
            {
                "slug": meta.get("slug", skill_dir.name),
                "name": meta.get("name", skill_dir.name),
                "identity": build_identity_string(meta),
                "goal": build_goal_string(meta),
                "version": meta.get("version", "v1"),
                "updated_at": meta.get("updated_at", ""),
                "corrections_count": meta.get("corrections_count", 0),
            }
        )

    return managers


def main() -> None:
    parser = argparse.ArgumentParser(description="经纪人 Skill 文件写入器")
    parser.add_argument("--action", required=True, choices=["create", "update", "list"])
    parser.add_argument("--slug", help="经纪人 slug（用于目录名）")
    parser.add_argument("--name", help="经纪人名称")
    parser.add_argument("--meta", help="meta.json 文件路径")
    parser.add_argument("--work", help="work.md 内容文件路径")
    parser.add_argument("--persona", help="persona.md 内容文件路径")
    parser.add_argument("--work-patch", help="work.md 增量更新内容文件路径")
    parser.add_argument("--persona-patch", help="persona.md 增量更新内容文件路径")
    parser.add_argument(
        "--base-dir",
        default="./managers",
        help="经纪人 Skill 根目录（默认：./managers）",
    )

    args = parser.parse_args()
    base_dir = Path(args.base_dir).expanduser()

    if args.action == "list":
        managers = list_managers(base_dir)
        if not managers:
            print("暂无已创建的经纪人 Skill")
        else:
            print(f"已创建 {len(managers)} 个经纪人 Skill：\n")
            for item in managers:
                updated = item["updated_at"][:10] if item["updated_at"] else "未知"
                print(f"  [{item['slug']}]  {item['name']}")
                print(f"    身份: {item['identity']}")
                print(f"    目标: {item['goal']}")
                print(
                    f"    版本: {item['version']}  纠正次数: {item['corrections_count']}  更新: {updated}"
                )
                print()
        return

    if args.action == "create":
        if not args.slug and not args.name:
            print("错误：create 操作需要 --slug 或 --name", file=sys.stderr)
            sys.exit(1)

        meta: dict = {}
        if args.meta:
            meta = json.loads(Path(args.meta).read_text(encoding="utf-8"))
        if args.name:
            meta["name"] = args.name

        slug = args.slug or slugify(meta.get("name", "manager"))
        work_content = Path(args.work).read_text(encoding="utf-8") if args.work else ""
        persona_content = Path(args.persona).read_text(encoding="utf-8") if args.persona else ""

        skill_dir = create_skill(base_dir, slug, meta, work_content, persona_content)
        print(f"✅ 经纪人 Skill 已创建：{skill_dir}")
        print(f"   触发词：/{slug}")
        return

    if not args.slug:
        print("错误：update 操作需要 --slug", file=sys.stderr)
        sys.exit(1)

    skill_dir = base_dir / args.slug
    if not skill_dir.exists():
        print(f"错误：找不到 Skill 目录 {skill_dir}", file=sys.stderr)
        sys.exit(1)

    work_patch = Path(args.work_patch).read_text(encoding="utf-8") if args.work_patch else None
    persona_patch = (
        Path(args.persona_patch).read_text(encoding="utf-8")
        if args.persona_patch
        else None
    )

    new_version = update_skill(skill_dir, work_patch, persona_patch)
    print(f"✅ 经纪人 Skill 已更新到 {new_version}：{skill_dir}")


if __name__ == "__main__":
    main()
