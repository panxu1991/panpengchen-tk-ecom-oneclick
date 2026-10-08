#!/usr/bin/env python3
"""Unit economics for a Vietnam cross-border POP general-merchandise store.

Fulfillment: JD border warehouse (cross-border leg) + platform Vietnam last-mile.
Rates are decimals: 14% is 0.14. Input is JSON; unspecified fields use defaults.

Key Vietnam POP fee facts (verify against seller-center fee preview):
- Platform commission: category-specific (non-Mall default 14%).
- Transaction fee 6%: base = 商品实付 + 平台补贴 + 尾程运费(买家付).
- Order processing: 3000 VND per fulfilled order.
- Income tax withholding: 1% (Decree 252/2026, cross-border sellers).
- Import VAT 10%: NOT withheld by platform in border-warehouse model (vat_base=0 default).
- Last-mile shipping: paid by buyer (not a seller cost).
"""

from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

DEFAULTS: dict[str, Any] = {
    "currency": "VND",
    "selling_price": 199000,
    "seller_discount": 0,
    "platform_subsidy": 0,
    "customer_shipping_paid": 30000,  # 尾程运费：买家付，计入交易费基数，不是卖家成本
    "commission_rate": 0.14,
    "transaction_fee_rate": 0.06,
    "order_processing_fee": 3000,
    "affiliate_rate": 0.10,
    "income_tax_rate": 0.01,  # 跨境企业所得税代扣
    "import_vat_rate": 0.10,
    "vat_base": 0,  # 边境仓模式平台不代扣 VAT，默认 0
    "tariff": 0,
    "cogs": 50000,
    "border_warehouse_fee": 12000,
    "packaging_cost": 0,  # 纸箱/包装耗材：布类=0，普通=0.3-0.6元，易碎/膏体=0.6-1.5元（按纸箱规格/品类）
    "last_mile_fee": 0,  # 尾程运费买家付，卖家成本 0
    "ad_cost_per_order": 5000,
    "return_reserve": 3000,
    "other_costs": 0,
}

COST_FIELDS = (
    "cogs",
    "border_warehouse_fee",
    "packaging_cost",
    "last_mile_fee",
    "ad_cost_per_order",
    "return_reserve",
    "other_costs",
    "tariff",
)
RATE_FIELDS = (
    "commission_rate",
    "transaction_fee_rate",
    "affiliate_rate",
    "income_tax_rate",
    "import_vat_rate",
)
MONEY_FIELDS = (
    "selling_price",
    "seller_discount",
    "platform_subsidy",
    "customer_shipping_paid",
    "order_processing_fee",
    "vat_base",
) + COST_FIELDS


def decimal(value: Any, field: str) -> Decimal:
    try:
        return Decimal(str(value))
    except Exception as exc:
        raise ValueError(f"{field} must be numeric") from exc


def money(value: Decimal) -> int:
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def pct(value: Decimal) -> float:
    return float((value * Decimal("100")).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))


