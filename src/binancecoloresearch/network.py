"""
Network module for DNS resolution, latency testing, and reverse DNS lookups.
"""

import socket
import ssl
import time
from typing import TypedDict

import dns.resolver
import dns.reversename


class LatencyResult(TypedDict):
    """Type definition for latency test result."""

    ip: str
    latency_ms: float
    success: bool


def resolve_ips(domain: str) -> list[str]:
    """
    Resolve domain to IP addresses using DNS A records.

    Args:
        domain: Domain name to resolve

    Returns:
        Sorted list of IP addresses
    """
    ips = set()
    try:
        for record in dns.resolver.resolve(domain, "A"):
            ips.add(str(record))
    except Exception:
        pass
    return sorted(ips)


def reverse_dns_aws(ip: str) -> str:
    """
    Perform reverse DNS lookup and extract AWS region information.

    Args:
        ip: IP address to lookup

    Returns:
        AWS region string if detected, PTR record otherwise, or "No PTR"
    """
    try:
        rev = dns.reversename.from_address(ip)
        ptr = str(dns.resolver.resolve(rev, "PTR")[0]).lower()
        if "ap-northeast-1" in ptr:
            # Extract availability zone (a, b, c, d, e, f)
            az = "".join(c for c in ptr if c in "abcdef") or "?"
            return f"AWS TOKYO ap-northeast-1{az}"
        return ptr[:50]
    except Exception:
        return "No PTR"


def test_latency(
    ip: str, domain: str, port: int = 443, timeout: int = 4
) -> LatencyResult:
    """
    Test TLS handshake latency to a specific IP address.

    Args:
        ip: IP address to test
        domain: Domain name for SNI in TLS handshake
        port: Port number (default: 443)
        timeout: Connection timeout in seconds (default: 4)

    Returns:
        Dictionary with ip, latency_ms, and success status
    """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    start = time.perf_counter()
    try:
        with (
            socket.create_connection((ip, port), timeout=timeout) as sock,
            ctx.wrap_socket(sock, server_hostname=domain),
        ):
            pass
        latency = round((time.perf_counter() - start) * 1000, 2)
        return {"ip": ip, "latency_ms": latency, "success": True}
    except Exception:
        latency = round((time.perf_counter() - start) * 1000, 2)
        return {"ip": ip, "latency_ms": latency, "success": False}
