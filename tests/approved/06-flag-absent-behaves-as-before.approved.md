# 场景 6：未传 `--required-headers` → 行为与改动前完全一致

回归保险。默认值是 `None`，不传该选项时不做任何校验：
表头缺 `currency`（场景 2 里会报错的同一份数据）也照常输出，退出码 0。

这条夹具的作用是：任何让"未声明必需列的用户"付出代价的实现，
都会在这里 diff 出来。

规格：`docs/specs/required-headers.md` 第 7 节 #6、第 3 节

## 输入 `reconciliation.csv`

```csv
order_id,amount
A-1001,120.50
A-1002,80.00
```

## 命令

```console
csvcut -c order_id,amount reconciliation.csv
```

## 退出码

```text
0
```

## 标准输出

```csv
order_id,amount
A-1001,120.50
A-1002,80.00
```

## 标准错误

```text
```
