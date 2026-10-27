# -*- coding: utf-8 -*-
"""
第 6 周项目 · 第 2 步：分析。

先跑 fetch_mp.py 拿到 data/mp_ti_binary.csv，再在这里写代码回答问题。

六个问题见 讲义.md 第 4 节。每个问题下面留了空，自己写。
写不出来时，先想"这个问题对应哪一列、要 groupby 还是筛选"，再去翻 week05 的练习。
"""


import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
HERE = Path(__file__).resolve().parent
FIG = HERE / "figures"
FIG.mkdir(exist_ok=True)

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

df = pd.read_csv(HERE / "data" / "mp_ti_binary.csv")

print("形状：", df.shape)
print(df.head())
print("每列缺失值：")
print(df.isna().sum().to_string())

before = len(df)
df = df[(df["nelements"] == 2) & (df["density"] > 1)].copy()
print("清洗：", before, "->", len(df))

record = len(df)
chemsy = df["chemsys"].nunique()      # nunique() 已经是整数，不要再套 len()
print(record, chemsy, record / chemsy)


# ============================================================
# 问题 2：稳定材料（is_stable）占多少？
# ------------------------------------------------------------
stable_material=(df["is_stable"]==True).mean()
print(stable_material)
# ============================================================
# 问题 3：金属占比？非金属带隙中位数？带隙最大的三个是谁？
# ------------------------------------------------------------
metal_mean=(df["is_metal"]==True).mean()
gap=df.loc[df["is_metal"]==False,"band_gap"].median()
gaps=df.loc[~df["is_metal"]].nlargest(3, "band_gap")[["formula_pretty", "band_gap"]]
print("金属占比", metal_mean, "非金属带隙中位数", gap, "n =", int((~df["is_metal"]).sum()))
print(gaps)
# ============================================================
# 问题 4：最轻、最重的材料各是哪个？密度中位数？
# ------------------------------------------------------------
print(df.nsmallest(1, "density")[["formula_pretty", "density"]])
print(df.nlargest(1, "density")[["formula_pretty", "density"]])
print("密度中位数", df["density"].median())
# ============================================================
# 问题 5：稳定 vs 非稳定的平均形成能，差多少？
# ------------------------------------------------------------
stable_formation=df.loc[(df["is_stable"]==True),"formation_energy_per_atom"].mean()
not_stable_formation=df.loc[(df["is_stable"]==False),"formation_energy_per_atom"].mean()
print("稳定:",stable_formation,"不稳定:",not_stable_formation,"形成能差:",stable_formation-not_stable_formation)
print(df.groupby("is_stable")["formation_energy_per_atom"].agg(["mean", "median", "count"]))


# ============================================================
# 问题 6：按搭档元素统计：哪个体系材料最多？哪个平均形成能最负？
# ------------------------------------------------------------

print("体系最多：")
print(df["chemsys"].value_counts().head(3))

mean_fe = df.groupby("chemsys")["formation_energy_per_atom"].mean().sort_values()
print("平均形成能最负：")
print(mean_fe.head(3))
# ============================================================
# 图 1：密度 vs 带隙（金属灰色、非金属彩色）
# ------------------------------------------------------------
plt.figure(figsize=(7, 5))
metal = df[df["is_metal"]]
nonmetal = df[~df["is_metal"]]
plt.scatter(metal["density"], metal["band_gap"],
            s=15, color="gray", alpha=0.5, label="金属")
plt.scatter(nonmetal["density"], nonmetal["band_gap"],
            s=15, alpha=0.8, label="非金属")
plt.xlabel("密度 (g/cm³)")
plt.ylabel("带隙 (eV)")
plt.title("密度 vs 带隙图")
plt.legend()
plt.tight_layout()
plt.savefig(FIG / "fig1_density_bandgap.png", dpi=150)
plt.close()

# ============================================================
# 图 2：形成能分布直方图（稳定 / 非稳定两组）
# ------------------------------------------------------------
plt.figure(figsize=(7, 4))

plt.hist(df.loc[df["is_stable"], "formation_energy_per_atom"],
         bins=30, alpha=0.6, label="稳定")
plt.hist(df.loc[~df["is_stable"], "formation_energy_per_atom"],
         bins=30, alpha=0.6, label="非稳定")

plt.xlabel("形成能 (eV/atom)")
plt.ylabel("材料数")
plt.title("形成能分布：稳定 vs 非稳定（n=661）")
plt.legend()
plt.tight_layout()
plt.savefig(FIG / "fig2_formation_energy.png", dpi=150)
plt.close()

# ============================================================
# 图 3：各体系材料数柱状图（前 12 个）
# ------------------------------------------------------------
counts = df["chemsys"].value_counts().head(12)

plt.figure(figsize=(8, 4))
plt.bar(counts.index, counts.values)

plt.xlabel("化学体系")
plt.ylabel("材料数")
plt.title("各化学体系的材料数量（前 12）")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(FIG / "fig3_chemsys_count.png", dpi=150)
plt.close()

print("\n图都存到 figures/ 里了。")
