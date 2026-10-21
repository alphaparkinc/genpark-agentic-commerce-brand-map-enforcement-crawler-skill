# -*- coding: utf-8 -*-
"""Brand MAP Enforcement Crawler Sentinel for GenPark Agentic Commerce."""
import json
from typing import Dict, Any, List

class BrandMAPEnforcementCrawlerSentinel:
    @staticmethod
    def audit_reseller_map_violations(product_sku: str, map_floor_price_usd: float, observed_listings: List[Dict[str, Any]]) -> Dict[str, Any]:
        violations = []
        for l in observed_listings:
            price = l.get("price_usd", 0.0)
            if price < map_floor_price_usd:
                erosion = round(map_floor_price_usd - price, 2)
                violations.append({
                    "merchant": l.get("merchant_name", "Unknown"),
                    "marketplace": l.get("marketplace", "Web"),
                    "observed_price": price,
                    "price_erosion_usd": erosion,
                    "violation_pct": round((erosion / map_floor_price_usd) * 100.0, 1)
                })
        
        return {
            "sku": product_sku,
            "map_floor_price_usd": map_floor_price_usd,
            "total_listings_audited": len(observed_listings),
            "violation_count": len(violations),
            "active_violations": violations,
            "brand_health_status": "MAP_INTEGRITY_COMPROMISED" if violations else "100PCT_MAP_COMPLIANT"
        }

    @staticmethod
    def generate_automated_cease_and_desist_map_notice(merchant_name: str, sku: str, violation_price_usd: float, map_floor_usd: float, marketplace: str = "Amazon") -> Dict[str, Any]:
        letter = f"""FORMAL NOTICE OF UNILATERAL MAP POLICY VIOLATION

To: {merchant_name}
Marketplace: {marketplace}
Subject: Price Policy Non-Compliance on SKU {sku}

Our brand monitoring system has logged your listing on {marketplace} advertising SKU {sku} at ${violation_price_usd:.2f}, which is below our established Minimum Advertised Price (MAP) floor of ${map_floor_usd:.2f}.

In accordance with our Authorized Reseller Agreement, you are required to cure this violation by adjusting your advertised price to or above ${map_floor_usd:.2f} within 24 hours of this transmission. Failure to comply will result in immediate suspension of purchasing privileges and revocation of authorized distributor status.
"""
        return {
            "merchant": merchant_name,
            "sku": sku,
            "notice_status": "ISSUED",
            "cure_period_hours": 24,
            "formal_letter_body": letter
        }
