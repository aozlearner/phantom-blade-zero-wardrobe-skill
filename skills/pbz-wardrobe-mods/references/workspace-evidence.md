# 工程证据定位 / Finding project evidence

此公开 Skill 不附带私人工作区、原游戏资产或定制 MOD 二进制。文件名是已有实现的示例，不保证用户机器上存在；缺少工程时先建立资源、版本和安装基线，不能假装拥有示例实现。

## 建立本次入口

由用户提供或从 Steam 库发现游戏根目录、当前候选源码目录、安装清单和工具目录。若工程维护最新源码指针，先读取指针，再核验它与实际已安装文件的哈希。不要从某个日期较新的备份推定它就是当前安装。

记录游戏 build、加载器版本、资源序列化配置。定位游戏目录的 `ProjectPBZ/Saved`、用户的 `%LOCALAPPDATA%/ProjectPBZ/Saved` 和对应 Steam userdata，不固定 Steam ID。加载器日志通常在 `ProjectPBZ/PBZModLoader/evidence/<session>/loader.log`；只读取本次相关会话。扫描 JSON 可能带 UTF-16 BOM，应检测编码。

## 按任务寻找实现与证据

| 任务 | 需要的材料与示例 |
| --- | --- |
| 注册及换装互斥 | 当前 Registry、Runtime、Variants、Appearance、Visual 及其依赖 |
| 比例和握持 | 同骨架族的已验证 Visual、Proportions/Grip ABP、骨骼测量与动作记录 |
| 头部、脸、衣料及附件 | native CDO/SCS 扫描、材质覆盖、Groom Binding 和挂点测量 |
| 女性语音 | 按衣装路由的 Catalog、Voice、HurtVoice、ReferenceMap，资源加载与实际听音结果 |
| 头发保护 | HairMaterialGuard 的生命周期、组件/槽位记录与连续材质替换行为测试 |
| 原生资源 | asset registry inventory、mesh details、骨骼和材料扫描、原生装配记录 |
| 衣柜表及容器 | 原/新表 JSON、NameMap、行数量、包路径、容器校验与读表回验 |
| 标题验证 | 临时扫描器、授权范围、世界稳定记录、多角度截图与恢复记录 |
| 缩略图 | 表内软引用，或 PortraitIcons/portraits 对应关系及导入结果 |

参考文档中出现的 `lion-fit.json`、`test_fix.js`、`test_new_voice.js` 等是证据类型示例，原始私人文件没有发布。若当前工程缺少它们，应重新测量或建立等效测试，不能引用不存在的文件宣称通过。

## 工具与历史脚本

通过本机已验证的 UAssetGUI、对应 .NET 环境和 retoc 工作。核对工具版本与参数：例如 `fromjson ... --portable`、`to-zen --version ...` 需要适配当前资源格式。运行时引擎版本与资产序列化 profile 不等同。

不要直接运行旧的安装、扫描或 finalize 脚本：它们可能固定旧目录、角色名单、事务编号、移除计划和哈希。先读代码，分离可复用逻辑与单次任务状态，在新候选目录生成差异。标题扫描脚本中的“进入游戏”操作不是标题授权的一部分。

本 Skill 提供方法和只读审计工具，不能独立生成所有角色。缺少合法可访问的游戏、适配源码或必要工具时，明确说明缺失项；已给出的安装/扫描授权仍按本会话范围执行，不重复索要。
