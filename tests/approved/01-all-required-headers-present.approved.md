# 场景 1：必需列全部存在

对账文件的表头行包含 `--required-headers` 声明的全部列名，
校验通过，命令照常输出，退出码 0。

规格：`docs/specs/required-headers.md` 第 7 节 #1

## 输入 `reconciliation.csv`

```csv
order_id,amount,currency
A-1001,120.50,USD
A-1002,80.00,EUR
```

## 命令

```console
csvcut -c order_id,currency --required-headers order_id,amount,currency reconciliation.csv
```

## 退出码

```text
0
```

## 标准输出

```csv
order_id,currency
A-1001,USD
A-1002,EUR
```

## 标准错误

```text
```
