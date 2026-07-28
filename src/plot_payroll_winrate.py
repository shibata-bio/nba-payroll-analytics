import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


CSV_PATH = "data/processed/payroll_winrate.csv"
OUTPUT_PATH = "images/payroll_vs_winrate.png"


def main():
    df = pd.read_csv(CSV_PATH)

    # 年俸を100万ドル単位に変換
    df["payroll_million"] = (
        df["total_salary"] / 1_000_000
    )

    # OKCだけオレンジ、他チームはグレー
    colors = [
        "#FF8C00" if team == "OKC" else "gray"
        for team in df["abbreviation"]
    ]

    fig, ax = plt.subplots(figsize=(11, 7))

    ax.scatter(
        df["payroll_million"],
        df["W_PCT"],
        c=colors,
        s=90,
        alpha=0.8,
        edgecolors="black"
    )

    # 回帰直線
    slope, intercept = np.polyfit(
        df["payroll_million"],
        df["W_PCT"],
        1
    )

    x_line = np.linspace(
        df["payroll_million"].min(),
        df["payroll_million"].max(),
        100
    )

    y_line = slope * x_line + intercept

    ax.plot(
        x_line,
        y_line,
        linestyle="--",
        linewidth=2,
        label="Regression line"
    )

    # チーム略称を全チームに表示
    for _, row in df.iterrows():
        ax.annotate(
            row["abbreviation"],
            (
                row["payroll_million"],
                row["W_PCT"]
            ),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=8
        )

    # 相関係数
    correlation = df[
        ["payroll_million", "W_PCT"]
    ].corr().iloc[0, 1]

    ax.text(
        0.03,
        0.95,
        f"Pearson r = {correlation:.3f}",
        transform=ax.transAxes,
        fontsize=12,
        verticalalignment="top"
    )

    ax.set_xlabel("Team Payroll (Million USD)")
    ax.set_ylabel("Win Percentage")
    ax.set_title(
        "NBA Team Payroll vs Win Percentage (2024-25)",
        fontsize=16,
        weight="bold"
    )

    ax.grid(
        alpha=0.3
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.legend(
        frameon=False
    )

    plt.tight_layout()

    plt.savefig(
        OUTPUT_PATH,
        dpi=300
    )

    plt.show()

    print(f"Correlation: {correlation:.3f}")
    print(f"Saved chart to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()