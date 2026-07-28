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
    return pd.read_csv(
        "data/processed/payroll_winrate.csv"
    )


df = load_data()

df["payroll_million"] = (
    df["total_salary"] / 1_000_000
)

# -------------------------
# Sidebar
# -------------------------
st.sidebar.header("Filters")

selected_team = st.sidebar.selectbox(
    "Select a team",
    sorted(df["abbreviation"].unique()),
    index=sorted(
        df["abbreviation"].unique()
    ).index("OKC")
)

# -------------------------
# Team summary
# -------------------------
team_row = df[
    df["abbreviation"] == selected_team
].iloc[0]

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Team",
    selected_team
)

col2.metric(
    "Payroll",
    f"${team_row['payroll_million']:.1f}M"
)

col3.metric(
    "Wins",
    int(team_row["W"])
)

col4.metric(
    "Win Percentage",
    f"{team_row['W_PCT']:.3f}"
)

# -------------------------
# Payroll ranking
# -------------------------
st.subheader("Team Payroll Ranking")

ranking_df = df.sort_values(
    "payroll_million",
    ascending=True
)

colors = [
    "#FF8C00"
    if team == selected_team
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

st.pyplot(fig1)

# -------------------------
# Payroll vs win rate
# -------------------------
st.subheader("Payroll vs Win Percentage")

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

scatter_colors = [
    "#FF8C00"
    if team == selected_team
    else "gray"
    for team in df["abbreviation"]
]

fig2, ax2 = plt.subplots(figsize=(10, 6))

ax2.scatter(
    df["payroll_million"],
    df["W_PCT"],
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

for _, row in df.iterrows():
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

correlation = df[
    ["payroll_million", "W_PCT"]
].corr().iloc[0, 1]

ax2.set_xlabel("Payroll (Million USD)")
ax2.set_ylabel("Win Percentage")
ax2.set_title(
    f"Payroll vs Win Percentage | Pearson r = {correlation:.3f}"
)

ax2.grid(alpha=0.3)
ax2.legend(frameon=False)

ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)

st.pyplot(fig2)

# -------------------------
# Cost efficiency
# -------------------------
df["expected_win_pct"] = (
    slope * df["payroll_million"] + intercept
)

df["residual"] = (
    df["W_PCT"] - df["expected_win_pct"]
)

st.subheader("Cost-Effectiveness Ranking")

efficiency_df = df.sort_values(
    "residual",
    ascending=False
)[
    [
        "abbreviation",
        "payroll_million",
        "W_PCT",
        "expected_win_pct",
        "residual"
    ]
]

st.dataframe(
    efficiency_df,
    use_container_width=True,
    hide_index=True
)