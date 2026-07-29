import pandas as pd

from units.database import get_connection


def load_salary_data():
    query = """
    SELECT
        cp.PLAYER AS player_name,
        cp.POSITION AS position,
        t.full_name AS team_name,
        s.salary
    FROM current_players AS cp
    JOIN teams AS t
        ON cp.TeamID = t.id
    JOIN salaries AS s
        ON cp.PLAYER = s.player_name
    ORDER BY s.salary DESC
    """

    conn = get_connection()
    df = pd.read_sql_query(query, conn)
    conn.close()

    return df


def main():
    df = load_salary_data()

    print(df)
    print(f"\nMatched players: {len(df)}")


if __name__ == "__main__":
    main()