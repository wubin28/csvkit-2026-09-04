# 场景 3：缺失多列，按声明顺序一次全部报出

声明顺序是 `order_id, currency, region, amount`，表头行里只有 `order_id, amount`。
缺失的 `currency` 与 `region` **一次全部报出**，顺序按**声明顺序**——
不是表头顺序、不排序。顺序确定是本夹具能稳定 diff 的前提。

规格：`docs/specs/required-headers.md` 第 7 节 #3、规则 R3

## 输入 `reconciliation.csv`

```csv
order_id,amount
A-1001,120.50
```

## 命令

```console
csvcut -c order_id --required-headers order_id,currency,region,amount reconciliation.csv
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
MissingRequiredHeadersError: Missing required header(s): currency, region
```
