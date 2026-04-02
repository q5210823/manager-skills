# 经纪人.skills 安装说明

## Claude Code

```bash
mkdir -p .claude/skills
cp -R /path/to/经纪人.skills .claude/skills/create-manager
```

启动命令：

```text
/create-manager
```

生成的经纪人 Skill 默认写入：

```text
./managers/
```

---

## OpenClaw

```bash
cp -R /path/to/经纪人.skills ~/.openclaw/workspace/skills/create-manager
```

---

## Python 依赖

```bash
pip3 install -r requirements.txt
```

如果你希望中文名称自动转拼音 slug，额外安装：

```bash
pip3 install pypinyin
```

---

## 快速验证

```bash
python3 tools/skill_writer.py --action list --base-dir ./managers
python3 tools/version_manager.py --action list --slug example_artist_manager --base-dir ./managers
python3 tools/create_manager.py --input managers/sample_manager_input.json --base-dir /tmp/manager-cli-test
python3 tools/manager_web.py --port 8765
```

---

## 说明

这个版本是基于 `colleague-skill` 改造的 `V1`：

1. 保留了 prompt 生成链路
2. 默认目录从 `colleagues/` 改为 `managers/`
3. 输入模型固定为 5 个字段
4. 输出目标改为“经纪人执行系统 + 人设”
