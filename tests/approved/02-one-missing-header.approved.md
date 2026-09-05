# 场景 2：缺失一列

上游漏发了 `currency` 列。校验在解析初始化阶段就报错，
退出码 1，stderr 给出可读的缺失列名，stdout 为空——**不产出半截结果**。

规格：`docs/specs/required-headers.md` 第 7 节 #2、规则 R4

## 输入 `reconciliation.csv`

```csv
order_id,amount
A-1001,120.50
A-1002,80.00
```

## 命令

```console
csvcut -c order_id --required-headers order_id,amount,currency reconciliation.csv
```

## 退出码

```text
1
```

## 标准输出

```csv
```

## 标准错误

```text
MissingRequiredHeadersError: Missing required header(s): currency
```
