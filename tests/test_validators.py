"""
Unit tests for the data quality validation rules.
Run with: pytest tests/
"""

import os
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import validators
import config


def test_check_null_rates_flags_high_null_column():
    df = pd.DataFrame({
        "customer_id": [1, 2, None, None, None],  # 60% null
        "amount": [10, 20, 30, 40, 50],
    })
    issues = validators.check_null_rates(df)
    assert any(i["check"] == "null_rate" and "customer_id" in i["detail"] for i in issues)


def test_check_null_rates_passes_clean_data():
    df = pd.DataFrame({
        "customer_id": [1, 2, 3, 4, 5],
        "amount": [10, 20, 30, 40, 50],
    })
    issues = validators.check_null_rates(df)
    assert issues == []


def test_check_duplicates_detects_dupes():
    df = pd.DataFrame({
        "customer_id": [1, 1, 2],
        "amount": [10, 10, 20],
        "region": ["East", "East", "West"],
    })
    issues = validators.check_duplicates(df)
    assert len(issues) == 1
    assert issues[0]["check"] == "duplicates"


def test_check_out_of_range_flags_negative_amount():
    df = pd.DataFrame({"amount": [100, -50, 200], "quantity": [1, 2, 3]})
    issues = validators.check_out_of_range(df)
    checks = [i["check"] for i in issues]
    assert "out_of_range" in checks


def test_check_out_of_range_flags_absurd_quantity():
    df = pd.DataFrame({"amount": [100, 200], "quantity": [5, 9999]})
    issues = validators.check_out_of_range(df)
    assert any("quantity" in i["detail"] for i in issues)


def test_check_out_of_range_passes_clean_data():
    df = pd.DataFrame({"amount": [100, 200, 300], "quantity": [1, 5, 10]})
    issues = validators.check_out_of_range(df)
    assert issues == []
