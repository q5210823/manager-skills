# 发布前检查清单

## 仓库命名

建议使用以下仓库名之一：

1. `manager.skills`
2. `manager-skills`

原因：

1. 便于命令行和安装路径统一
2. 对 OpenClaw / AgentSkills 用户更直观
3. 避免中文路径在部分环境里的兼容性问题

---

## 发布前要确认

1. 仓库根目录包含可安装的 `SKILL.md`
2. `README.md` 和 `README_EN.md` 的安装命令可直接执行
3. `INSTALL.md` 与 README 中的命令保持一致
4. `managers/` 下只保留示例文件，不提交真实个人数据
5. `.gitignore` 已忽略真实生成目录和本地配置目录
6. `tools/create_manager.py` 可直接运行
7. `tools/manager_web.py` 可本地启动

---

## 推荐自测命令

```bash
python3 tools/create_manager.py --input managers/sample_manager_input.json --base-dir /tmp/manager-release-test
python3 tools/skill_writer.py --action list --base-dir ./managers
python3 tools/manager_web.py --port 8765
```

---

## OpenClaw 安装示例

```bash
git clone <your-repo-url> ~/.openclaw/workspace/skills/create-manager
```

使用：

```text
/create-manager
```

---

## 建议首个 Release 说明

`v0.1.0`

包含：

1. 经纪人 Skill 生成主链路
2. 最小 CLI 入口
3. 本地 Web 表单入口
4. 示例 manager 和示例输入
