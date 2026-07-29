from data_loader import load_dashboard_data

from charts import (
    create_efficiency_history_chart,
    create_payroll_history_chart,
    create_payroll_ranking_chart,
    create_payroll_vs_win_chart,
    create_team_vs_league_chart,
    create_two_team_efficiency_chart,
    create_two_team_payroll_chart,
    create_two_team_win_chart,
    create_win_history_chart,
)

import numpy as np
import pandas as pd
import streamlit as st

from metrics import (
    add_cost_efficiency,
    add_cost_efficiency_all_seasons,
)


# --------------------------------------------------
# App settings
# --------------------------------------------------
st.set_page_config(
    page_title="NBA Payroll Analytics",
    page_icon="🏀",
    layout="wide",
)

st.title("🏀 NBA Payroll Analytics")
st.write(
    "Explore NBA payroll, regular-season performance, and cost efficiency "
    "across multiple seasons."
)


try:
    df = load_dashboard_data()
except (FileNotFoundError, ValueError, pd.errors.ParserError) as error:
    st.error(str(error))
    st.stop()


# --------------------------------------------------
# Sidebar filters
# --------------------------------------------------
st.sidebar.header("Filters")

season_options = sorted(
    df["SEASON"].dropna().astype(str).unique(),
    reverse=True,
)

if not season_options:
    st.error("No seasons were found in team_season_dataset.csv.")
    st.stop()

selected_season = st.sidebar.selectbox(
    "Season",
    options=season_options,
    index=0,
    )

selected_conference = st.sidebar.selectbox(
    "Conference",
    options=["All", "Eastern", "Western"],
)

# Cost efficiency is calculated using all 30 teams in the selected season.
season_df = df.loc[df["SEASON"].astype(str) == selected_season].copy()
season_df = add_cost_efficiency(season_df)

if selected_conference == "All":
    filtered_df = season_df.copy()
else:
    filtered_df = season_df.loc[
        season_df["conference"] == selected_conference
    ].copy()

st.sidebar.caption(
    f"{len(filtered_df)} teams displayed · {selected_season}"
)

if filtered_df.empty:
    st.warning("No teams match the selected filters.")
    st.stop()


# --------------------------------------------------
# Tabs
# --------------------------------------------------
overview_tab, team_tab, compare_tab = st.tabs(
    ["📊 League Overview", "🏀 Team Details", "⚔️ Team Comparison"]
)


# ==================================================
# League Overview
# ==================================================
with overview_tab:
    st.caption(
        f"Season: {selected_season} · Conference: {selected_conference}"
    )

    # -------------------------
    # Payroll ranking
    # -------------------------
    st.subheader("Team Payroll Ranking")

    ranking_df = filtered_df.sort_values(
        "payroll_million",
        ascending=True,
    )

    fig1 = create_payroll_ranking_chart(
        ranking_df,
        selected_season,
    )
    st.pyplot(fig1, use_container_width=True)

    # -------------------------
    # Payroll vs win rate
    # -------------------------
    st.subheader("Payroll vs Win Percentage")

    plot_df = filtered_df.dropna(
        subset=["payroll_million", "W_PCT"]
    ).copy()

    fig2 = create_payroll_vs_win_chart(
        plot_df,
        selected_season,
    )
    st.pyplot(fig2, use_container_width=True)

    # -------------------------
    # Cost efficiency ranking
    # -------------------------
    st.subheader("Cost-Effectiveness Ranking")
    st.caption(
        "Expected Win% is estimated from payroll across all 30 teams "
        "in the selected season."
    )

    efficiency_df = filtered_df.sort_values(
        "cost_efficiency",
        ascending=False,
    )[
        [
            "cost_efficiency_rank",
            "abbreviation",
            "payroll_million",
            "W_PCT",
            "expected_win_pct",
            "cost_efficiency",
        ]
    ].copy()

    efficiency_df["payroll_million"] = efficiency_df[
        "payroll_million"
    ].map(lambda value: f"${value:.1f}M" if pd.notna(value) else "—")
    efficiency_df["W_PCT"] = efficiency_df["W_PCT"].map(
        lambda value: f"{value:.1%}" if pd.notna(value) else "—"
    )
    efficiency_df["expected_win_pct"] = efficiency_df[
        "expected_win_pct"
    ].map(lambda value: f"{value:.1%}" if pd.notna(value) else "—")
    efficiency_df["cost_efficiency"] = efficiency_df[
        "cost_efficiency"
    ].map(lambda value: f"{value:+.1%}" if pd.notna(value) else "—")

    efficiency_df.columns = [
        "Rank",
        "Team",
        "Payroll",
        "Actual Win%",
        "Expected Win%",
        "Cost Efficiency",
    ]

    st.dataframe(
        efficiency_df,
        use_container_width=True,
        hide_index=True,
    )


