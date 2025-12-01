"""
Reporter module for generating JSON and HTML reports.
"""

import json
import time
from pathlib import Path
from typing import TypedDict, Union


class TestResult(TypedDict):
    """Type definition for a complete test result."""

    Constant: str
    Category: str
    Domain: str
    IP: str
    Latency_ms: float
    Status: str
    AWS_Region: str
    Country: str
    Region: str
    City: str


def save_json(results: list[TestResult], filepath: Union[str, Path]) -> None:
    """
    Save results to JSON file.

    Args:
        results: List of test results
        filepath: Output file path
    """
    with Path(filepath).open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)


def generate_html(results: list[TestResult], threshold: float = 12.0) -> str:
    """
    Generate HTML report with interactive DataTables.

    Args:
        results: List of test results
        threshold: Latency threshold in ms for co-location classification

    Returns:
        HTML string
    """
    colo_count = sum(1 for r in results if r["Status"] == "COLO")
    total_count = len(results)
    colo_percentage = (colo_count / total_count * 100) if total_count > 0 else 0

    timestamp = time.strftime("%Y-%m-%d %H:%M")

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Binance Co-location Report</title>
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 2em;
            background: #1a1a1a;
            color: #eee;
        }}
        table {{
            background: #2d2d2d;
            width: 100%;
        }}
        th {{
            background: #007acc;
            color: white;
        }}
        td {{
            padding: 8px;
            border-bottom: 1px solid #444;
        }}
        .colo {{
            background: #0f5132 !important;
            color: #d4edda;
            font-weight: bold;
        }}
        .slow {{
            background: #664d03 !important;
            color: #fff3cd;
        }}
        .fail {{
            background: #842029 !important;
            color: #f8d7da;
        }}
        .summary {{
            margin: 1em 0 2em 0;
            padding: 1em;
            background: #2d2d2d;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <h1>Binance Latency Report – {timestamp}</h1>
    <div class="summary">
        <p><strong>{colo_count}</strong> / <strong>{total_count}</strong> IPs under {threshold} ms → <strong>{colo_percentage:.1f}% CO-LOCATED IN TOKYO</strong></p>
    </div>
    <table id="t">
        <thead>
            <tr>
                <th>Constant</th>
                <th>Category</th>
                <th>Domain</th>
                <th>IP</th>
                <th>Latency (ms)</th>
                <th>Status</th>
                <th>AWS Region</th>
                <th>Country</th>
                <th>City</th>
            </tr>
        </thead>
        <tbody>"""

    for r in results:
        row_class = (
            "colo"
            if r["Status"] == "COLO"
            else "slow"
            if r["Status"] == "SLOW"
            else "fail"
        )
        lat = f"{r['Latency_ms']:.2f}" if r["Latency_ms"] else "N/A"
        html += f"""
            <tr class="{row_class}">
                <td>{r["Constant"]}</td>
                <td>{r["Category"]}</td>
                <td>{r["Domain"]}</td>
                <td>{r["IP"]}</td>
                <td>{lat}</td>
                <td>{r["Status"]}</td>
                <td>{r["AWS_Region"]}</td>
                <td>{r["Country"]}</td>
                <td>{r["City"]}</td>
            </tr>"""

    html += """
        </tbody>
    </table>
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
    <script>
        $(() => $('#t').DataTable({
            "pageLength": 100,
            "order": [[4, "asc"]]
        }));
    </script>
</body>
</html>"""

    return html


def save_html(
    results: list[TestResult], filepath: Union[str, Path], threshold: float = 12.0
) -> None:
    """
    Generate and save HTML report.

    Args:
        results: List of test results
        filepath: Output file path
        threshold: Latency threshold in ms for co-location classification
    """
    html = generate_html(results, threshold)
    with Path(filepath).open("w", encoding="utf-8") as f:
        f.write(html)
