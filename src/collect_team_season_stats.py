from nba_api.stats.endpoints import leaguedashteamstats

from database import get_connection


SEASON = "2024-25"


def main():
    print(f"Collecting team stats for {SEASON}...")

    response = leaguedashteamstats.LeagueDashTeamStats(
        season=SEASON,
        season_type_all_star="Regular Season",
        timeout=60
    )

    df = response.get_data_frames()[0]

    columns = [
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
    "TOV"
    ]

    df = df[columns].copy()

    conn = get_connection()

    df.to_sql(
        "team_season_stats",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()

    print(f"Saved {len(df)} teams.")
    print(df.head())


if __name__ == "__main__":
    main()