from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]

TEAM_SEASON_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "team_season_dataset.csv"
)

EASTERN_TEAMS = {
    "ATL", "BOS", "BKN", "CHA", "CHI",
    "CLE", "DET", "IND", "MIA", "MIL",
    "NYK", "ORL", "PHI", "TOR", "WAS",
}

REQUIRED_COLUMNS = {
    "SEASON",
    "TEAM_ID",
    "TEAM_NAME",
    "TEAM_ABBREVIATION",
    "W",
    "L",
    "W_PCT",
    "PTS",
    "FG_PCT",
    "FG3_PCT",
    "FT_PCT",
    "REB",
    "AST",
    "TOV",
    "TOTAL_SALARY",
}


@st.cache_data
def load_dashboard_data() -> pd.DataFrame:
    if not TEAM_SEASON_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {TEAM_SEASON_DATA_PATH}\n"
            "Run src/processing/create_team_season_dataset.py first."
        )

    data = pd.read_csv(TEAM_SEASON_DATA_PATH)

    missing_columns = REQUIRED_COLUMNS - set(data.columns)
    if missing_columns:
        raise ValueError(
            "The team-season dataset is missing columns: "
            f"{sorted(missing_columns)}"
        )

    numeric_columns = [
        "TEAM_ID",
        "W",
        "L",
        "W_PCT",
        "PTS",
        "FG_PCT",
        "FG3_PCT",
        "FT_PCT",
        "REB",
        "AST",
        "TOV",
        "TOTAL_SALARY",
        "AVG_AGE",
        "PLAYER_COUNT",
    ]

    for column in numeric_columns:
        if column in data.columns:
            data[column] = pd.to_numeric(
                data[column],
                errors="coerce",
            )

    data["payroll_million"] = (
        data["TOTAL_SALARY"] / 1_000_000
    )

    data["abbreviation"] = (
        data["TEAM_ABBREVIATION"]
    )

    data["conference"] = (
        data["abbreviation"]
        .map(
            lambda team: (
                "Eastern"
                if team in EASTERN_TEAMS
                else "Western"
            )
        )
    )

    return data