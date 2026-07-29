import time

import pandas as pd
from nba_api.stats.endpoints import commonteamroster
from nba_api.stats.static import teams

from units.database import get_connection


SEASON = "2025-26"


def collect_current_players():
    team_list = teams.get_teams()
    player_dfs = []

    for team in team_list:
        print(f"Collecting: {team['full_name']}")

        roster = commonteamroster.CommonTeamRoster(
            team_id=team["id"],
            season=SEASON,
            timeout=60
        )

        df = roster.get_data_frames()[0]

        df["TEAM_NAME"] = team["full_name"]
        df["TEAM_ABBREVIATION"] = team["abbreviation"]

        player_dfs.append(df)

        # NBA APIへの連続アクセスを避ける
        time.sleep(1)

    return pd.concat(player_dfs, ignore_index=True)


def save_current_players(df):
    conn = get_connection()

    df.to_sql(
        "current_players",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()


def main():
    df = collect_current_players()
    save_current_players(df)

    print(f"{len(df)} current players saved.")


if __name__ == "__main__":
    main()