import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np


st.set_page_config(
    page_title="NBA Payroll Analytics",
    page_icon="🏀",
    layout="wide"
)

st.title("🏀 NBA Payroll Analytics")
st.write(
    "Explore the relationship between NBA team payroll "
    "and regular-season performance."
)


@st.cache_data
def load_data():
    payroll_df = pd.read_csv(
        "data/processed/payroll_winrate.csv"
    )

    efficiency_df = pd.read_csv(
        "data/processed/cost_efficiency_ranking.csv"
    )

    efficiency_columns = [
        "abbreviation",
        "cost_efficiency_rank",
        "expected_win_pct",
        "cost_efficiency"
    ]

    merged_df = payroll_df.merge(
        efficiency_df[efficiency_columns],
        on="abbreviation",
        how="left"
    )

    return merged_df

df = load_data()

df["payroll_million"] = (
    df["total_salary"] / 1_000_000
)

EASTERN_TEAMS = {
    "ATL", "BOS", "BKN", "CHA", "CHI",
    "CLE", "DET", "IND", "MIA", "MIL",
    "NYK", "ORL", "PHI", "TOR", "WAS"
}

df["conference"] = df["abbreviation"].apply(
    lambda team: (
        "Eastern"
        if team in EASTERN_TEAMS
        else "Western"
    )
)

st.sidebar.header("Filters")

season_options = sorted(
    df["season"].dropna().unique(),
    reverse=True
)

selected_season = st.sidebar.selectbox(
    "Season",
    options=season_options,
    index=0
)

season_df = df[
    df["season"] == selected_season
].copy()

selected_conference = st.sidebar.selectbox(
    "Conference",
    options=[
        "All",
        "Eastern",
        "Western"
    ]
)

if selected_conference == "All":
    filtered_df = season_df.copy()
else:
    filtered_df = season_df[
        season_df["conference"] == selected_conference
    ].copy()

st.sidebar.caption(
    f"{len(filtered_df)} teams displayed"
)

# -------------------------
# Tabs
# -------------------------
overview_tab, team_tab = st.tabs(
    [
        "📊 League Overview",
        "🏀 Team Details"
    ]
)

# ==================================================
# League Overview
# ==================================================
with overview_tab:

    # -------------------------
    # Payroll ranking
    # -------------------------
    st.subheader("Team Payroll Ranking")

    ranking_df = filtered_df.sort_values(
        "payroll_million",
        ascending=True
    )

    colors = [
        "#FF8C00"
        if team == "OKC"
        else "#1D428A"
        for team in ranking_df["abbreviation"]
    ]

    fig1, ax1 = plt.subplots(figsize=(10, 8))

    ax1.barh(
        ranking_df["abbreviation"],
        ranking_df["payroll_million"],
        color=colors
    )

    ax1.set_xlabel("Payroll (Million USD)")
    ax1.set_ylabel("Team")
    ax1.set_title("NBA Team Payroll Ranking")

    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.grid(axis="x", alpha=0.3)
    ax1.set_axisbelow(True)

    st.pyplot(fig1)

    # -------------------------
    # Payroll vs win rate
    # -------------------------
    st.subheader("Payroll vs Win Percentage")

    slope, intercept = np.polyfit(
        filtered_df["payroll_million"],
        filtered_df["W_PCT"],
        1
    )

    x_line = np.linspace(
        filtered_df["payroll_million"].min(),
        filtered_df["payroll_million"].max(),
        100
    )

    y_line = slope * x_line + intercept

    scatter_colors = [
        "#FF8C00"
        if team == "OKC"
        else "gray"
        for team in filtered_df["abbreviation"]
    ]

    fig2, ax2 = plt.subplots(figsize=(10, 6))

    ax2.scatter(
        filtered_df["payroll_million"],
        filtered_df["W_PCT"],
        c=scatter_colors,
        s=90,
        edgecolors="black",
        alpha=0.8
    )

    ax2.plot(
        x_line,
        y_line,
        linestyle="--",
        label="Regression line"
    )

    for _, row in filtered_df.iterrows():
        ax2.annotate(
            row["abbreviation"],
            (
                row["payroll_million"],
                row["W_PCT"]
            ),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=8
        )

    correlation = filtered_df[
        ["payroll_million", "W_PCT"]
    ].corr().iloc[0, 1]

    ax2.set_xlabel("Payroll (Million USD)")
    ax2.set_ylabel("Win Percentage")
    ax2.set_title(
        f"Payroll vs Win Percentage | Pearson r = {correlation:.3f}"
    )

    ax2.grid(alpha=0.3)
    ax2.legend(frameon=False)
    ax2.set_axisbelow(True)

    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    st.pyplot(fig2)

    # -------------------------
    # Cost efficiency ranking
    # -------------------------
    st.subheader("Cost-Effectiveness Ranking")

    efficiency_df = filtered_df.sort_values(
        "cost_efficiency",
        ascending=False
    )[
        [
            "cost_efficiency_rank",
            "abbreviation",
            "payroll_million",
            "W_PCT",
            "expected_win_pct",
            "cost_efficiency"
        ]
    ].copy()

    efficiency_df["payroll_million"] = (
        efficiency_df["payroll_million"]
        .map(lambda value: f"${value:.1f}M")
    )

    efficiency_df["W_PCT"] = (
        efficiency_df["W_PCT"]
        .map(lambda value: f"{value:.1%}")
    )

    efficiency_df["expected_win_pct"] = (
        efficiency_df["expected_win_pct"]
        .map(lambda value: f"{value:.1%}")
    )

    efficiency_df["cost_efficiency"] = (
        efficiency_df["cost_efficiency"]
        .map(lambda value: f"{value:+.1%}")
    )

    efficiency_df.columns = [
        "Rank",
        "Team",
        "Payroll",
        "Actual Win%",
        "Expected Win%",
        "Cost Efficiency"
    ]

    st.dataframe(
        efficiency_df,
        use_container_width=True,
        hide_index=True
    )


