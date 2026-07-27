import pandas as pd

from database import get_connection


URL = "https://www.espn.com/nba/salaries"
CSV_PATH = "data/raw/salaries_2025.csv"


def collect_salaries():
    tables = pd.read_html(URL)

    print(df.head(20))
    print(df.columns)
    print(df.shape)

    # ESPNの年俸表
    df = tables[0].copy()

    print(df.head())
    print(df.columns)

    return df


def clean_salaries(df):
    # ESPNの表は列名や不要行が混ざることがあるので整理
    df.columns = ["rank", "player_name", "team", "salary"]

    # 表の途中に繰り返し入る見出し行を削除
    df = df[df["player_name"] != "NAME"].copy()

    # 年俸を "$59,606,817" → 59606817 に変換
    df["salary"] = (
        df["salary"]
        .astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
    )

    df["salary"] = pd.to_numeric(df["salary"], errors="coerce")

    # 年俸が数値にならなかった行を削除
    df = df.dropna(subset=["salary"]).copy()
    df["salary"] = df["salary"].astype(int)

    # 必要な列だけ残す
    df = df[["player_name", "team", "salary"]]

    return df


def save_salaries(df):
    # CSVにも保存
    df.to_csv(CSV_PATH, index=False)

    # SQLiteにも保存
    conn = get_connection()

    df.to_sql(
        "salaries",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()


def main():
    raw_df = collect_salaries()
    df = clean_salaries(raw_df)
    save_salaries(df)

    print(df.head(10))
    print(f"\n{len(df)} salary records saved.")


if __name__ == "__main__":
    main()