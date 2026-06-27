# 择日应用库（cbcm-app-dateselect）

调用 `cbcm-core` 的**消费者**：在指定年月内按干支/五行关系给每日评分，排序输出吉日。

> ⚠️ 含经验断法（择吉规则），未经统计验证，仅供玩乐探索。

## 用法
```bash
python -m cbcm_dateselect example_input.toml
python -m cbcm_dateselect example_input.toml --json
```

## 评分维度（均复用 core 算子）
- 日支冲**月建** → 月破（大忌）
- 日支与当事人**年支/日支**：三合(吉) / 六合(吉) / 冲 / 刑 / 害
- 日柱内部：日支本气**生扶日干**为得地（吉），克日干为忌

输入见 `example_input.toml`：`[anchor]`（当事人生辰）/ `[range]`（年月）/ `[options]`（top_n）。