# ==================================================
# Team Details
# ==================================================
with team_tab:
    st.header("🏀 Team Details")
    st.caption(
        f"Season: {selected_season} · Conference: {selected_conference}"
    )

    team_options = sorted(
        filtered_df["abbreviation"].dropna().unique()
    )

    if not team_options:
        st.info("No teams are available for the selected filters.")
        st.stop()

    default_team = "OKC" if "OKC" in team_options else team_options[0]

    selected_team = st.selectbox(
        "Select a team",
        options=team_options,
        index=team_options.index(default_team),
    )

    team_row = filtered_df.loc[
        filtered_df["abbreviation"] == selected_team
    ].iloc[0]

    st.subheader(team_row["TEAM_NAME"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Payroll", f"${team_row['payroll_million']:.1f}M")
    col2.metric("Record", f"{int(team_row['W'])}-{int(team_row['L'])}")
    col3.metric("Win Percentage", f"{team_row['W_PCT']:.1%}")
    col4.metric(
        "Cost Efficiency",
        f"{team_row['cost_efficiency']:+.1%}",
    )

    rank_value = team_row["cost_efficiency_rank"]
    rank_text = int(rank_value) if pd.notna(rank_value) else "—"
    st.caption(
        f"Cost-efficiency rank: #{rank_text} / {len(season_df)} "
        f"in {selected_season}"
    )

    st.divider()

    expected_col, actual_col, difference_col = st.columns(3)
    expected_col.metric(
        "Expected Win%",
        f"{team_row['expected_win_pct']:.1%}",
    )
    actual_col.metric("Actual Win%", f"{team_row['W_PCT']:.1%}")
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
        ),
    )

    st.divider()

    # -------------------------
    # Team logo and comparison title
    # -------------------------
    logo_col, title_col = st.columns([1, 5], vertical_alignment="center")

    team_id = int(team_row["TEAM_ID"])
    logo_url = (
        f"https://cdn.nba.com/logos/nba/{team_id}/primary/L/logo.svg"
    )

    with logo_col:
        st.image(logo_url, width=110)

    with title_col:
        st.subheader(f"{team_row['TEAM_NAME']} vs League Average")
        st.caption(
            f"Comparison with all NBA teams in {selected_season}. "
            "Positive values represent better-than-average performance."
        )

    comparison_metrics = {
        "Points": "PTS",
        "FG%": "FG_PCT",
        "3P%": "FG3_PCT",
        "FT%": "FT_PCT",
        "Rebounds": "REB",
        "Assists": "AST",
        "Turnovers": "TOV",
    }

    comparison_data = []
    for label, column in comparison_metrics.items():
        team_value = team_row[column]
        league_average = season_df[column].mean()

        if pd.isna(team_value) or pd.isna(league_average) or league_average == 0:
            difference_pct = np.nan
        else:
            difference_pct = (
                (team_value - league_average) / league_average
            ) * 100

        # Fewer turnovers are better.
        if column == "TOV" and pd.notna(difference_pct):
            difference_pct *= -1

        comparison_data.append(
            {"Metric": label, "Difference": difference_pct}
        )

    comparison_df = pd.DataFrame(comparison_data).dropna(
        subset=["Difference"]
    )

    metric_order = [
        "Points", "FG%", "3P%", "FT%",
        "Rebounds", "Assists", "Turnovers",
    ]
    comparison_df["Metric"] = pd.Categorical(
        comparison_df["Metric"],
        categories=metric_order,
        ordered=True,
    )
    comparison_df = comparison_df.sort_values("Metric", ascending=False)

    fig3 = create_team_vs_league_chart(
        comparison_df,
        team_row["TEAM_NAME"],
        selected_season,
    )
    st.pyplot(fig3, use_container_width=True)

    best = comparison_df.loc[comparison_df["Difference"].idxmax()]
    best = comparison_df.loc[comparison_df["Difference"].idxmax()]
    worst = comparison_df.loc[comparison_df["Difference"].idxmin()]

    strength_col, weakness_col = st.columns(2)
    with strength_col:
        st.success(
            f"**Biggest Strength**\n\n"
            f"{best['Metric']}: ▲ {best['Difference']:.1f}%"
        )
    with weakness_col:
        st.error(
            f"**Biggest Weakness**\n\n"
            f"{worst['Metric']}: ▼ {abs(worst['Difference']):.1f}%"
        )

    st.caption(
        "Turnovers are inverted because fewer turnovers represent "
        "better performance."
    )


    st.divider()

    # -------------------------
    # Historical trends
    # -------------------------
    st.subheader("Historical Trends")
    st.caption(
        f"Track {team_row['TEAM_NAME']} across every available season. "
        "Cost efficiency is recalculated independently within each season."
    )

    history_df = add_cost_efficiency_all_seasons(df)
    history_df = history_df.loc[
        history_df["abbreviation"] == selected_team
    ].copy()

    history_df = history_df.sort_values("SEASON")

    if history_df.empty:
        st.info("No historical data are available for this team.")
    else:
        latest_history = history_df.iloc[-1]
        earliest_history = history_df.iloc[0]

        history_col1, history_col2, history_col3 = st.columns(3)

        history_col1.metric(
            "Payroll Change",
            f"${latest_history['payroll_million']:.1f}M",
            delta=(
                f"${latest_history['payroll_million'] - earliest_history['payroll_million']:+.1f}M"
            ),
        )
        history_col2.metric(
            "Win% Change",
            f"{latest_history['W_PCT']:.1%}",
            delta=(
                f"{latest_history['W_PCT'] - earliest_history['W_PCT']:+.1%}"
            ),
        )
        history_col3.metric(
            "Latest Efficiency Rank",
            (
                f"#{int(latest_history['cost_efficiency_rank'])}"
                if pd.notna(latest_history['cost_efficiency_rank'])
                else "—"
            ),
            delta=(
                f"{int(earliest_history['cost_efficiency_rank']) - int(latest_history['cost_efficiency_rank']):+d} places"
                if pd.notna(earliest_history['cost_efficiency_rank'])
                and pd.notna(latest_history['cost_efficiency_rank'])
                else None
            ),
        )

        fig4 = create_payroll_history_chart(
            history_df,
            team_row["TEAM_NAME"],
        )
        st.pyplot(fig4, use_container_width=True)

        fig5 = create_win_history_chart(
            history_df,
            team_row["TEAM_NAME"],
        )
        st.pyplot(fig5, use_container_width=True)

        fig6 = create_efficiency_history_chart(
            history_df,
            team_row["TEAM_NAME"],
        )
        st.pyplot(fig6, use_container_width=True)

        history_table = history_df[
            [
                "SEASON",
                "payroll_million",
                "W_PCT",
                "expected_win_pct",
                "cost_efficiency",
                "cost_efficiency_rank",
            ]
        ].copy()

        history_table["payroll_million"] = history_table[
            "payroll_million"
        ].map(lambda value: f"${value:.1f}M")
        history_table["W_PCT"] = history_table["W_PCT"].map(
            lambda value: f"{value:.1%}"
        )
        history_table["expected_win_pct"] = history_table[
            "expected_win_pct"
        ].map(lambda value: f"{value:.1%}")
        history_table["cost_efficiency"] = history_table[
            "cost_efficiency"
        ].map(lambda value: f"{value:+.1%}")
        history_table["cost_efficiency_rank"] = history_table[
            "cost_efficiency_rank"
        ].map(lambda value: f"#{int(value)}" if pd.notna(value) else "—")

        history_table.columns = [
            "Season",
            "Payroll",
            "Actual Win%",
            "Expected Win%",
            "Cost Efficiency",
            "Efficiency Rank",
        ]

        with st.expander("View historical data table"):
            st.dataframe(
                history_table,
                use_container_width=True,
                hide_index=True,
            )


