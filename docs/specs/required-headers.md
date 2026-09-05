# Spec: Strict Header Schema Validation Mode — `required-headers` 规则

> 状态：已评审 · 切片 v1 · 2026-09-05
> 落点：`csvkit/cli.py` 的 `CSVKitUtility`
> 基线 commit：`ba8033d`

---

## 1. 问题陈述

当团队明确知道上游对账文件应包含哪些列时，应在**解析初始化阶段**就显式校验并给出可读错误，
而不是把问题拖到下游清算、报表逻辑中才爆炸。

## 2. 术语

| 术语 | 定义 |
| --- | --- |
| **表头行（header row）** | 跳过 `-K/--skip-lines` 指定行数后的第一行 |
| **必需列（required header）** | 用户通过 `--required-headers` 声明的、必须出现在表头行中的列名 |
| **缺失列（missing header）** | 声明为必需、但未出现在表头行中的列名 |

## 3. 用户接口

```
--required-headers COLUMNS
```

- 值为逗号分隔的列名字符串，例如 `--required-headers order_id,amount,currency`
- 定义在 `CSVKitUtility._init_common_parser()`，与 `-H/--no-header-row` 相邻
- **默认值为 `None`**——未传该选项时，csvkit 的行为与改动前**逐字节一致**

## 4. 规则

| 编号 | 规则 | 裁决 |
| --- | --- | --- |
| **R1** | 匹配方式 | **精确匹配，大小写敏感**。列名是上游契约，宽松匹配会掩盖变更 |
| **R2** | 空白处理 | 表头名与声明名**两侧 strip 后**比较。BOM/空格是真实对账文件的常态噪音 |
| **R3** | 多列缺失 | **一次全部报出**，顺序按 `--required-headers` 中的**声明顺序**（不是表头顺序、不排序）。顺序确定是 Approved Scenarios 能稳定 diff 的前提 |
| **R4** | 错误形态 | 抛 `MissingRequiredHeadersError`（新增，继承既有 `CustomException`），走 csvkit 既有 `_install_exception_handler`。**退出码 1**，stderr 输出：<br>`MissingRequiredHeadersError: Missing required header(s): currency, region` |
| **R5** | 与 `-H/--no-header-row` 同传 | **报错退出**：`--required-headers cannot be used with --no-header-row.`。无表头时列名是合成的 `a,b,c`，与"必需列"逻辑矛盾，静默忽略是最坏选项 |
| **R6** | 多余列 | **允许通过**。`allow-unknown-headers` 是独立规则，属非目标 |
| **R7** | 重复列名 | **算通过**（存在即可）。重复列检测是 `csvclean` 的职责 |
| **R8** | 空输入文件 | **跳过校验**，行为不变。`get_rows_and_column_names_and_column_ids()` 在 `StopIteration` 时提前返回 `[], [], []`，永远到不了校验点。<br>**这条是硬约束**：`EmptyFileTests` 被混入 13 个测试类，破坏它等于破坏整个回归网 |

## 5. 覆盖范围（诚实收口）

csvkit **不存在**单一的 header 解析收敛点。本切片只覆盖走公共方法
`CSVKitUtility.get_rows_and_column_names_and_column_ids()` 的命令：

| 状态 | 命令 |
| --- | --- |
| ✅ **本切片覆盖** | `csvcut`、`csvgrep` |
| ⛔ **明确非目标** | `csvclean`、`csvformat`、`csvjson`、`csvlook`、`csvsort`、`csvstat`、`csvsql`、`csvjoin`、`csvstack`、`csvpy`、`in2csv`、`sql2csv` |

> **风险已知并接受**：这 12 个命令能接受 `--required-headers` 参数但不生效。
> 这是切片纪律的代价，必须写进文档与 `--help`，否则就成了
> **"声称在校验但实际没校验的守门选项，比没有更危险"**。

## 6. 明确不做（非目标）

- `allow-unknown-headers`（是否允许额外列）
- `enforce-header-order`（列顺序是否必须一致）
- 列类型校验
- 行级业务规则校验
- header 别名 / 规范名映射
- 多套 schema profile
- 大小写不敏感匹配
- BOM 剥离（仅做两侧 strip，不特殊处理 `﻿`）
- 列名本身含逗号或引号的转义语法
- 写出（printer）侧的 schema 输出
- 覆盖第 5 节列出的 12 个非目标命令

## 7. 验收标准（对应 `tests/approved/` 的 6 个场景）

| # | 场景 | 期望 |
| --- | --- | --- |
| 1 | 必需列全部存在 | 正常输出，退出码 0 |
| 2 | 缺失一列 | 退出码 1，`Missing required header(s): currency` |
| 3 | 缺失多列 | 退出码 1，缺失列按**声明顺序**列出 |
| 4 | 存在多余列 | 通过（R6） |
| 5 | 大小写不一致 | 视为缺失，报错（R1） |
| 6 | 未传 `--required-headers` | 行为与改动前完全一致（**回归保险**） |

补充：`-H` + `--required-headers` 同传 → 报错（R5）；空文件 → 不报错（R8）。
这两条由 `tests/` 既有测试与新增单测覆盖，不进 approval 夹具（它们不是"业务事实"，是接口契约）。

## 8. 与原培训大纲的偏离

| 大纲原文 | 实际 | 原因 |
| --- | --- | --- |
| 落在 `csvkit/cli.py` 的 `CSVKitBaseReader` | 落在 `CSVKitUtility` | **`CSVKitBaseReader` 在 csvkit 中不存在**（全仓库 grep 零命中） |
| TDD 红-绿-重构驱动实现 | Approved Scenarios 驱动 | 测试锚定业务事实，而非 AI 生成的代码行为 |
| 「改基类 → 所有命令生效」 | 只覆盖 2 / 14 个命令 | csvkit 有 5 条互不相干的 header 读取路径 |
