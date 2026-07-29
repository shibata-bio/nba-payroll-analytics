import re
import unicodedata

import pandas as pd

from units.database import get_connection


def normalize_name(name):
    if pd.isna(name):
        return ""

    # Jokić → Jokic のようにアクセント記号を除去
    name = unicodedata.normalize("NFKD", str(name))
    name = "".join(
        char for char in name
        if not unicodedata.combining(char)
    )

    # 小文字化
    name = name.lower().strip()

    # Jr. / Sr. / II / III / IV などの末尾表記を除去
    name = re.sub(
        r"\s+(jr\.?|sr\.?|iv|iii|ii)$",
        "",
        name
    )

    # ピリオド、ハイフン、アポストロフィ、空白などを除去
    name = re.sub(r"[^a-z0-9]", "", name)

    return name


def add_player_id():
    conn = get_connection()

    salaries = pd.read_sql_query(
        """
        SELECT
            player_name,
            team,
            salary,
            season
        FROM salaries
        """,
        conn
    )

    # Kaggle側の略称をNBA API側に統一
    team_abbreviation_map = {
    "BRK": "BKN",
    "PHO": "PHX",
    "CHO": "CHA"
    }

    salaries["team"] = salaries["team"].replace(
    team_abbreviation_map
    )

    players = pd.read_sql_query(
        """
        SELECT
            id AS PLAYER_ID,
            full_name AS PLAYER
        FROM players
        """,
        conn
    )

    teams = pd.read_sql_query(
        """
        SELECT
            id AS TeamID,
            abbreviation
        FROM teams
        """,
        conn
    )

    # 選手名を正規化
    salaries["name_key"] = salaries["player_name"].apply(
        normalize_name
    )

    players["name_key"] = players["PLAYER"].apply(
        normalize_name
    )

    # 同じ選手が重複していた場合に備える
    players = players.drop_duplicates(
        subset=["name_key"]
    )

    # PLAYER_IDは選手名だけで照合
    merged = salaries.merge(
        players[["PLAYER_ID", "name_key"]],
        on="name_key",
        how="left"
    )

    # TeamIDは年俸データのチーム略称で照合
    merged = merged.merge(
        teams,
        left_on="team",
        right_on="abbreviation",
        how="left"
    )

    result = merged[
        [
            "PLAYER_ID",
            "TeamID",
            "player_name",
            "team",
            "salary",
            "season"
        ]
    ].copy()

    matched = result[result["PLAYER_ID"].notna()].copy()
    unmatched = result[result["PLAYER_ID"].isna()].copy()

    # 未一致をCSVへ保存
    unmatched.to_csv(
    "data/processed/unmatched_players.csv",
    index=False
    )

    print("Saved unmatched players.")

    matched["PLAYER_ID"] = matched["PLAYER_ID"].astype(int)

    matched.to_sql(
        "salaries_with_id",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()

    print(f"Total salary records: {len(result)}")
    print(f"Matched players: {len(matched)}")
    print(f"Unmatched players: {len(unmatched)}")

    if not unmatched.empty:
        print("\nUnmatched players:")
        print(
            unmatched[
                ["player_name", "team", "salary"]
            ].to_string(index=False)
        )

    print(
        f"\n{len(matched)} salary records "
        "saved to salaries_with_id."
    )


if __name__ == "__main__":
    add_player_id()
