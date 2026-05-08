#!/usr/bin/env python3
"""Configure Cloudflare DNS for therealrishabh.com.

Required:
  CLOUDFLARE_API_TOKEN with Zone:Read and DNS:Edit permissions.

Optional:
  CLOUDFLARE_ZONE_ID, SITE_DOMAIN, SITE_IPV4, SITE_PROXIED=true
"""

from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.error
import urllib.request


API_BASE = "https://api.cloudflare.com/client/v4"
DOMAIN = os.environ.get("SITE_DOMAIN", "therealrishabh.com")


def request(method: str, path: str, token: str, body: dict | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(
        f"{API_BASE}{path}",
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            payload = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode()
        raise SystemExit(f"Cloudflare API error {exc.code}: {detail}") from exc

    if not payload.get("success"):
        raise SystemExit(f"Cloudflare API request failed: {payload}")
    return payload


def public_ipv4() -> str:
    override = os.environ.get("SITE_IPV4")
    if override:
        return override
    with urllib.request.urlopen("https://api.ipify.org", timeout=10) as response:
        return response.read().decode().strip()


def zone_id(token: str) -> str:
    override = os.environ.get("CLOUDFLARE_ZONE_ID")
    if override:
        return override
    payload = request("GET", f"/zones?name={urllib.parse.quote(DOMAIN)}", token)
    zones = payload.get("result", [])
    if not zones:
        raise SystemExit(f"No Cloudflare zone found for {DOMAIN}")
    return zones[0]["id"]


def upsert_record(token: str, zid: str, desired: dict) -> None:
    name = desired["name"]
    record_type = desired["type"]
    payload = request(
        "GET",
        f"/zones/{zid}/dns_records?type={record_type}&name={urllib.parse.quote(name)}",
        token,
    )
    records = payload.get("result", [])
    if records:
        record_id = records[0]["id"]
        request("PUT", f"/zones/{zid}/dns_records/{record_id}", token, desired)
        print(f"updated {record_type} {name}")
    else:
        request("POST", f"/zones/{zid}/dns_records", token, desired)
        print(f"created {record_type} {name}")


def main() -> int:
    token = os.environ.get("CLOUDFLARE_API_TOKEN") or os.environ.get("CF_API_TOKEN")
    if not token:
        raise SystemExit("Set CLOUDFLARE_API_TOKEN or CF_API_TOKEN first.")

    ip = public_ipv4()
    zid = zone_id(token)
    proxied = os.environ.get("SITE_PROXIED", "").lower() in {"1", "true", "yes"}
    upsert_record(
        token,
        zid,
        {
            "type": "A",
            "name": DOMAIN,
            "content": ip,
            "ttl": 1,
            "proxied": proxied,
            "comment": "Managed by rishabhgoel0213 repo",
        },
    )
    upsert_record(
        token,
        zid,
        {
            "type": "CNAME",
            "name": f"www.{DOMAIN}",
            "content": DOMAIN,
            "ttl": 1,
            "proxied": proxied,
            "comment": "Managed by rishabhgoel0213 repo",
        },
    )
    mode = "proxied through Cloudflare" if proxied else "DNS-only through Cloudflare"
    print(f"{DOMAIN} now points to {ip} ({mode}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