def calculate(raw: dict[str, Any]) -> dict[str, Any]:
    data = dict(DEFAULTS)
    data.update(raw)

    for field in MONEY_FIELDS:
        data[field] = decimal(data[field], field)
        if data[field] < 0:
            raise ValueError(f"{field} must be non-negative")
    for field in RATE_FIELDS:
        data[field] = decimal(data[field], field)
        if data[field] < 0 or data[field] > 1:
            raise ValueError(f"{field} must be between 0 and 1")

    selling_price = data["selling_price"]
    if selling_price <= 0:
        raise ValueError("selling_price must be greater than zero")

    product_paid = selling_price - data["seller_discount"]
    shipping = data["customer_shipping_paid"]
    subsidy = data["platform_subsidy"]
    seller_gross = product_paid + subsidy  # 卖家实际收款（不含买家付的尾程运费）

    commission_base = product_paid + subsidy
    transaction_base = product_paid + subsidy + shipping  # 交易费基数含尾程运费
    affiliate_base = decimal(data.get("affiliate_base", product_paid), "affiliate_base")
    if commission_base < 0 or transaction_base < 0 or affiliate_base < 0:
        raise ValueError("fee bases must be non-negative")

    commission = commission_base * data["commission_rate"]
    transaction_fee = transaction_base * data["transaction_fee_rate"]
    income_tax = commission_base * data["income_tax_rate"]
    affiliate_cost = affiliate_base * data["affiliate_rate"]
    import_vat = data["vat_base"] * data["import_vat_rate"] if data["vat_base"] else Decimal("0")

    platform_fees = commission + transaction_fee + data["order_processing_fee"] + income_tax
    variable_costs = affiliate_cost + import_vat + sum(data[f] for f in COST_FIELDS)
    contribution_profit = seller_gross - platform_fees - variable_costs

    variable_rate = (
        data["commission_rate"]
        + data["transaction_fee_rate"]
        + data["income_tax_rate"]
        + data["affiliate_rate"]
    )
    fixed_costs = (
        data["order_processing_fee"]
        + sum(data[f] for f in COST_FIELDS)
        + data["transaction_fee_rate"] * shipping  # 交易费里运费部分近似
    )
    break_even_price = fixed_costs / (Decimal("1") - variable_rate) if variable_rate < 1 else None

    return {
        "currency": str(data["currency"]),
        "inputs": {
            key: (
                money(value)
                if key in MONEY_FIELDS and isinstance(value, Decimal)
                else float(value)
                if key in RATE_FIELDS
                else value
            )
            for key, value in data.items()
            if key in MONEY_FIELDS or key in RATE_FIELDS or key == "currency"
        },
        "computed": {
            "product_paid": money(product_paid),
            "seller_gross": money(seller_gross),
            "customer_shipping_paid": money(shipping),
            "commission_base": money(commission_base),
            "transaction_base": money(transaction_base),
            "affiliate_base": money(affiliate_base),
            "platform_commission": money(commission),
            "transaction_fee": money(transaction_fee),
            "income_tax": money(income_tax),
            "order_processing_fee": money(data["order_processing_fee"]),
            "affiliate_cost": money(affiliate_cost),
            "import_vat": money(import_vat),
            "tariff": money(data["tariff"]),
            "border_warehouse_fee": money(data["border_warehouse_fee"]),
            "last_mile_fee": money(data["last_mile_fee"]),
            "total_platform_fees": money(platform_fees),
            "total_other_costs": money(variable_costs - affiliate_cost - import_vat),
            "contribution_profit": money(contribution_profit),
            "contribution_margin_pct": pct(contribution_profit / seller_gross) if seller_gross else 0.0,
            "break_even_selling_price": money(break_even_price) if break_even_price is not None else None,
        },
        "assumptions": {
            "last_mile": "last_mile_fee=0 (buyer pays shipping); customer_shipping_paid feeds the 6% transaction fee base only",
            "transaction_fee": "6% of (product_paid + platform_subsidy + customer_shipping_paid)",
            "commission": "category-specific rate of (product_paid + platform_subsidy)",
            "income_tax": "1% withholding on (product_paid + platform_subsidy), Decree 252/2026",
            "vat": "import_vat_rate applied to explicit vat_base only; border-warehouse model defaults to 0 (no platform VAT withholding)",
            "tariff": "high-value import tariff entered explicitly; only applies per-item > 1,000,000 VND",
            "returns": "included through return_reserve; actual refunds and fee reversals reconcile separately",
            "border": "JD border warehouse fee entered explicitly; verify official/seller-center rates",
        },
    }


def load_input(path: str | None) -> dict[str, Any]:
    if path in (None, "-"):
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", "-i", help="JSON file path, or - for stdin")
    parser.add_argument("--example", action="store_true", help="print an example result from DEFAULTS")
    args = parser.parse_args()

    if not args.input and not args.example:
        parser.print_help()
        return 2

    try:
        raw = DEFAULTS if args.example else load_input(args.input)
        result = calculate(raw)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
