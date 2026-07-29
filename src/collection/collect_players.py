from nba_api.stats.static import players
import pandas as pd

from units.database import get_connection


def collect_players():
    player_list = players.get_players()
    df = pd.DataFrame(player_list)
    return df


def save_players(df):
    conn = get_connection()

    df.to_sql(
        "players",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()


def main():
    df = collect_players()
    save_players(df)
    print("Player data saved to players table.")


if __name__ == "__main__":
    main()
