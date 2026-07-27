import pandas as pd

from database import get_connection


CSV_PATH = "data/raw/nba_player_stats.csv"


def main():
    df = pd.read_csv(CSV_PATH)

    print("Original columns:")
    print(df.columns.tolist())
    print(f"Total rows: {len(df)}")

    # 2024-25シーズンだけ抽出
    df_2025 = df[df["Year"] == 2025].copy()

    # 必要な列だけ取り出す
    salaries = df_2025[
        ["Player", "Team", "Salary", "Year"]
    ].copy()

    # 列名をプロジェクト側に合わせる
    salaries = salaries.rename(
        columns={
            "Player": "player_name",
            "Team": "team",
            "Salary": "salary",
            "Year": "season",
        }
    )

    # 欠損データを削除
    salaries = salaries.dropna(
        subset=["player_name", "team", "salary"]
    )

    # 年俸を整数型にする
    salaries["salary"] = pd.to_numeric(
        salaries["salary"],
        errors="coerce"
    )

    salaries = salaries.dropna(subset=["salary"])
    salaries["salary"] = salaries["salary"].astype(int)

    # CSVとして保存
    salaries.to_csv(
        "data/processed/salaries_2025.csv",
        index=False
    )

    # SQLiteへ保存
    conn = get_connection()

    salaries.to_sql(
        "salaries",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()

    print("\n2025 salary data:")
    print(salaries.head(10))
    print(f"\nSaved rows: {len(salaries)}")


if __name__ == "__main__":
    main()