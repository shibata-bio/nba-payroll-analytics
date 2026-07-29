import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure


def create_payroll_ranking_chart(
    ranking_df: pd.DataFrame,
    season: str,
) -> Figure:
    colors = [
        "#FF8C00" if team == "OKC" else "#1D428A"
        for team in ranking_df["abbreviation"]
    ]

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(
        ranking_df["abbreviation"],
        ranking_df["payroll_million"],
        color=colors,
    )
    ax.set_xlabel("Payroll (Million USD)")
    ax.set_ylabel("Team")
    ax.set_title(f"NBA Team Payroll Ranking — {season}")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", alpha=0.3)
    ax.set_axisbelow(True)
    fig.tight_layout()
    return fig


def create_payroll_vs_win_chart(
    plot_df: pd.DataFrame,
    season: str,
) -> Figure:
    fig, ax = plt.subplots(figsize=(10, 6))

    scatter_colors = [
        "#FF8C00" if team == "OKC" else "gray"
        for team in plot_df["abbreviation"]
    ]

    ax.scatter(
        plot_df["payroll_million"],
        plot_df["W_PCT"],
        c=scatter_colors,
        s=90,
        edgecolors="black",
        alpha=0.8,
    )

    correlation = np.nan
    if len(plot_df) >= 2 and plot_df["payroll_million"].nunique() >= 2:
        slope, intercept = np.polyfit(
            plot_df["payroll_million"],
            plot_df["W_PCT"],
            1,
        )
        x_line = np.linspace(
            plot_df["payroll_million"].min(),
            plot_df["payroll_million"].max(),
            100,
        )
        ax.plot(
            x_line,
            slope * x_line + intercept,
            linestyle="--",
            label="Regression line",
        )
        correlation = plot_df[
            ["payroll_million", "W_PCT"]
        ].corr().iloc[0, 1]

    for _, row in plot_df.iterrows():
        ax.annotate(
            row["abbreviation"],
            (row["payroll_million"], row["W_PCT"]),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=8,
        )

    correlation_text = (
        f"{correlation:.3f}" if pd.notna(correlation) else "N/A"
    )
    ax.set_xlabel("Payroll (Million USD)")
    ax.set_ylabel("Win Percentage")
    ax.set_title(
        f"Payroll vs Win Percentage — {season} "
        f"| Pearson r = {correlation_text}"
    )
    ax.grid(alpha=0.3)
    if len(ax.lines) > 0:
        ax.legend(frameon=False)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return fig


def create_team_vs_league_chart(
    comparison_df: pd.DataFrame,
    team_name: str,
    season: str,
) -> Figure:
    colors = [
        "#2E8B57" if value >= 0 else "#D9534F"
        for value in comparison_df["Difference"]
    ]

    fig, ax = plt.subplots(figsize=(13, 8))
    bars = ax.barh(
        comparison_df["Metric"],
        comparison_df["Difference"],
        color=colors,
        height=0.65,
    )
    ax.axvline(0, color="black", linestyle="--", linewidth=2)

    for bar, value in zip(bars, comparison_df["Difference"]):
        y_position = bar.get_y() + bar.get_height() / 2
        if value >= 0:
            ax.text(
                value + 0.5,
                y_position,
                f"▲ {value:.1f}%",
                va="center",
                ha="left",
                fontsize=11,
                fontweight="bold",
            )
        else:
            ax.text(
                value - 0.5,
                y_position,
                f"▼ {abs(value):.1f}%",
                va="center",
                ha="right",
                fontsize=11,
                fontweight="bold",
            )

    ax.set_xlabel("Difference from League Average (%)", fontsize=12)
    ax.set_ylabel("Metric", fontsize=12)
    ax.set_title(
        f"{team_name} — {season}\nCompared with League Average",
        fontsize=16,
        fontweight="bold",
        pad=15,
    )
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    max_abs = comparison_df["Difference"].abs().max()
    if pd.isna(max_abs) or max_abs == 0:
        max_abs = 5
    ax.set_xlim(-max_abs - 5, max_abs + 5)

    fig.tight_layout()
    return fig


