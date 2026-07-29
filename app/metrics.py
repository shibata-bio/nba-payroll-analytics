import pandas as pd
import numpy as np

def add_cost_efficiency(season_data: pd.DataFrame) -> pd.DataFrame:
    """Calculate season-wide expected win percentage and residual ranking."""
    result = season_data.copy()

    valid = result[["payroll_million", "W_PCT"]].dropna()

    if (
        len(valid) < 2
        or valid["payroll_million"].nunique() < 2
    ):
        result["expected_win_pct"] = np.nan
        result["cost_efficiency"] = np.nan
        result["cost_efficiency_rank"] = np.nan
        return result

    slope, intercept = np.polyfit(
        valid["payroll_million"],
        valid["W_PCT"],
        1,
    )

    result["expected_win_pct"] = (
        slope * result["payroll_million"] + intercept
    )
    result["cost_efficiency"] = (
        result["W_PCT"] - result["expected_win_pct"]
    )
    result["cost_efficiency_rank"] = (
        result["cost_efficiency"]
        .rank(method="min", ascending=False)
        .astype("Int64")
    )

    return result

def add_cost_efficiency_all_seasons(data: pd. DataFrame) -> pd.DataFrame:
    """Calculate cost efficiency independently within each season."""
    season_frames = []

    for _, season_data in data.groupby("SEASON", sort=False):
        season_frames.append(add_cost_efficiency(season_data))

    if not season_frames:
        return data.copy()

    return pd.concat(season_frames, ignore_index=True)