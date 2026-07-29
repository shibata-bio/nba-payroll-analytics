import pandas as pd
import matplotlib.pyplot as plt

INPUT_PATH = "data/processed/cost_efficiency_ranking.csv"
OUTPUT_PATH = "images/cost_efficiency_ranking.png"


def main():
    df = pd.read_csv(INPUT_PATH)

    # 下から低評価、上に高評価が並ぶようにする
    df = df.sort_values(
        "cost_efficiency",
        ascending=True
    ).reset_index(drop=True)

    # 上位3・下位3を取得
    top3 = set(
        df.nlargest(3, "cost_efficiency")["abbreviation"]
    )
    bottom3 = set(
        df.nsmallest(3, "cost_efficiency")["abbreviation"]
    )

    # 色分け
    colors = []

    for team in df["abbreviation"]:
        if team == "OKC":
            colors.append("orange")
        elif team in top3:
            colors.append("seagreen")
        elif team in bottom3:
            colors.append("indianred")
        else:
            colors.append("steelblue")

    fig, ax = plt.subplots(figsize=(12, 10))

    bars = ax.barh(
        df["abbreviation"],
        df["cost_efficiency"],
        color=colors,
        height=0.72
    )

    # 0ライン
    ax.axvline(
        0,
        color="black",
        linestyle="--",
        linewidth=1.2
    )

    # バー横に数値を表示
    for bar, value in zip(bars, df["cost_efficiency"]):
        y_position = bar.get_y() + bar.get_height() / 2

        if value >= 0:
            ax.text(
                value + 0.008,
                y_position,
                f"+{value:.1%}",
                va="center",
                ha="left",
                fontsize=9
            )
        else:
            ax.text(
                value - 0.008,
                y_position,
                f"{value:.1%}",
                va="center",
                ha="right",
                fontsize=9
            )

    # グリッド
    ax.grid(
        axis="x",
        linestyle="--",
        alpha=0.35
    )
    ax.set_axisbelow(True)

    # タイトル
    fig.suptitle(
        "NBA Team Cost Efficiency Ranking (2024-25)",
        fontsize=17,
        fontweight="bold",
        y=0.97
    )

    # サブタイトル
    ax.set_title(
        "Positive values indicate teams outperforming payroll expectations.",
        fontsize=11,
        pad=14
    )

    ax.set_xlabel(
        "Cost Efficiency (Actual Win% - Expected Win%)",
        fontsize=12,
        labelpad=10
    )

    ax.set_ylabel(
        "Team",
        fontsize=12,
        labelpad=10
    )

    ax.tick_params(axis="x", labelsize=10)
    ax.tick_params(axis="y", labelsize=10)

    # 左右の余白
    max_abs = df["cost_efficiency"].abs().max()

    ax.set_xlim(
        -max_abs - 0.07,
        max_abs + 0.07
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout(rect=[0, 0, 1, 0.94])

    plt.savefig(
        OUTPUT_PATH,
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()

    print(f"Saved chart to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()