def create_payroll_history_chart(
    history_df: pd.DataFrame,
    team_name: str,
) -> Figure:
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(
        history_df["SEASON"],
        history_df["payroll_million"],
        marker="o",
        linewidth=2,
    )
    ax.set_title(f"{team_name} Payroll History")
    ax.set_xlabel("Season")
    ax.set_ylabel("Payroll (Million USD)")
    ax.grid(alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    return fig


def create_win_history_chart(
    history_df: pd.DataFrame,
    team_name: str,
) -> Figure:
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(
        history_df["SEASON"],
        history_df["W_PCT"],
        marker="o",
        linewidth=2,
        label="Actual Win%",
    )
    ax.plot(
        history_df["SEASON"],
        history_df["expected_win_pct"],
        marker="o",
        linestyle="--",
        label="Expected Win% from Payroll",
    )
    ax.set_title(f"{team_name} Win Percentage History")
    ax.set_xlabel("Season")
    ax.set_ylabel("Win Percentage")
    ax.set_ylim(0, 1)
    ax.grid(alpha=0.3)
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    return fig


def create_efficiency_history_chart(
    history_df: pd.DataFrame,
    team_name: str,
) -> Figure:
    efficiency_colors = [
        "#2E8B57" if value >= 0 else "#D9534F"
        for value in history_df["cost_efficiency"]
    ]

    fig, ax = plt.subplots(figsize=(11, 5))
    bars = ax.bar(
        history_df["SEASON"],
        history_df["cost_efficiency"],
        color=efficiency_colors,
    )
    ax.axhline(0, color="black", linestyle="--", linewidth=1.5)

    for bar, value, rank in zip(
        bars,
        history_df["cost_efficiency"],
        history_df["cost_efficiency_rank"],
    ):
        label = (
            f"{value:+.1%}\n#{int(rank)}"
            if pd.notna(rank)
            else f"{value:+.1%}"
        )
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + (0.004 if value >= 0 else -0.004),
            label,
            ha="center",
            va="bottom" if value >= 0 else "top",
            fontsize=9,
            fontweight="bold",
        )

    ax.set_title(f"{team_name} Cost-Efficiency History")
    ax.set_xlabel("Season")
    ax.set_ylabel("Actual Win% − Expected Win%")
    ax.grid(axis="y", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    return fig


def create_two_team_payroll_chart(
    team_a_history: pd.DataFrame,
    team_b_history: pd.DataFrame,
    team_a: str,
    team_b: str,
) -> Figure:
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(
        team_a_history["SEASON"],
        team_a_history["payroll_million"],
        marker="o",
        linewidth=2,
        label=team_a,
    )
    ax.plot(
        team_b_history["SEASON"],
        team_b_history["payroll_million"],
        marker="o",
        linewidth=2,
        label=team_b,
    )
    ax.set_title("Payroll History Comparison")
    ax.set_xlabel("Season")
    ax.set_ylabel("Payroll (Million USD)")
    ax.grid(alpha=0.3)
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    return fig


def create_two_team_win_chart(
    team_a_history: pd.DataFrame,
    team_b_history: pd.DataFrame,
    team_a: str,
    team_b: str,
) -> Figure:
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(
        team_a_history["SEASON"],
        team_a_history["W_PCT"],
        marker="o",
        linewidth=2,
        label=team_a,
    )
    ax.plot(
        team_b_history["SEASON"],
        team_b_history["W_PCT"],
        marker="o",
        linewidth=2,
        label=team_b,
    )
    ax.set_title("Win Percentage History Comparison")
    ax.set_xlabel("Season")
    ax.set_ylabel("Win Percentage")
    ax.set_ylim(0, 1)
    ax.grid(alpha=0.3)
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    return fig


def create_two_team_efficiency_chart(
    team_a_history: pd.DataFrame,
    team_b_history: pd.DataFrame,
    team_a: str,
    team_b: str,
) -> Figure:
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(
        team_a_history["SEASON"],
        team_a_history["cost_efficiency"],
        marker="o",
        linewidth=2,
        label=team_a,
    )
    ax.plot(
        team_b_history["SEASON"],
        team_b_history["cost_efficiency"],
        marker="o",
        linewidth=2,
        label=team_b,
    )
    ax.axhline(0, color="black", linestyle="--", linewidth=1.5)
    ax.set_title("Cost-Efficiency History Comparison")
    ax.set_xlabel("Season")
    ax.set_ylabel("Actual Win% − Expected Win%")
    ax.grid(alpha=0.3)
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    return fig