# ==================================================
# Team Comparison
# ==================================================
with compare_tab:
    st.header("⚔️ Team vs Team Comparison")
    st.caption(
        "Compare two teams across payroll, winning percentage, and "
        "cost efficiency for every available season."
    )

    all_team_options = sorted(df["abbreviation"].dropna().unique())

    comparison_col1, comparison_col2 = st.columns(2)

    default_team_a = "OKC" if "OKC" in all_team_options else all_team_options[0]
    default_team_b = "BOS" if "BOS" in all_team_options else all_team_options[1]

    with comparison_col1:
        team_a = st.selectbox(
            "Team A",
            options=all_team_options,
            index=all_team_options.index(default_team_a),
            key="comparison_team_a",
        )

    with comparison_col2:
        team_b = st.selectbox(
            "Team B",
            options=all_team_options,
            index=all_team_options.index(default_team_b),
            key="comparison_team_b",
        )

    if team_a == team_b:
        st.warning("Select two different teams to compare.")
    else:
        comparison_history = add_cost_efficiency_all_seasons(df)
        comparison_history = comparison_history.loc[
            comparison_history["abbreviation"].isin([team_a, team_b])
        ].copy()

        team_a_history = comparison_history.loc[
            comparison_history["abbreviation"] == team_a
        ].sort_values("SEASON")
        team_b_history = comparison_history.loc[
            comparison_history["abbreviation"] == team_b
        ].sort_values("SEASON")

        team_names = (
            comparison_history[["abbreviation", "TEAM_NAME"]]
            .drop_duplicates()
            .set_index("abbreviation")["TEAM_NAME"]
            .to_dict()
        )

        team_a_name = team_names.get(team_a, team_a)
        team_b_name = team_names.get(team_b, team_b)

        latest_common_seasons = sorted(
            set(team_a_history["SEASON"]).intersection(team_b_history["SEASON"])
        )

        if not latest_common_seasons:
            st.info("No overlapping seasons are available for these teams.")
        else:
            latest_common_season = latest_common_seasons[-1]
            latest_a = team_a_history.loc[
                team_a_history["SEASON"] == latest_common_season
            ].iloc[0]
            latest_b = team_b_history.loc[
                team_b_history["SEASON"] == latest_common_season
            ].iloc[0]

            st.subheader(
                f"{team_a_name} vs {team_b_name} — {latest_common_season}"
            )

            metric_col1, metric_col2, metric_col3 = st.columns(3)
            metric_col1.metric(
                "Payroll Difference",
                f"${latest_a['payroll_million'] - latest_b['payroll_million']:+.1f}M",
                help=f"{team_a} minus {team_b}",
            )
            metric_col2.metric(
                "Win% Difference",
                f"{latest_a['W_PCT'] - latest_b['W_PCT']:+.1%}",
                help=f"{team_a} minus {team_b}",
            )
            metric_col3.metric(
                "Efficiency Difference",
                f"{latest_a['cost_efficiency'] - latest_b['cost_efficiency']:+.1%}",
                help=f"{team_a} minus {team_b}",
            )

            st.divider()

            fig7 = create_two_team_payroll_chart(
                team_a_history,
                team_b_history,
                team_a,
                team_b,
            )
            st.pyplot(fig7, use_container_width=True)

            fig8 = create_two_team_win_chart(
                team_a_history,
                team_b_history,
                team_a,
                team_b,
            )
            st.pyplot(fig8, use_container_width=True)

            fig9 = create_two_team_efficiency_chart(
                team_a_history,
                team_b_history,
                team_a,
                team_b,
            )
            st.pyplot(fig9, use_container_width=True)

            comparison_table = comparison_history[
                [
                    "SEASON",
                    "abbreviation",
                    "payroll_million",
                    "W_PCT",
                    "expected_win_pct",
                    "cost_efficiency",
                    "cost_efficiency_rank",
                ]
            ].copy()

            comparison_table["payroll_million"] = comparison_table[
                "payroll_million"
            ].map(lambda value: f"${value:.1f}M")
            comparison_table["W_PCT"] = comparison_table["W_PCT"].map(
                lambda value: f"{value:.1%}"
            )
            comparison_table["expected_win_pct"] = comparison_table[
                "expected_win_pct"
            ].map(lambda value: f"{value:.1%}")
            comparison_table["cost_efficiency"] = comparison_table[
                "cost_efficiency"
            ].map(lambda value: f"{value:+.1%}")
            comparison_table["cost_efficiency_rank"] = comparison_table[
                "cost_efficiency_rank"
            ].map(lambda value: f"#{int(value)}" if pd.notna(value) else "—")

            comparison_table.columns = [
                "Season",
                "Team",
                "Payroll",
                "Actual Win%",
                "Expected Win%",
                "Cost Efficiency",
                "Efficiency Rank",
            ]

            comparison_table = comparison_table.sort_values(
                ["Season", "Team"]
            )

            with st.expander("View comparison data table"):
                st.dataframe(
                    comparison_table,
                    use_container_width=True,
                    hide_index=True,
                )
