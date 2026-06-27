# 合婚应用库（cbcm-app-compatibility）

调用 `cbcm-core` 的**消费者**：读两人 TOML → 排盘 → 合婚关系分析。

> ⚠️ 含经验断法（生肖/五行合婚），未经统计验证，仅供玩乐探索。

## 用法
```bash
python -m cbcm_compat example_input.toml
python -m cbcm_compat example_input.toml --json
```

## 分析维度（均复用 core 算子）
- **生肖（年支）**：三合 / 六合 / 相冲 / 相害 / 相刑
- **夫妻宫（日支）**：同上关系
- **日主五行**：相生 / 相克 / 比和（docs/04 差分表）
- **五行互补**：A 之缺行是否为 B 之旺行
- 综合评分（断法占位，非验证）

输入见 `example_input.toml`：`[person_a]` / `[person_b]` / `[convention]`。
