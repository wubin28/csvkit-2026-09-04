# 场景 4：存在多余列 → 通过

表头行有 `region`、`note` 两个未声明的列。多余列**允许通过**：
`--required-headers` 只回答"必需列在不在"，不回答"有没有额外列"
（`allow-unknown-headers` 是独立规则，属非目标）。

本场景走 `csvgrep`，与场景 1/2/3/5/6 的 `csvcut` 一起覆盖切片声明的两个命令。

规格：`docs/specs/required-headers.md` 第 7 节 #4、规则 R6、第 5 节

## 输入 `reconciliation.csv`

```csv
order_id,amount,currency,region,note
A-1001,120.50,USD,NA,manual
A-1002,80.00,EUR,EU,auto
A-1003,45.25,USD,NA,auto
```

## 命令

```console
csvgrep -c currency -m USD --required-headers order_id,amount reconciliation.csv
```

## 退出码

```text
0
```

## 标准输出

```csv
order_id,amount,currency,region,note
A-1001,120.50,USD,NA,manual
A-1003,45.25,USD,NA,auto
```

## 标准错误

```text
```
