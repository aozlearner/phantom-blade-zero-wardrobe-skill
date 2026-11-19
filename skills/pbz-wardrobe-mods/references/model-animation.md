# 模型、动作与附件

## 从原生装配取证

优先查看已有 asset registry、mesh details、CDO、SCS component templates 和继承覆盖扫描。每个候选记录：

```text
key / outfitId / name / phase
body / head / skeleton / nativeClass
bodyMaterials[] / headMaterials[]
clothParts[] / grooms[{asset,binding}] / extraParts[] / staticParts[]
hideBones[] / scale / floorOffset / portrait / voiceProfile
```

分别确认骨骼名与父节点、必要手脚骨、材质槽顺序、原生组件覆盖、Groom Binding 的目标头模型、衣料配套骨架。头和头发可能是独立 SkeletalMesh、Groom 或 ChaosCloth；头部也可能已合并在 body。`head:null` 应走一体模型分支。

资源默认材质可能是占位网格；CDO 的实际覆盖优先。没有 CDO 证据时，用纹理槽/同角色材料/渲染证明替代关系，不能随便填一个能加载的材质。离线资料不足才补运行扫描；多角色合并扫描。

## 保留原骨架，叠加私有视觉层

成熟实现的组成是：

1. 隐藏但继续更新的原主角 body/head，仍承担移动、胶囊、武器与动画驱动。
2. 独立的主角参考姿势组件，用于取得参考姿势，不跟随当前动画。
3. 角色自己的比例姿势 `Proportions` ABP，及可见身体 `Grip` ABP。
4. 必要时使用独立 `Head` / `HeadFacial` ABP；衣料、Groom、附件挂在对应的可见部件上。

核心是把**主角相对参考姿势的运动变化**应用到目标角色自己的参考姿势；不是把主角绝对骨骼坐标直接复制成目标骨架。不同角色的肩宽、臂长和颈部比例因此得以保留。

从当前验证过的角色族克隆完整模块及 ABP 依赖，替换明确的包名、类名、Skeleton 引用与资源配置。只改名字不等于完成重定向；旧 ABP 的骨架、CopyPose 来源和所有引用仍要核对。复制时清除模板角色专有的背饰、待机让位或比例补偿，除非已重新测量证明适用。

武器握持在私有可见骨架上对齐主角手腕/肘部，按握持、松手、影兵/闪现窗口平滑混合；指尖、手掌、扭转骨、肩锁骨不能用同一个开关粗暴处理。复用已验证的限伸长与自由肩算法，不把旧角色测得的距离当成通用常数。

## 更新顺序与头身分离

- 创建对象后先登记到 `state.created`，后续任何加载失败均能清理。
- 私有组件无碰撞、无 overlap、无独立 ragdoll；原主角物理与控制保留。
- `AddTickPrerequisiteComponent` 排清 body、参考姿势、比例姿势、头和附件的先后顺序；隐藏驱动仍需刷新骨骼。
- Puerts 动画节点只写必要的暴露字段，不整块覆盖带原生缓存的 AnimNode 结构。使用游戏线程回调的私有实例禁用多线程动画更新。
- 换装、预览重建或过场可能换掉 AnimInstance：检测实例变化，重新绑定 CopyPose 来源。
- 独立头应跟随**目标身体的已重定向姿势**。原主角头存在独立面部曲线时用对应 Facial 分支；原头本身是 leader follower 时走无独立脸曲线分支。按角色的 DNA/后处理需要验证，不能一律开或关所有后处理。

`SetLeaderPoseComponent` 适用于确认兼容的骨骼布局。额外骨骼、骨序或 LOD 不匹配时，改用自己的 CopyPose ABP 保留附件原生骨骼。虎炮雷当的炮臂曾用这种方式修复；“复制全体骨骼”并不自动证明战斗中不会分离。

## 缩放与附件挂点

统一缩放整个私有角色装配，包括头和衣料；不缩放原主角胶囊或武器。优先测量注册后的参考姿势头/脚高度，单靠 bounds 可能把武器、坐骑或第二个人一起算进去。约 180 cm 的头骨高度是此项目的一种取景参考，不是所有角色的硬性身高。

配件按类型处理：

- StaticMesh：确认 socket、相对位置/旋转/缩放，再挂接。
- 骨骼附件：先检查父链，选择兼容 leader 或独立 CopyPose。
- 根节点上的特殊头饰：仅向下平移无法解决随头运动问题。舞狮二阶段的 `LionDanceHead` 原来挂在 `Root`，已用私有 PoseableMesh 保留狮头分支、隐藏其余分支，并挂到可见 body 的 `Head`；原 body 隐藏重复狮头。
- 上述 Poseable 做法已验证 `SetSkinnedAssetAndUpdate`、`SetBoneTransformByName(..., EBoneSpaces.ComponentSpace)`；挂点旋转需要抵消原参考 Head 朝向，相对偏移必须转换到 Head 局部空间。读取 `lion-fit.json` 的测量过程，别把该角色的数值套到其他头饰。附件子骨的原生旋转应保留。
- 隐藏分支用 `IsBoneHiddenByName` 加实际渲染确认。`GetSocketTransform().Scale3D` 不一定反映渲染层的隐藏状态，曾造成锯者分支“未隐藏”的误报。
- 合体模型先找独立资源。力者的合体资源可隐藏 `pelvis001` 锯者分支并仅保留自己的衣料；锯者另用独立模型。不能仅隐藏力者就假设锯者的 `...001` 骨链会自动获得主角动画。

## 清理

取消定时器/回调、移除私有 AnimInstance 映射，按子组件到父组件顺序销毁外观对象，再恢复自己记录的原始可见性和 tick 状态。对象失效、换 Pawn、回标题、切回原衣装都走相同的幂等清理路径。不要恢复不属于本模块的临时特效或武器状态。
