# Binance Co-location Research

[![GitHub CI](https://github.com/adityonugrohoid/binance-colo-research/actions/workflows/ci.yml/badge.svg)](https://github.com/adityonugrohoid/binance-colo-research/actions/workflows/ci.yml)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![pytest](https://img.shields.io/badge/pytest-enabled-blue?logo=pytest)](https://docs.pytest.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![mypy](https://img.shields.io/badge/mypy-checked-blue?logo=python)](http://mypy-lang.org/)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg?logo=python&logoColor=white)](https://www.python.org)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

A Python tool for testing latency to Binance endpoints and detecting co-location opportunities. This package performs comprehensive latency testing, DNS resolution, geolocation lookups, and AWS region detection to identify if you're co-located with Binance servers (particularly in Tokyo).

**Topics**: `binance` · `latency` · `co-location` · `trading` · `network-testing` · `dns` · `aws` · `tokyo` · `performance` · `python` · `uv` · `pytest` · `ruff` · `mypy`

## Features

- **Multi-Endpoint Testing**: Tests all Binance API endpoints (Spot, Futures, WebSocket, etc.)
- **Concurrent Testing**: Fast parallel testing with configurable worker threads
- **DNS Resolution**: Resolves all IP addresses for each domain
- **Latency Measurement**: TLS handshake latency testing with configurable thresholds
- **Geolocation**: IP geolocation lookup (country, region, city)
- **AWS Detection**: Reverse DNS lookup with AWS region detection
- **Interactive Reports**: Generates JSON and sortable HTML reports with color-coded results
- **Best Practices**: Built with type hints, linting (Ruff), testing (Pytest), and type checking (MyPy)

## Installation

### Prerequisites

1. **Install `uv` (if not already installed):**
   ```bash
   # On Windows
   python -m pip install uv

   # Or see https://github.com/astral-sh/uv for other methods
   ```

2. **Clone the repository:**
   ```bash
   git clone https://github.com/adityonugrohoid/binance-colo-research.git
   cd binance-colo-research
   ```

3. **Sync dependencies:**
   ```bash
   python -m uv sync
   ```
   This command will create the virtual environment (`.venv`) and install all dependencies.

4. **Install pre-commit hooks:**
   ```bash
   python -m uv run pre-commit install
   ```

## Usage

### Command Line Interface

Run the latency test using the CLI:

```bash
# Using default settings
python -m uv run binance-colo

# Or activate the venv first
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
binance-colo
```

### CLI Options

```bash
binance-colo [OPTIONS]

Options:
  --url-file PATH       Path to URL constants file (default: data/binance_url.txt)
  --output-json PATH    JSON output path (default: latency_results.json)
  --output-html PATH    HTML output path (default: latency_results.html)
  --workers INT         Number of concurrent threads (default: 80)
  --threshold FLOAT     Co-location latency threshold in ms (default: 12)
  --log-file PATH       Log file path (default: latency.log)
```

### Examples

```bash
# Test with custom threshold
python -m uv run binance-colo --threshold 10

# Use custom URL file and output paths
python -m uv run binance-colo --url-file my_urls.txt --output-html results/report.html --output-json results/report.json

# Reduce concurrent workers
python -m uv run binance-colo --workers 40

# Save to results directory (recommended)
python -m uv run binance-colo --output-html results/latency.html --output-json results/latency.json
```

### Programmatic Usage

You can also use the package programmatically:

```python
from binancecoloresearch.parser import parse_constants
from binancecoloresearch.network import resolve_ips, test_latency
from binancecoloresearch.geo import get_geo
from binancecoloresearch.reporter import save_json, save_html

# Parse URL constants
constants = parse_constants("data/binance_url.txt")

# Resolve DNS
ips = resolve_ips("api.binance.com")

# Test latency
result = test_latency("1.2.3.4", "api.binance.com")

# Get geolocation
geo = get_geo("1.2.3.4")

# Save results
save_json(results, "output.json")
save_html(results, "output.html", threshold=12.0)
```

## Real-World Results Comparison

### Test Setup

Two test locations were used to measure latency to Binance endpoints:

1. **Local PC (Singapore)** - Consumer ISP, ~300km from Tokyo
2. **Linode VPS (Tokyo)** - Data center server, located in Tokyo region

### Results Summary

**Note**: Testnet endpoints excluded from this comparison (production endpoints only)

| Metric | Singapore (Local) | Tokyo (VPS) | Improvement |
|--------|------------------|-------------|-------------|
| **Total Endpoints** | 96 | 103 | +7 |
| **COLO (<12ms)** | 0 (0%) | 0 (0%) | - |
| **SLOW (≥12ms)** | 74 (77.1%) | 103 (100%) | Better stability |
| **FAIL (timeout)** | 22 (22.9%) | 0 (0%) | 🎯 **100% success** |
| **Min Latency** | 55.71ms | **13.46ms** | 🎯 **4.1× faster** |
| **Max Latency** | 3,341ms | 1,089ms | 🎯 **3.1× better** |
| **Avg Latency** | 1,344ms | **307ms** | 🎯 **4.4× faster** |

### Key Findings

#### 🌏 From Singapore (Local PC):
- ❌ **23% endpoints failed** (timeout > 4s)
- ❌ **Very high average latency** (1.34 seconds)
- ❌ Some endpoints unreachable or severely degraded
- ⚠️ Not suitable for latency-sensitive trading

#### 🗼 From Tokyo VPS:
- ✅ **100% endpoint success rate**
- ✅ **4.4× faster average latency** (307ms vs 1,344ms)
- ✅ **Best latency: 13.46ms** to CloudFront Tokyo edge (`api.binance.com`)
- ✅ Consistent sub-500ms latency to most endpoints
- ⚠️ Still **no true co-location** (< 12ms threshold)

### Co-location Reality Check

**Even from Tokyo VPS, no endpoints achieved true co-location status (<12ms).** This suggests:

1. **Binance uses CloudFront CDN** - The closest we get is ~13ms to Tokyo CloudFront edge
2. **True co-location requires same data center** - Sub-12ms latency needs physical proximity to Binance servers
3. **Tokyo VPS is practical compromise** - 4× improvement over Singapore, 100% reliability

### Recommendation

For **latency-sensitive trading**:
- 🥇 **Best**: Tokyo-based VPS (307ms avg, 0% failures)
- 🥈 **Acceptable**: Other Asia-Pacific locations (test first)
- 🥉 **Not recommended**: Singapore consumer ISP (1,344ms avg, 23% failures)

For **true co-location** (<12ms):
- Consider Equinix Tokyo data centers (TY2, TY3, TY4)
- AWS ap-northeast-1 (same region as Binance infrastructure)
- Contact Binance for institutional co-location options

---

## Output Format

### JSON Report

The JSON file contains an array of test results:

```json
[
  {
    "Constant": "SPOT_REST_API_PROD_URL",
    "Category": "Spot Constants",
    "Domain": "api.binance.com",
    "IP": "1.2.3.4",
    "Latency_ms": 8.45,
    "Status": "COLO",
    "AWS_Region": "AWS TOKYO ap-northeast-1a",
    "Country": "Japan",
    "Region": "Tokyo",
    "City": "Tokyo"
  }
]
```

### HTML Report

The HTML report features:
- **Dark theme UI** for comfortable viewing
- **Color-coded rows**:
  - 🟢 Green (COLO): Latency < threshold → You're co-located!
  - 🟡 Yellow (SLOW): Successful but latency ≥ threshold
  - 🔴 Red (FAIL): Connection failed
- **Interactive DataTables**: Sort, filter, and paginate results
- **Summary statistics**: Co-location percentage

### Latency Classification

- **COLO**: Success + latency < 12ms (default threshold) → Co-located in Tokyo
- **SLOW**: Success + latency ≥ 12ms → Connected but not co-located
- **FAIL**: Connection failure

## Development

### Running Tests

```bash
python -m uv run pytest
```

### Linting and Formatting

```bash
# Check code
python -m uv run ruff check .

# Format code
python -m uv run ruff format .
```

### Type Checking

```bash
python -m uv run mypy .
```

## Project Structure

```
.
├── data/                      # Input data files
│   └── binance_url.txt        # Binance endpoint constants
├── results/                   # Output directory (git-ignored)
│   ├── latency_results.html   # Generated HTML report
│   ├── latency_results.json   # Generated JSON data
│   └── latency.log            # Execution log
├── src/
│   └── binancecoloresearch/   # Main package
│       ├── __init__.py
│       ├── __main__.py        # Enable python -m execution
│       ├── parser.py          # URL constants parser
│       ├── network.py         # DNS, latency, reverse DNS
│       ├── geo.py             # Geolocation lookup
│       ├── reporter.py        # JSON/HTML report generation
│       └── cli.py             # CLI interface
├── tests/                     # Test suite
│   └── test_example.py
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml             # Project configuration
├── uv.lock                    # Dependency lock file
└── README.md
```

**Note**: The `results/` directory will be auto-created on first run. It's git-ignored to avoid committing large reports.

## Technical Details

### Concurrent Testing

- Uses `ThreadPoolExecutor` for parallel testing
- Default: 80 worker threads
- Progress bars powered by `tqdm`
- 4-second timeout per connection

### DNS Resolution

- Uses `dnspython` for A record lookups
- Resolves all IP addresses for each domain
- Tests each IP individually

### AWS Region Detection

- Performs reverse DNS (PTR) lookups
- Detects AWS Tokyo region (ap-northeast-1)
- Extracts availability zone when possible

### Geolocation

- Uses ipwhois.app free API
- Provides country, region, and city
- 5-second timeout per lookup

## Dependencies

- **dnspython**: DNS resolution and reverse lookups
- **requests**: HTTP client for geolocation API
- **tqdm**: Progress bars for better UX

### Dev Dependencies

- **ruff**: Fast Python linter and formatter
- **mypy**: Static type checker
- **pytest**: Testing framework
- **pytest-cov**: Coverage reporting
- **pre-commit**: Git hooks for code quality

## License

MIT License

## Author

Adityo Nugroho - [adityo.nugroho.id@gmail.com](mailto:adityo.nugroho.id@gmail.com)

## Contributing

Contributions are welcome! Please ensure all tests pass and code is properly formatted before submitting a PR.
