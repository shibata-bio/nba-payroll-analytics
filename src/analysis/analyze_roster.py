import pandas as pd

from units.database import get_connection


def load_roster():
    query = """
    SELECT
        cp.PLAYER AS player_name,
        cp.POSITION AS position,
        cp.NUM AS jersey_number,
        t.full_name AS team_name,
        t.abbreviation
    FROM current_players AS cp
    JOIN teams AS t
        ON cp.TeamID = t.id
    ORDER BY t.full_name, cp.PLAYER
    """

    conn = get_connection()
    df = pd.read_sql_query(query, conn)
    conn.close()

    return df


def main():
    df = load_roster()

    print(df.head(20))
    print(f"\nTotal players: {len(df)}")


if __name__ == "__main__":
    main()