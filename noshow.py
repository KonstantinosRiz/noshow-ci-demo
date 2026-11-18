"""No-show feature pipeline (trimmed version of last night's module, for the CI demo)."""

import logging
import os

import pandas as pd

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = (
    "date",
    "flight_number",
    "destination",
    "dep_time",
    "booked",
    "no_shows",
)
TARGET = "no_shows"


class DataValidationError(ValueError):
    """Raised when input data does not meet the expected contract."""


def validate(df: pd.DataFrame) -> None:
    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise DataValidationError(f"Missing required columns: {sorted(missing)}")
    if df.empty:
        raise DataValidationError("Input data is empty")


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned copy: parse dates, drop duplicates and invalid rows."""
    out = df.copy()
    out["date"] = pd.to_datetime(out["date"])
    out = out.drop_duplicates()
    invalid = out["booked"].isna() | (out["booked"] <= 0) | (out[TARGET] < 0)
    logger.info("clean: dropping %d invalid rows", int(invalid.sum()))
    return out[~invalid].reset_index(drop=True)


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Calendar features + previous-flight no-show rate (past information only)."""
    out = df.sort_values(["flight_number", "date"]).copy()
    out["dow"] = out["date"].dt.dayofweek
    out["hour"] = out["dep_time"].str[:2].astype(int)
    rate = out[TARGET] / out["booked"]
    out["prev_rate"] = rate.groupby(out["flight_number"]).shift(1)
    return out


def time_split(df: pd.DataFrame, test_start: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    cutoff = pd.Timestamp(test_start)
    return df[df["date"] < cutoff], df[df["date"] >= cutoff]
