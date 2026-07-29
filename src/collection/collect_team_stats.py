import pandas as pd
from nba_api.stats.static import teams

from database import get_connection


def collect_teams():
    nba_teams = teams.get_teams()
    df = pd.DataFrame(nba_teams)
    return df


def save_teams(df):
    conn = get_connection()

    df.to_sql(
        "teams",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()


def main():
    df = collect_teams()
    save_teams(df)
    print("Team data saved to nba.db")


if __name__ == "__main__":
    main()