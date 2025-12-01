"""
CLI interface for Binance co-location research tool.
"""

import argparse
import logging
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from tqdm import tqdm

from binancecoloresearch.geo import get_geo
from binancecoloresearch.network import resolve_ips, reverse_dns_aws, test_latency
from binancecoloresearch.parser import parse_constants
from binancecoloresearch.reporter import TestResult, save_html, save_json


def setup_logging(log_file: str) -> None:
    """Set up logging configuration."""
    # Create log directory if it doesn't exist
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s %(message)s",
    )


def classify_status(success: bool, latency_ms: float, threshold: float) -> str:
    """
    Classify test result based on success and latency.

    Args:
        success: Whether connection was successful
        latency_ms: Measured latency in milliseconds
        threshold: Threshold for co-location classification

    Returns:
        Status string: "COLO", "SLOW", or "FAIL"
    """
    if success and latency_ms < threshold:
        return "COLO"
    elif success:
        return "SLOW"
    else:
        return "FAIL"


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Test latency to Binance endpoints and detect co-location"
    )
    parser.add_argument(
        "--url-file",
        default="data/binance_url.txt",
        help="Path to URL constants file (default: data/binance_url.txt)",
    )
    parser.add_argument(
        "--output-json",
        default="results/latency_results.json",
        help="JSON output path (default: results/latency_results.json)",
    )
    parser.add_argument(
        "--output-html",
        default="results/latency_results.html",
        help="HTML output path (default: results/latency_results.html)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=80,
        help="Number of concurrent threads (default: 80)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=12.0,
        help="Co-location latency threshold in ms (default: 12)",
    )
    parser.add_argument(
        "--log-file",
        default="results/latency.log",
        help="Log file path (default: results/latency.log)",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_file)

    # Check if URL file exists
    url_file = Path(args.url_file)
    if not url_file.exists():
        print(f"Error: URL file not found: {args.url_file}")
        sys.exit(1)

    print("Loading Binance endpoints...")
    constants = parse_constants(args.url_file)
    print(f"Found {len(constants)} endpoints")

    # Resolve DNS for all domains
    domain_ip_map: dict[str, list[str]] = {}
    for endpoint in tqdm(constants, desc="Resolving DNS"):
        domain = endpoint["domain"]
        if domain not in domain_ip_map:
            domain_ip_map[domain] = resolve_ips(domain)

    # Build target list
    targets = []
    for endpoint in constants:
        for ip in domain_ip_map.get(endpoint["domain"], []):
            targets.append(
                (endpoint["constant"], endpoint["category"], endpoint["domain"], ip)
            )

    print(f"\nTesting TLS handshake + geo + AWS region on {len(targets)} IPs...")
    results: list[TestResult] = []
    colo_count = 0

    # Test latency concurrently
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(test_latency, ip, domain): (const, cat, domain, ip)
            for const, cat, domain, ip in targets
        }

        for future in tqdm(
            as_completed(futures),
            total=len(futures),
            desc="TLS + Geo",
            unit="ip",
            colour="green",
        ):
            const, cat, domain, ip = futures[future]
            result = future.result()

            # Get AWS region and geo info
            aws = reverse_dns_aws(result["ip"])
            geo = get_geo(result["ip"])

            # Classify status
            status = classify_status(
                result["success"], result["latency_ms"], args.threshold
            )
            if status == "COLO":
                colo_count += 1

            results.append(
                {
                    "Constant": const,
                    "Category": cat,
                    "Domain": domain,
                    "IP": result["ip"],
                    "Latency_ms": result["latency_ms"],
                    "Status": status,
                    "AWS_Region": aws,
                    "Country": geo["country"],
                    "Region": geo["region"],
                    "City": geo["city"],
                }
            )

    # Save results
    print("\nSaving results...")
    # Create output directory if it doesn't exist
    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_html).parent.mkdir(parents=True, exist_ok=True)

    save_json(results, args.output_json)
    save_html(results, args.output_html, args.threshold)

    # Summary
    total_count = len(results)
    colo_percentage = (colo_count / total_count * 100) if total_count > 0 else 0
    print(f"\nDONE! {colo_count}/{total_count} IPs are COLO ({colo_percentage:.1f}%)")
    print(f"📊 JSON: {args.output_json}")
    print(f"🌐 HTML: {args.output_html} → green = your edge")


if __name__ == "__main__":
    main()
