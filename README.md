# 钛的二元化合物：Materials Project 数据画像

用 Materials Project API 拉取钛与另一种元素形成的二元化合物，清洗后做统计与可视化，
回答"这些材料有多金属、多稳定、带隙和密度是什么样"。

## 主要发现

- 87.3%（577/661）的 Ti-X 二元化合物是金属；非金属带隙中位数 1.81 eV（n=84）
- 只有 21.0%（139/661）位于热力学凸包上
- 形成能的平均数与中位数给出相反趋势，根因是 Mg-Ti 的 81 条正值数据拉偏了平均数

完整分析见 [report.md](report.md)。

## 数据

- 来源：Materials Project API（`/materials/summary`），2026-10-26 抓取
- 查询：`elements=Ti`、`nelements_max=2`
- 清洗：剔除 10 条纯钛（`nelements=1`）和 2 条密度异常（< 1 g/cm³）
  → 最终 661 条、70 个化学体系、15 个字段

## 文件

| 文件 | 说明 |
|---|---|
| `fetch_mp.py` | 从 MP API 分页拉取数据，输出 `data/mp_ti_binary.csv` |
| `analysis.py` | 六个分析问题 + 三张图 |
| `report.md` | 分析报告 |
| `figures/` | 密度—带隙、形成能分布、体系计数三张图 |

## 运行

```bash
pip install pandas matplotlib requests
# 把 API key 写入 api_key.txt（该文件已被 .gitignore 排除）
python fetch_mp.py
python analysis.py
```

## 环境

Python 3.14.7 · pandas 3.1.0 · matplotlib 3.11.2 · requests 2.34.2
