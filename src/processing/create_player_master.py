import pandas as pd

from units.database import get_connection


def create_player_master():
    query = """
    SELECT
        cp.PLAYER_ID,
        cp.PLAYER,
        cp.TeamID,
        t.full_name AS TEAM_NAME,
        t.abbreviation,
        cp.POSITION,
        cp.NUM
    FROM current_players cp
    JOIN teams t
        ON cp.TeamID = t.id
    """

    conn = get_connection()

    df = pd.read_sql_query(query, conn)

    df.to_sql(
        "player_master",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()

    return df


def main():
    df = create_player_master()

    print(df.head())
    print(f"\nTotal Players : {len(df)}")


if __name__ == "__main__":
    main()