# cbcm

**English** | [中文](README.zh-CN.md)

> The algebra of bazi — a finite-group formalisation of the Chinese sexagenary system, with a verified Python library and a paper.

---

## What this is
**cbcm** (*Chinese Birth Chart → Math*) translates the traditional devices of Chinese fate-calculation — the heavenly stems and earthly branches (*ganzhi*), the five phases (*wuxing*), the hexagrams of the *Yijing*, and the four pillars (*bazi*) — into elementary finite algebra:

- the 60-term sexagenary cycle is the cyclic group $\mathbb{Z}_{60}$, an index-$2$ subgroup of $\mathbb{Z}_{10}\times\mathbb{Z}_{12}$;
- the five-phase generating/overcoming system is a single cyclic group $C_5$, in which **overcoming equals generating squared**;
- the trigrams and hexagrams are vector spaces over $\mathbb{F}_2$ ($\mathbb{F}_2^3$, $\mathbb{F}_2^6$);
- the operator relations (clashes, combinations, three-harmonies, ten-gods) are involutions, coset partitions, and product maps.

The project ships three things: a pure-function **kernel library**, three **consumer apps**, and an academic **paper**.

## Headline results
1. **Sixty** — the sexagenary cycle is $\mathbb{Z}_{60}=\langle(1,1)\rangle$, of order $\mathrm{lcm}(10,12)$.
2. **Five** — overcoming is generating squared ($\mathsf{ke}=\sigma^2$); the whole sheng/ke system is $C_5$.
3. **Two** — the *Yijing* is linear algebra over $\mathbb{F}_2$; the classical "changing" operations are affine involutions.
4. **The casting map $\Phi$** — from a birth time to a point of $\mathbb{Z}_{60}^4$, including a closed form for the day pillar, $(\mathrm{JDN}+49)\bmod 60$.
5. **Skeleton vs decoration** — relations expressible as group laws are exactly the parts of the tradition no school disputes; the rest are lookups long contested, and historically they ceded the mainstream to the former.

## Architecture
```
        consumers  :  app-personality · app-compatibility · app-dateselect   ← empirical claims live here
             ↑
        operators  :  ten-gods · branch relations (clash/combine/harm/3-harm) · nayin · vacancy
             ↑
   kernel cbcm-core :  ganzhi (Z60) · wuxing (C5) · yijing (F2^n) · chart (Φ)   ← application-agnostic, pure
```
Empirical assertions (e.g. "this configuration yields that temperament") are confined to the consumer layer; the kernel is neutral and carries no such claims.

## Packages
| package | role |
|---|---|
| [`packages/cbcm-core`](packages/cbcm-core) | the algebraic kernel + casting map $\Phi$ |
| [`packages/app-personality`](packages/app-personality) | chart → personality / five-zhi profile |
| [`packages/app-compatibility`](packages/app-compatibility) | two charts → marriage-compatibility analysis |
| [`packages/app-dateselect`](packages/app-dateselect) | search a month for auspicious days |

## Install & run
Requires Python ≥ 3.11, managed with [`uv`](https://github.com/astral-sh/uv).
```bash
uv sync                                          # install the workspace
uv run pytest -q                                 # 79 tests, incl. cross-validation

uv run python -m cbcm_personality  packages/app-personality/example_input.toml
uv run python -m cbcm_compat       packages/app-compatibility/example_input.toml
uv run python -m cbcm_dateselect   packages/app-dateselect/example_input.toml
```
For minute-precise solar terms, install the optional extra: `uv pip install "cbcm-core[precise]"` (pulls in `lunar_python`).

## Tests & verification
**79 tests pass.** They double as machine-checked versions of the theorems (e.g. $\mathsf{ke}=\sigma^2$ over all $x$; clash/combine/harm are involutions; the three-harmony cosets partition $\mathbb{Z}_{12}$; the ten-god map is exactly ten-valued). The casting map $\Phi$ is end-to-end cross-validated against the independent library `lunar_python` on **300 random dates (1960–2030)**, all four pillars matching.

## Paper
[`paper/main.tex`](paper/main.tex) (English) / [`paper/main_zh.tex`](paper/main_zh.tex) (Chinese) — *Sixty, Five, and Two: A Finite-Group Formalisation of Bazi*.
```bash
cd paper
pdflatex main.tex       && pdflatex main.tex      # English
xelatex  main_zh.tex    && xelatex  main_zh.tex   # Chinese (needs ctex + fandol)
```

## Documentation
Detailed Chinese design notes live in [`docs/`](docs/) — philosophy, notation, and a formal definition of every object.

## Status & disclaimer
Exploratory, built for fun and curiosity. **Formalising the logic of bazi does not validate its empirical predictions** — it only makes them precise enough to be tested. All empirical claims sit in the app layer and carry explicit disclaimers.

## License
MIT (placeholder — to be confirmed on publication).

## Links
- Repository: https://github.com/Shukahub/cbcm-Chinese-Birth-Chart-2-Math
