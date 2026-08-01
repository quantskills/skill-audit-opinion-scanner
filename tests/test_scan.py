"""Integration-style tests for the scan pipeline (scripts/scan.py)."""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import scan


class TestResolveQuarter:
    def test_valid_format(self):
        q = scan._resolve_quarter("2024q4")
        assert q == "2024q4"

    def test_default_returns_valid_format(self):
        q = scan._resolve_quarter(None)
        assert "q" in q
        assert len(q) == 6

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError):
            scan._resolve_quarter("2024-Q4")

    def test_invalid_quarter_number(self):
        with pytest.raises(ValueError):
            scan._resolve_quarter("2024q5")


class TestValidateQuarter:
    def test_valid(self):
        scan._validate_quarter("2024q1")
        scan._validate_quarter("2024Q4")  # uppercase ok

    def test_invalid(self):
        with pytest.raises(ValueError):
            scan._validate_quarter("2024q5")
        with pytest.raises(ValueError):
            scan._validate_quarter("24q1")
        with pytest.raises(ValueError):
            scan._validate_quarter("2024q")


class TestResolveQuarters:
    def test_both_provided(self):
        s, e = scan._resolve_quarters("2024q1", "2024q4", "2024q3")
        assert s == "2024q1"
        assert e == "2024q4"

    def test_only_start(self):
        s, e = scan._resolve_quarters("2024q2", None, "2024q3")
        assert s == "2024q2"
        assert e == "2024q2"

    def test_only_end(self):
        s, e = scan._resolve_quarters(None, "2024q4", "2024q3")
        assert s == "2024q4"
        assert e == "2024q4"

    def test_default(self):
        s, e = scan._resolve_quarters(None, None, "2024q3")
        assert s == "2024q3"
        assert e == "2024q3"

    def test_invalid_start_raises(self):
        with pytest.raises(ValueError):
            scan._resolve_quarters("bad", None, "2024q3")


class TestBuildClassified:
    def test_basic_classification(self, sample_opinions_df, universe_symbols):
        name_map = {
            "000001.SZ": "平安银行",
            "000002.SZ": "万科A",
            "600519.SH": "贵州茅台",
            "300750.SZ": "宁德时代",
        }
        df = scan._build_classified(
            opinions_df=sample_opinions_df,
            universe_symbols=universe_symbols,
            include_internal_control=False,
            name_map=name_map,
        )
        assert not df.empty
        assert "risk_level" in df.columns
        assert "risk_label" in df.columns
        assert "name" in df.columns

        # 300750.SZ has qualified_opinion → should be high risk
        row = df[df["symbol"] == "300750.SZ"]
        assert len(row) == 1
        from scripts.rules import RISK_HIGH
        assert row["risk_level"].iloc[0] == RISK_HIGH

        # internal_control rows should be excluded by default
        assert "internal_control" not in df["audit_type"].values

    def test_include_internal_control(self, sample_opinions_df, universe_symbols):
        name_map = {}
        df = scan._build_classified(
            opinions_df=sample_opinions_df,
            universe_symbols=universe_symbols,
            include_internal_control=True,
            name_map=name_map,
        )
        assert "internal_control" in df["audit_type"].values

    def test_universe_filter(self, sample_opinions_df):
        """Symbols not in universe should be excluded."""
        name_map = {}
        df = scan._build_classified(
            opinions_df=sample_opinions_df,
            universe_symbols=["000001.SZ", "600519.SH"],  # only 2 of 4
            include_internal_control=False,
            name_map=name_map,
        )
        assert set(df["symbol"].unique()) == {"000001.SZ", "600519.SH"}

    def test_empty_opinions(self, universe_symbols):
        df = pd.DataFrame(columns=["symbol", "quarter", "date", "agency", "audit_type", "opinion"])
        result = scan._build_classified(df, universe_symbols, False, {})
        assert result.empty
