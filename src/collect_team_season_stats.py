import sqlite3
import time
import pandas as pd

from nba_api.stats.endpoints import leaguedashteamstats


DB_PATH = "data/nba.db"

SEASONS = [
    "2019-20",
    "2020-21",
    "2021-22",
    "2022-23",
    "2023-24",
    "2024-25",
]


def collect_season_stats(season):
    print(f"Collecting {season}...")

    response = leaguedashteamstats.LeagueDashTeamStats(
        season=season,
        season_type_all_star="Regular Season"
    )

    df = response.get_data_frames()[0]

    df["SEASON"] = season

    return df


def main():
    season_frames = []

    for season in SEASONS:
        try:
            season_df = collect_season_stats(season)
            season_frames.append(season_df)

            # NBA APIへの連続アクセスを避ける
            time.sleep(2)

        except Exception as error:
            print(f"Failed to collect {season}: {error}")

    if not season_frames:
        raise RuntimeError("No season data was collected.")

    all_seasons_df = pd.concat(
        season_frames,
        ignore_index=True
    )

    columns = [
        "SEASON",
        "TEAM_ID",
        "TEAM_NAME",
        "GP",
        "W",
        "L",
        "W_PCT",
        "PTS",
        "FG_PCT",
        "FG3_PCT",
        "FT_PCT",
        "REB",
        "AST",
        "TOV",
    ]

    all_seasons_df = all_seasons_df[columns]

    with sqlite3.connect(DB_PATH) as connection:
        all_seasons_df.to_sql(
            "team_season_stats",
            connection,
            if_exists="replace",
            index=False
        )

    print(
        f"Saved {len(all_seasons_df)} rows "
        f"across {all_seasons_df['SEASON'].nunique()} seasons."
    )


if __name__ == "__main__":
    main()