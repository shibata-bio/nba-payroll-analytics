east = [
    "BOS", "BKN", "NYK", "PHI", "TOR",
    "CHI", "CLE", "DET", "IND", "MIL",
    "ATL", "CHA", "MIA", "ORL", "WAS"
]

west = [
    "DAL", "DEN", "GSW", "HOU", "LAC",
    "LAL", "MEM", "MIN", "NOP", "OKC",
    "PHX", "POR", "SAC", "SAS", "UTA"
]

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

df = pd.read_csv(
    "data/processed/team_salary_ranking.csv"
)

# 年俸順
df = df.sort_values(
    "total_salary",
    ascending=True
)

plt.figure(figsize=(10,8))

colors = []

for team in df["abbreviation"]:

    if team == "OKC":
        colors.append("#FF8C00")

    elif team in west:
        colors.append("#1D428A")

    else:
        colors.append("#C8102E")


bars = plt.barh(
    df["abbreviation"],
    df["total_salary"] / 1_000_000,
    color=colors
)

for bar, salary in zip(bars, df["total_salary"]):

    plt.text(
        bar.get_width() + 1,
        bar.get_y() + bar.get_height()/2,
        f"{salary/1_000_000:.1f}M",
        va="center",
        fontsize=8
    )

legend_elements = [
    Patch(facecolor="#FF8C00", label="Oklahoma City Thunder"),
    Patch(facecolor="#1D428A", label="Western Conference"),
    Patch(facecolor="#C8102E", label="Eastern Conference"),
]

plt.legend(
    handles=legend_elements,
    loc="lower right"
)

plt.xlabel("Total Salary (Million $)")
plt.ylabel("Team")
plt.title(
    "2025 NBA Team Payroll Ranking\nConference Comparison",
    fontsize=16,
    weight="bold"
)

plt.grid(axis="x", alpha=0.3)

ax = plt.gca()

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()

plt.savefig(
    "images/team_salary_ranking.png",
    dpi=300
)

plt.show()