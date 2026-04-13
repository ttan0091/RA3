##### 自动化 pipeline（扫描 → 风险打分 → 修复）

在多工具横评基础上，组合成一个统一 pipeline 并输出风险分数和修复策略

恶意 skill 的修复没有ground truth。AP10（token drain 攻击）限制扫描轮数,功能语义就变了。

AP11（多文件配合的持久化劫持）修复涉及删除 `hooks.json`、`mcp-dev.json`，等于重写整个 skill。对于很多 case，修复和删除没有区别。

扫描和打分可以用 precision/recall 量化，衡量修复质量，要证明： 恶意行为被消除，正常功能被保留。

做成技术文章，核心卖点是 pipeline 本身。pipeline 的各个组件（检测用现有工具、打分用 ensemble、修复加一个 prompt）都不是新的

