import pytest
from data_ingestion.api import fetch_market_data

def test_api_agent():
    data = fetch_market_data(["TSM"])
    assert "TSM" in data
    assert "price" in data["TSM"]