import pandas as pd
import pytest

import noshow


def make_df(**overrides):
    """Tiny hand-made frame: one flight on 4 consecutive days."""
    base = {
        "date": ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"],
        "flight_number": ["KL1"] * 4,
        "destination": ["LHR"] * 4,
        "dep_time": ["07:05"] * 4,
        "booked": [100, 100, 100, 100],
        "no_shows": [1, 2, 3, 4],
    }
    base.update(overrides)
    return pd.DataFrame(base)


def test_validate_rejects_missing_column():
    with pytest.raises(noshow.DataValidationError, match="booked"):
        noshow.validate(make_df().drop(columns=["booked"]))


@pytest.mark.parametrize("bad_booked", [None, 0, -1])
def test_clean_drops_invalid_bookings(bad_booked):
    df = make_df(booked=[100, bad_booked, 100, 100])
    assert len(noshow.clean(df)) == 3


def test_clean_does_not_mutate_input():
    df = make_df()
    snapshot = df.copy()
    noshow.clean(df)
    pd.testing.assert_frame_equal(df, snapshot)


def test_lag_features_only_use_past_flights():
    out = noshow.add_features(noshow.clean(make_df()))
    assert pd.isna(out["prev_rate"].iloc[0])
    assert out["prev_rate"].iloc[1:].tolist() == pytest.approx([0.01, 0.02, 0.03])


def test_time_split_has_no_overlap():
    train, test = noshow.time_split(noshow.clean(make_df()), "2026-01-03")
    assert train["date"].max() < test["date"].min()
