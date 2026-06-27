# cbcm

[English](README.md) | **中文**

> 八字的代数——中国六十甲子体系的有限群形式化，附经验证的 Python 库与一篇论文。

---

## 这是什么
**cbcm**（*Chinese Birth Chart → Math*）把中国传统命理的各套装置——十天干十二地支（干支）、五行、易经的卦、以及四柱（八字）——翻译为初等有限代数：

- 六十甲子是循环群 $\mathbb{Z}_{60}$，即 $\mathbb{Z}_{10}\times\mathbb{Z}_{12}$ 的指数 $2$ 子群；
- 五行的相生相克体系是单一循环群 $C_5$，其中**相克 = 相生²**；
- 八卦与六十四卦是 $\mathbb{F}_2$ 上的向量空间（$\mathbb{F}_2^3$、$\mathbb{F}_2^6$）；
- 算子层关系（冲、合、三合、十神）则是对合、陪集分解与乘积映射。

项目交付三件东西：一个纯函数**内核库**、三个**消费者应用**、一篇学术**论文**。

## 核心结果
1. **六十** —— 六十甲子即 $\mathbb{Z}_{60}=\langle(1,1)\rangle$，阶为 $\mathrm{lcm}(10,12)$。
2. **五** —— 相克即相生之平方（$\mathsf{ke}=\sigma^2$）；整个生克体系即 $C_5$。
3. **二** —— 易经即 $\mathbb{F}_2$ 上的线性代数；古典"变卦"操作是仿射对合。
4. **排盘映射 $\Phi$** —— 从出生时刻到 $\mathbb{Z}_{60}^4$ 中的一点，含日柱闭式 $(\mathrm{JDN}+49)\bmod 60$。
5. **骨架与装饰** —— 能写成群运算的关系，恰是传统中各派无争议的部分；其余是长期被争执的查表，且在历史上把主流让位给了前者。

## 架构
```
        消费者  :  app-personality · app-compatibility · app-dateselect   ← 经验断言只在此层
           ↑
        算子层  :  十神 · 地支关系（冲/合/害/三合）· 纳音 · 旬空
           ↑
   内核 cbcm-core :  干支 (Z60) · 五行 (C5) · 易经 (F2^n) · 排盘 (Φ)      ← 应用无关，纯函数
```
经验性断言（如"某格局致某性情"）被严格限制在消费者层；内核中立，不含此类断言。

## 包列表
| 包 | 作用 |
|---|---|
| [`packages/cbcm-core`](packages/cbcm-core) | 代数内核 + 排盘映射 $\Phi$ |
| [`packages/app-personality`](packages/app-personality) | 命盘 → 性格 / 五志画像 |
| [`packages/app-compatibility`](packages/app-compatibility) | 两盘 → 合婚分析 |
| [`packages/app-dateselect`](packages/app-dateselect) | 月内择吉日 |

## 安装与运行
需 Python ≥ 3.11，用 [`uv`](https://github.com/astral-sh/uv) 管理。
```bash
uv sync                                          # 安装工作区
uv run pytest -q                                 # 79 项测试，含交叉验证

uv run python -m cbcm_personality  packages/app-personality/example_input.toml
uv run python -m cbcm_compat       packages/app-compatibility/example_input.toml
uv run python -m cbcm_dateselect   packages/app-dateselect/example_input.toml
```
若需分钟级精确节气，装可选扩展：`uv pip install "cbcm-core[precise]"`（引入 `lunar_python`）。

## 测试与验证
**79 项测试全部通过。** 它们同时也是各定理的机器检验版（如：对所有 $x$ 成立 $\mathsf{ke}=\sigma^2$；冲/合/害皆为对合；三合陪集划分 $\mathbb{Z}_{12}$；十神映射恰十值）。排盘映射 $\Phi$ 端到端交叉验证于独立库 `lunar_python`，**300 个随机日期（1960–2030）四柱全部吻合**。

## 论文
[`paper/main_zh.tex`](paper/main_zh.tex)（中文）/ [`paper/main.tex`](paper/main.tex)（英文）——《六十、五与二：八字的有限群形式化》。
```bash
cd paper
xelatex  main_zh.tex    && xelatex  main_zh.tex   # 中文（需 ctex + fandol）
pdflatex main.tex       && pdflatex main.tex      # 英文
```

## 文档
详细的中文设计稿在 [`docs/`](docs/) —— 哲学立场、记号约定、每个对象的形式化定义。

## 状态与免责
探索性项目，为好玩与好奇而做。**形式化八字的"逻辑"，并不等于验证其"经验"预测**——它只是让这些预测精确到可被检验。所有经验断言都在应用层并附明确免责声明。

## 许可证
MIT（占位——发布时确认）。

## 链接
- 代码仓库：https://github.com/Shukahub/cbcm-Chinese-Birth-Chart-2-Math
