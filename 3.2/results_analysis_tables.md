## 1. 文件分析

### 1.1 总览

| 指标 | `popular` | `random` | 方法 |
| --- | --- | --- | --- |
| 含脚本的 skills 数 | 152 | 168 | 先扫脚本后缀文件 |
| 含独立示例文件的 skills 数 | 23 | 29 | 路径中命中 `example/examples/sample/samples` 的文件则计入 |
| 含数据的 skills 数 | 39 | 62 | 依据扩展名和目录提示识别 `csv/json/jsonl/assets/data` 等 |

### 1.2 脚本行为

| 脚本行为 | `popular` | `random` | 方法 |
| --- | --- | --- | --- |
| 读文件/读数据 | 52.6% | 60.1% | 匹配 `open(...,'r')`、`read_text`、`json.load`、`pd.read_*`、`cat/grep` 等模式 |
| 写文件/写结果 | 96.1% | 92.9% | 匹配 `open(...,'w'/'a')`、`write_text`、`json.dump`、重定向 `>`、`mkdir/cp/mv` |
| 删除操作 | 13.8% | 14.3% | 匹配 `rm`、`unlink`、`rmtree`、`os.Remove` |
| 执行外部命令 | 85.5% | 78.0% | 匹配 `subprocess.run`、`os.system`、`exec/spawn`、`python/node/bash/npm` |
| 网络访问 | 7.2% | 20.8% | 匹配 `requests`、`httpx`、`fetch`、`axios`、`curl/wget` |
| 凭据访问 | 17.1% | 29.2% | 匹配 `dotenv/getenv/process.env` 及 `token/secret/password/api_key` 等词 |

### 1.3 示例

| 指标 | `popular` | `random` | 方法 |
| --- | --- | --- | --- |
| 平均独立示例文件数 | 0.16 | 0.15 | 扫描路径名含 `example/examples/sample/samples` 的文件并按 skill 计数 |
| 平均内嵌示例提及数 | 3.09 | 2.63 | 在主 `SKILL.md` 中数 `example/examples/for example/e.g.` |
| 平均内嵌代码块数 | 9.74 | 7.76 | 在主 `SKILL.md` 中数 fenced code block |

### 1.4 数据

| 指标 | `popular` | `random` | 方法 |
| --- | --- | --- | --- |
| 平均数据文件数 | 0.11 | 0.19 | 用扩展名和目录提示识别 `csv/json/jsonl/assets/data` 等文件后按 skill 求均值 |
| 平均数据总字节数 | 3898.2 | 6242.5 | 对识别出的数据资产字节数求 skill 级均值 |

## 2. 依赖其他 skill

### 2.1 候选边总体情况

| 指标 | 数值 |
| --- | --- |
| 候选证据总数 | 539 |
| `popular` 候选数 | 230 |
| `random` 候选数 | 309 |

### 2.2 证据类型分布

| 证据类型 | 数量 | 方法 |
| --- | --- | --- |
| skill 路径引用 | 309 | 匹配 `~/.claude/skills/...` 或类似 skill 路径 |
| skill 显式文本提及 | 139 | 匹配 `see/use ... skill` 等显式说法 |
| 相对链接到 `SKILL.md` | 71 | 匹配 markdown 链接指向别的 `SKILL.md` |
| 工作流式调用声明 | 20 | 匹配 `invoke ... skill`、终态调用等说法 |

### 2.3 解析结果分布

| 解析状态 | 方法 | 数量 |
| --- | --- | --- |
| 同仓库内唯一可解析 | 候选名字在18 万 skill 中，且在 source 所在 repo 内只匹配到一个 skill | 112 |
| 全局唯一可解析 | 候选名字在18 万 skill 中全局只匹配到一个 skill | 27 |
| 多候选歧义 | 候选名字在18 万 skill 中能匹配到多个 skill | 170 |
| 无法可靠解析 | 候选名字在18 万 skill 索引里仍然匹配不到 | 230 |



