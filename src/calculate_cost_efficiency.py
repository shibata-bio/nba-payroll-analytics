import pandas as pd
import numpy as np


INPUT_PATH = "data/processed/payroll_winrate.csv"
OUTPUT_PATH = "data/processed/cost_efficiency_ranking.csv"


def main():
    df = pd.read_csv(INPUT_PATH)

    # 年俸を100万ドル単位に変換
    df["payroll_million"] = (
        df["total_salary"] / 1_000_000
    )

    # 年俸から勝率を予測する単回帰
    slope, intercept = np.polyfit(
        df["payroll_million"],
        df["W_PCT"],
        1
    )

    # 各チームの予測勝率
    df["expected_win_pct"] = (
        slope * df["payroll_million"] + intercept
    )

    # 残差 = 実際の勝率 - 予測勝率
    df["cost_efficiency"] = (
        df["W_PCT"] - df["expected_win_pct"]
    )

    # コスパ順位
    df = df.sort_values(
        "cost_efficiency",
        ascending=False
    ).reset_index(drop=True)

    df["cost_efficiency_rank"] = (
        df.index + 1
    )

    # 出力列
    result = df[
        [
            "cost_efficiency_rank",
            "abbreviation",
            "TEAM_NAME",
            "payroll_million",
            "W",
            "L",
            "W_PCT",
            "expected_win_pct",
            "cost_efficiency"
        ]
    ].copy()

    result.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print(result.head(10).to_string(index=False))

    print(
        f"\nSaved {len(result)} teams "
        f"to {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()