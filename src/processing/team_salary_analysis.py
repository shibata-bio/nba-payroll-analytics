import pandas as pd

from units.database import get_connection


def main():
    conn = get_connection()

    query = """
    SELECT
        t.full_name AS team_name,
        t.abbreviation,
        SUM(s.salary) AS total_salary,
        COUNT(*) AS matched_players
    FROM salaries_with_id s
    JOIN teams t
      ON s.TeamID = t.id
    GROUP BY t.id, t.full_name, t.abbreviation
    ORDER BY total_salary DESC
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    # 見やすい表示
    df["total_salary"] = df["total_salary"].astype(int)
    df["total_salary($M)"] = (df["total_salary"] / 1_000_000).round(1)

    print(df)

    # CSV保存
    df.to_csv(
        "data/processed/team_salary_ranking.csv",
        index=False
    )

    print("\nSaved to data/processed/team_salary_ranking.csv")


if __name__ == "__main__":
    main()