# ==================================================
# Team Details
# ==================================================
with team_tab:

    st.header("🏀 Team Details")

    team_options = sorted(
        filtered_df["abbreviation"]
        .dropna()
        .unique()
    )

    default_team = (
        "OKC"
        if "OKC" in team_options
        else team_options[0]
    )

    selected_team = st.selectbox(
        "Select a team",
        options=team_options,
        index=team_options.index(default_team)
    )

    team_row = filtered_df.loc[
        df["abbreviation"] == selected_team
    ].iloc[0]

    st.subheader(team_row["TEAM_NAME"])

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Payroll",
        f"${team_row['payroll_million']:.1f}M"
    )

    col2.metric(
        "Record",
        f"{int(team_row['W'])}-{int(team_row['L'])}"
    )

    col3.metric(
        "Win Percentage",
        f"{team_row['W_PCT']:.1%}"
    )

    col4.metric(
    "Cost Efficiency",
    f"{team_row['cost_efficiency']:+.1%}"
    )

    st.caption(
    f"Cost-efficiency rank: "
    f"#{int(team_row['cost_efficiency_rank'])} / {len(df)}"
    )

    st.divider()

    expected_col, actual_col, difference_col = st.columns(3)

    expected_col.metric(
        "Expected Win%",
        f"{team_row['expected_win_pct']:.1%}"
    )

    actual_col.metric(
        "Actual Win%",
        f"{team_row['W_PCT']:.1%}"
    )

    difference_col.metric(
        "Performance vs Expectation",
        f"{team_row['cost_efficiency']:+.1%}",
        delta=(
            "Above expectation"
            if team_row["cost_efficiency"] >= 0
            else "Below expectation"
        ),
        delta_color=(
            "normal"
            if team_row["cost_efficiency"] >= 0
            else "inverse"
        )
    )

    st.divider()

    # -------------------------
    # Team logo and comparison title
    # -------------------------
    logo_col, title_col = st.columns(
        [1, 5],
        vertical_alignment="center"
    )

    team_id = int(team_row["TEAM_ID"])

    logo_url = (
        f"https://cdn.nba.com/logos/nba/"
        f"{team_id}/primary/L/logo.svg"
    )

    with logo_col:
        st.image(
            logo_url,
            width=110
        )

    with title_col:
        st.subheader(
            f"{team_row['TEAM_NAME']} vs League Average"
        )

        st.caption(
            "Positive values represent better-than-average performance."
        )

    comparison_metrics = {
        "Points": "PTS",
        "FG%": "FG_PCT",
        "3P%": "FG3_PCT",
        "FT%": "FT_PCT",
        "Rebounds": "REB",
        "Assists": "AST",
        "Turnovers": "TOV"
    }

    comparison_data = []

    for label, column in comparison_metrics.items():
        team_value = team_row[column]
        league_average = df[column].mean()

        difference_pct = (
            (team_value - league_average)
            / league_average
        ) * 100

        # Turnoversは少ないほど高評価
        if column == "TOV":
            difference_pct *= -1

        comparison_data.append(
            {
                "Metric": label,
                "Difference": difference_pct
            }
        )

    comparison_df = pd.DataFrame(comparison_data)

    # バスケットボール指標として自然な順番を維持
    metric_order = [
        "Points",
        "FG%",
        "3P%",
        "FT%",
        "Rebounds",
        "Assists",
        "Turnovers"
    ]

    comparison_df["Metric"] = pd.Categorical(
        comparison_df["Metric"],
        categories=metric_order,
        ordered=True
    )

    comparison_df = comparison_df.sort_values(
        "Metric",
        ascending=False
    )

    colors = [
        "#2E8B57"
        if value >= 0
        else "#D9534F"
        for value in comparison_df["Difference"]
    ]

    # -------------------------
    # Bigger chart
    # -------------------------
    fig3, ax3 = plt.subplots(
        figsize=(13, 8)
    )

    bars = ax3.barh(
        comparison_df["Metric"],
        comparison_df["Difference"],
        color=colors,
        height=0.65
    )

    ax3.axvline(
        0,
        color="black",
        linestyle="--",
        linewidth=2
    )

    # ▲▼付き数値ラベル
    for bar, value in zip(
        bars,
        comparison_df["Difference"]
    ):
        y_position = (
            bar.get_y()
            + bar.get_height() / 2
        )

        if value >= 0:
            text = f"▲ {value:.1f}%"

            ax3.text(
                value + 0.5,
                y_position,
                text,
                va="center",
                ha="left",
                fontsize=11,
                fontweight="bold"
            )

        else:
            text = f"▼ {abs(value):.1f}%"

            ax3.text(
                value - 0.5,
                y_position,
                text,
                va="center",
                ha="right",
                fontsize=11,
                fontweight="bold"
            )

    ax3.set_xlabel(
        "Difference from League Average (%)",
        fontsize=12
    )

    ax3.set_ylabel(
        "Metric",
        fontsize=12
    )

    ax3.set_title(
        f"{team_row['TEAM_NAME']}\n"
        "Compared with League Average",
        fontsize=16,
        fontweight="bold",
        pad=15
    )

    ax3.grid(
        axis="x",
        linestyle="--",
        alpha=0.3
    )

    ax3.set_axisbelow(True)

    ax3.spines["top"].set_visible(False)
    ax3.spines["right"].set_visible(False)

    max_abs = (
        comparison_df["Difference"]
        .abs()
        .max()
    )

    ax3.set_xlim(
        -max_abs - 5,
        max_abs + 5
    )

    plt.tight_layout()

    st.pyplot(
        fig3,
        width="stretch"
    )

    plt.close(fig3)

    # -------------------------
    # Biggest strength / weakness
    # -------------------------
    best = comparison_df.loc[
        comparison_df["Difference"].idxmax()
    ]

    worst = comparison_df.loc[
        comparison_df["Difference"].idxmin()
    ]

    strength_col, weakness_col = st.columns(2)

    with strength_col:
        st.success(
            f"**Biggest Strength**\n\n"
            f"{best['Metric']}: "
            f"▲ {best['Difference']:.1f}%"
        )

    with weakness_col:
        st.error(
            f"**Biggest Weakness**\n\n"
            f"{worst['Metric']}: "
            f"▼ {abs(worst['Difference']):.1f}%"
        )

    st.caption(
        "Turnovers are inverted because fewer turnovers "
        "represent better performance."
    )