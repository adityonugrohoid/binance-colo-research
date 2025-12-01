"""Test suite for binancecoloresearch package."""

from pathlib import Path

from binancecoloresearch import __version__
from binancecoloresearch.cli import classify_status
from binancecoloresearch.parser import parse_constants
from binancecoloresearch.reporter import TestResult, generate_html, save_json


def test_version() -> None:
    """Test package version."""
    assert __version__ == "0.1.0"


def test_parse_constants_with_sample_data(tmp_path: Path) -> None:
    """Test parsing URL constants from a sample file."""
    # Create a temporary file with sample data
    sample_file = tmp_path / "sample_urls.txt"
    sample_file.write_text(
        """# Test Category
TEST_URL = "https://api.example.com"
ANOTHER_URL = "wss://ws.example.com/stream"

# Another Category
THIRD_URL = "https://test.example.org"
"""
    )

    results = parse_constants(sample_file)

    assert len(results) == 3
    assert results[0]["constant"] == "TEST_URL"
    assert results[0]["category"] == "Test Category"
    assert results[0]["domain"] == "api.example.com"

    assert results[1]["constant"] == "ANOTHER_URL"
    assert results[1]["domain"] == "ws.example.com"

    assert results[2]["category"] == "Another Category"


def test_parse_constants_empty_file(tmp_path: Path) -> None:
    """Test parsing an empty file."""
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("")

    results = parse_constants(empty_file)
    assert len(results) == 0


def test_classify_status_colo() -> None:
    """Test status classification for co-located server."""
    assert classify_status(True, 5.0, 12.0) == "COLO"
    assert classify_status(True, 11.99, 12.0) == "COLO"


def test_classify_status_slow() -> None:
    """Test status classification for slow but successful connection."""
    assert classify_status(True, 12.0, 12.0) == "SLOW"
    assert classify_status(True, 50.0, 12.0) == "SLOW"


def test_classify_status_fail() -> None:
    """Test status classification for failed connection."""
    assert classify_status(False, 1000.0, 12.0) == "FAIL"
    assert classify_status(False, 0.0, 12.0) == "FAIL"


def test_save_json(tmp_path: Path) -> None:
    """Test saving results to JSON file."""
    output_file = tmp_path / "output.json"
    test_data: list[TestResult] = [
        {
            "Constant": "TEST",
            "Category": "Test",
            "Domain": "example.com",
            "IP": "1.2.3.4",
            "Latency_ms": 10.5,
            "Status": "COLO",
            "AWS_Region": "ap-northeast-1",
            "Country": "Japan",
            "Region": "Tokyo",
            "City": "Tokyo",
        }
    ]

    save_json(test_data, output_file)

    assert output_file.exists()
    content = output_file.read_text()
    assert "TEST" in content
    assert "example.com" in content


def test_generate_html() -> None:
    """Test HTML report generation."""
    test_data: list[TestResult] = [
        {
            "Constant": "TEST",
            "Category": "Test",
            "Domain": "example.com",
            "IP": "1.2.3.4",
            "Latency_ms": 10.5,
            "Status": "COLO",
            "AWS_Region": "ap-northeast-1",
            "Country": "Japan",
            "Region": "Tokyo",
            "City": "Tokyo",
        }
    ]

    html = generate_html(test_data, threshold=12.0)

    assert "<!DOCTYPE html>" in html
    assert "TEST" in html
    assert "example.com" in html
    assert "1.2.3.4" in html
    assert "DataTable" in html  # DataTables library usage
    assert "COLO" in html
