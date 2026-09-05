# 场景 5：大小写不一致 → 视为缺失

表头行是 `Currency`，声明的是 `currency`。匹配**精确、大小写敏感**：
列名是上游契约，宽松匹配会掩盖上游的变更。

同一份表头顺带钉住 R2：`order_id` 与 `amount` 两侧带空格，
strip 后比较仍然匹配，所以它们**不**出现在缺失列表里——
唯一被报出的是 `currency`。

规格：`docs/specs/required-headers.md` 第 7 节 #5、规则 R1、R2

## 输入 `reconciliation.csv`

```csv
 order_id , amount , Currency
A-1001,120.50,USD
```

## 命令

```console
csvcut -c 1 --required-headers order_id,amount,currency reconciliation.csv
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
