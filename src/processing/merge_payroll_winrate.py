import sqlite3
import pandas as pd

conn = sqlite3.connect("data/nba.db")

salary_df = pd.read_csv(
    "data/processed/team_salary_ranking.csv"
)

stats_df = pd.read_sql(
    """
    SELECT
        s.*,
        t.abbreviation
    FROM team_season_stats AS s
    LEFT JOIN teams AS t
        ON s.TEAM_ID = t.id
    """,
    conn
)

merged_df = pd.merge(
    salary_df,
    stats_df,
    on="abbreviation",
    how="inner"
)

print(merged_df.head())

output_path = "data/processed/payroll_winrate.csv"

merged_df.to_csv(
    output_path,
    index=False
)

print(f"Saved {len(merged_df)} teams to {output_path}")

salary_teams = set(salary_df["abbreviation"])
stats_teams = set(stats_df["abbreviation"])

print("Salary only:", salary_teams - stats_teams)
print("Stats only :", stats_teams - salary_teams)

print(
    stats_df[
        stats_df["TEAM_NAME"].isin([
            "Brooklyn Nets",
            "Phoenix Suns",
            "Charlotte Hornets"
        ])
    ][["TEAM_NAME", "abbreviation"]]
)

teams_df = pd.read_sql(
    """
    SELECT id, full_name, abbreviation
    FROM teams
    ORDER BY full_name
    """,
    conn
)

print(teams_df)

conn.close()