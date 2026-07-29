import sqlite3
import pandas as pd

DB_PATH = "data/nba.db"
PLAYER_STATS_PATH = "data/raw/nba_player_stats.csv"
OUTPUT_PATH = "data/processed/team_season_dataset.csv"

def load_player_stats():

  player_df = pd.read_csv(PLAYER_STATS_PATH)

  return player_df  

def load_team_stats():

  with sqlite3.connect(DB_PATH) as conn:
    team_df = pd.read_sql(
        "SELECT * FROM team_season_stats",
        conn
    )

  return team_df

player_df = load_player_stats()
team_df = load_team_stats()

def create_team_payroll(player_df):
    required_columns = [
        "Player",
        "Salary",
        "Year",
        "Team",
        "G",
        "Age",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in player_df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    payroll_df = player_df[required_columns].copy()

    # 数値列を安全に数値型へ変換
    payroll_df["Salary"] = pd.to_numeric(
        payroll_df["Salary"],
        errors="coerce"
    )

    payroll_df["Year"] = pd.to_numeric(
        payroll_df["Year"],
        errors="coerce"
    )

    payroll_df["G"] = pd.to_numeric(
        payroll_df["G"],
        errors="coerce"
    )

    payroll_df["Age"] = pd.to_numeric(
        payroll_df["Age"],
        errors="coerce"
    )

    payroll_df = payroll_df.dropna(
        subset=["Player", "Salary", "Year", "Team"]
    )

    # Basketball Referenceの移籍合計行を除外
    payroll_df = payroll_df[
        payroll_df["Team"] != "TOT"
    ].copy()

    # 同じ年に複数チーム所属した選手は、
    # 最も出場試合数が多いチームに給与を割り当てる
    payroll_df = (
        payroll_df
        .sort_values(
            ["Year", "Player", "G"],
            ascending=[True, True, False]
        )
        .drop_duplicates(
            subset=["Year", "Player"],
            keep="first"
        )
    )

    # KaggleのYearはシーズン終了年
    # 例：2020 → 2019-20
    payroll_df["SEASON"] = payroll_df["Year"].apply(
        lambda year: (
            f"{int(year) - 1}-"
            f"{str(int(year))[-2:]}"
        )
    )

    team_name_mapping = {
        "BRK": "BKN",
        "CHO": "CHA",
        "PHO": "PHX",
    }

    payroll_df["TEAM_ABBREVIATION"] = (
        payroll_df["Team"]
        .replace(team_name_mapping)
    )

    team_payroll_df = (
        payroll_df
        .groupby(
            ["SEASON", "TEAM_ABBREVIATION"],
            as_index=False
        )
        .agg(
            TOTAL_SALARY=("Salary", "sum"),
            AVG_AGE=("Age", "mean"),
            PLAYER_COUNT=("Player", "nunique"),
        )
    )

    return team_payroll_df

def load_teams():
    with sqlite3.connect(DB_PATH) as conn:
        teams_df = pd.read_sql(
            """
            SELECT
                id AS TEAM_ID,
                abbreviation AS TEAM_ABBREVIATION
            FROM teams
            """,
            conn
        )

    return teams_df

def create_team_season_dataset(
    player_df,
    team_df,
    teams_df
):
    payroll_df = create_team_payroll(player_df)

    team_stats_df = team_df.merge(
        teams_df,
        on="TEAM_ID",
        how="left"
    )

    dataset_df = team_stats_df.merge(
        payroll_df,
        on=["SEASON", "TEAM_ABBREVIATION"],
        how="left"
    )

    dataset_df["PAYROLL_MILLION"] = (
        dataset_df["TOTAL_SALARY"] / 1_000_000
    )

    dataset_df = dataset_df.sort_values(
        ["SEASON", "W_PCT"],
        ascending=[True, False]
    )

    return dataset_df

def main():
    player_df = load_player_stats()
    team_df = load_team_stats()
    teams_df = load_teams()

    dataset_df = create_team_season_dataset(
        player_df,
        team_df,
        teams_df
    )

    dataset_df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print(dataset_df.head())
    print()
    print(
        f"Saved {len(dataset_df)} rows "
        f"across {dataset_df['SEASON'].nunique()} seasons."
    )

    print()
    print("Missing payroll rows:")
    print(
        dataset_df[
            dataset_df["TOTAL_SALARY"].isna()
        ][
            [
                "SEASON",
                "TEAM_NAME",
                "TEAM_ABBREVIATION",
            ]
        ]
    )


if __name__ == "__main__":
    main()
