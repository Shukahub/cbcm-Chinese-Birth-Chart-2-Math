# 性格应用库（cbcm-app-personality）

调用 `cbcm-core` 的**消费者**示例：读 TOML 输入 → 排盘 → 输出性格/情志画像。

> ⚠️ 本应用的解读层包含**经验断言**（五行偏旺→五志倾向等传统对应），
> 按 docs/01 的边界，这些断言**只活在应用层**、未经统计验证，仅供玩乐探索。

## 用法

```bash
# 默认人类可读输出
python -m cbcm_personality example_input.toml

# JSON 输出
python -m cbcm_personality example_input.toml --json
```

## 输入 TOML

见 `example_input.toml`：`[birth]` 段为生辰（核心 schema），`[convention]` 段为排盘约定开关。

## 架构位置

```
BirthInput(核心schema) ──→ cbcm-core.compute_chart ──→ Chart
                                                        │
                          cbcm_personality.interpret ◀──┘  ← 经验断言只在此层
```
