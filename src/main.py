from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
from pathlib import Path

from housing_user_cost import HousingCostInput, simulate_yearly_housing_costs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bereken jaarlijkse maandkosten koop vs markthuur bij annuïtaire hypotheek."
    )
    parser.add_argument("--floor-area-m2", type=float, default=85)
    parser.add_argument("--purchase-price-per-m2", type=float, default=4_500)
    parser.add_argument("--annual-mortgage-rate", type=float, default=0.04)
    parser.add_argument("--annual-home-value-growth-rate", type=float, default=0.02)
    parser.add_argument("--gross-household-income-start", type=float, default=60_000)
    parser.add_argument("--annual-income-growth-rate", type=float, default=0.03)
    parser.add_argument("--annual-market-rent-per-m2", type=float, default=220)
    parser.add_argument("--annual-market-rent-growth-rate", type=float, default=0.02)
    parser.add_argument("--tax-policy-change-year", type=int, default=None)
    parser.add_argument("--post-change-annual-imputed-rent-rate", type=float, default=None)
    parser.add_argument("--post-change-mortgage-interest-deductible-fraction", type=float, default=None)
    parser.add_argument("--post-change-annual-home-value-growth-rate-delta", type=float, default=0.0)
    parser.add_argument("--output-csv", type=Path, default=Path("output/yearly_housing_costs.csv"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    inputs = HousingCostInput(
        floor_area_m2=args.floor_area_m2,
        purchase_price_per_m2=args.purchase_price_per_m2,
        annual_mortgage_rate=args.annual_mortgage_rate,
        annual_home_value_growth_rate=args.annual_home_value_growth_rate,
        gross_household_income_start=args.gross_household_income_start,
        annual_income_growth_rate=args.annual_income_growth_rate,
        annual_market_rent_per_m2=args.annual_market_rent_per_m2,
        annual_market_rent_growth_rate=args.annual_market_rent_growth_rate,
        tax_policy_change_year=args.tax_policy_change_year,
        post_change_annual_imputed_rent_rate=args.post_change_annual_imputed_rent_rate,
        post_change_mortgage_interest_deductible_fraction=args.post_change_mortgage_interest_deductible_fraction,
        post_change_annual_home_value_growth_rate_delta=args.post_change_annual_home_value_growth_rate_delta,
    )

    rows = simulate_yearly_housing_costs(inputs)

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)

    print("Jaar | Koop user cost/mnd | Markthuur/mnd | Verschil (koop-huur)")
    for row in rows[:5]:
        print(
            f"{row.year:>4} | € {row.monthly_user_cost_excluding_principal:>10.2f} | "
            f"€ {row.monthly_market_rent_cost:>10.2f} | "
            f"€ {row.monthly_owner_user_cost_minus_renter_market_cost:>10.2f}"
        )
    print(f"\nCSV opgeslagen op: {args.output_csv}")


if __name__ == "__main__":
    main()
