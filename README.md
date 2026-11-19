# Phantom Blade Zero Wardrobe Skill

**影之刃零 / 影之刃0 独立衣柜角色 MOD 制作 Skill**

[English](README.en.md) · [Skill 入口](skills/pbz-wardrobe-mods/SKILL.md) · [MIT License](LICENSE)

面向 AI 编程 Agent 的《Phantom Blade Zero》（PBZ / ProjectPBZ）角色 MOD 制作与修复方法：保留主角动作和原衣装，将其他角色作为可切换的独立衣柜外观。

An agent skill for creating and repairing Phantom Blade Zero wardrobe character mods, with animation binding, outfit-scoped voices, hair-material protection, thumbnails, and backup-aware validation.

## 能做什么

- 模型绑定主角动作，处理头身跟随、比例、握持、衣料、头发和附件。
- 分衣装切换战斗语音：本人优先，缺失类别默认回退沐小葵；原衣装和剧情对白保留原声。
- 排查切武器、闪现后的红发或材质异常，约束材质恢复的组件范围与生命周期。
- 维护唯一衣柜 ID、单一合并表、互斥注册和换装清理，减少皮肤冲突。
- 配置原生缩略图或角色 PNG，并分别验证资源、装配、动作和实际游戏表现。
- 使用只读脚本审计候选文件与现有基线，发现漂移、遗漏和未知文件碰撞。

## 安装与使用

仓库中的 Skill 目录是 `skills/pbz-wardrobe-mods`。将**整个目录**复制到 Agent 支持的技能目录，保留 references、scripts 和 agents 子目录；例如 Codex 的技能根目录下应出现 `pbz-wardrobe-mods/SKILL.md`。已有同名 Skill 时先比较版本并备份，不直接覆盖个人定制。

也可让支持从 GitHub 安装 Skill 的 Agent 读取：

```text
仓库：https://github.com/aozlearner/phantom-blade-zero-wardrobe-skill
Skill 路径：skills/pbz-wardrobe-mods
```

调用示例：

```text
使用 $pbz-wardrobe-mods，为这个角色制作独立衣柜外观。
保留原版衣装和当前正常的 MOD，按衣装切换声音，先准备候选并验证。
我仍在游戏中，写入前等我保存退出。
```

详细工程参考以中文为主，英文使用说明见 English 页面。其他 Agent 也可以直接阅读 SKILL.md，无需依赖特定连接器。

## 输入与边界

需要用户本机合法可访问的游戏资源、当前适配工程/源码、加载器和对应资产工具。**这不是完整 MOD 下载包，也不是自动生成所有角色的一键程序。** 仓库不含模型、音频、存档、私人路径、认证信息或游戏二进制。

只读审计需要 Python 3.10+，使用标准库。候选应包含全部受管理文件；基线格式为 JSON 数组：

```json
[{"relative":"ProjectPBZ/PBZModLoader/mods/example/main.js","sha256":"文件的64位SHA256"}]
```

```powershell
python skills/pbz-wardrobe-mods/scripts/audit_stage.py --baseline baseline.json --game "D:\Games\PBZ" --stage "D:\ModWork\candidate" --report "D:\ModWork\audit.json"
```

退出码 0 表示文件基线审计通过，1 表示存在阻断项，2 表示输入无效。它不安装、不卸载，也不证明骨架或实战兼容。

## 独立项目

这个仓库讲“如何制作和修复”。另一个 [Phantom Blade Zero Modpack Deploy](https://github.com/aozlearner/phantom-blade-zero-modpack-deploy) 提供特定历史组合的安装、备份和回滚工程。两者无运行依赖，可分别使用。

## 验证与许可

```powershell
python -m unittest discover -s tests -v
```

MIT 许可适用于此仓库的说明和审计工具，不授予游戏或第三方 MOD 资产的使用/分发权。本项目为社区项目，与游戏开发商或发行商无隶属关系。
