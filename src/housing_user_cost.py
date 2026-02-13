from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class HousingCostInput:
    floor_area_m2: float
    purchase_price_per_m2: float
    down_payment_fraction: float = 0.0
    annual_mortgage_rate: float = 0.04
    mortgage_term_years: int = 30
    annual_home_value_growth_rate: float = 0.02
    annual_income_growth_rate: float = 0.03
    gross_household_income_start: float = 60_000.0
    household_size: int = 2
    annual_property_tax_rate: float = 0.001
    annual_maintenance_rate: float = 0.01
    annual_inflation_rate: float = 0.02
    annual_required_return_rate: float = 0.03
    annual_imputed_rent_rate: float = 0.0035
    mortgage_interest_deductible_fraction: float = 1.0
    mortgage_interest_tax_rate: float = 0.37
    wet_hillen_fraction: float = 0.0
    transfer_tax_rate_owner_occupier: float = 0.02
    other_purchase_cost_rate: float = 0.03


@dataclass(frozen=True)
class YearlyHousingCost:
    year: int
    home_value: float
    annual_interest_paid: float
    annual_principal_paid: float
    annual_mortgage_payment: float
    annual_tax_benefit_hra: float
    annual_property_tax: float
    annual_maintenance: float
    annual_imputed_rent_tax: float
    annual_required_return_cost: float
    annual_expected_capital_gain: float
    annualized_purchase_cost: float
    annual_user_cost_excluding_principal: float
    monthly_user_cost_excluding_principal: float
    monthly_cash_outflow_including_principal: float
    gross_household_income: float
    user_cost_income_ratio: float


def _annuity_monthly_payment(loan_principal: float, annual_rate: float, months: int) -> float:
    if months <= 0:
        raise ValueError("months must be > 0")
    if annual_rate == 0:
        return loan_principal / months

    monthly_rate = annual_rate / 12
    factor = (1 + monthly_rate) ** months
    return loan_principal * (monthly_rate * factor) / (factor - 1)


def simulate_yearly_housing_costs(inputs: HousingCostInput) -> List[YearlyHousingCost]:
    home_value_start = inputs.floor_area_m2 * inputs.purchase_price_per_m2
    if not 0 <= inputs.down_payment_fraction < 1:
        raise ValueError("down_payment_fraction must be in [0, 1)")

    mortgage_principal = home_value_start * (1 - inputs.down_payment_fraction)
    total_months = inputs.mortgage_term_years * 12
    monthly_payment = _annuity_monthly_payment(
        loan_principal=mortgage_principal,
        annual_rate=inputs.annual_mortgage_rate,
        months=total_months,
    )

    one_time_purchase_cost = home_value_start * (
        inputs.transfer_tax_rate_owner_occupier + inputs.other_purchase_cost_rate
    )
    annualized_purchase_cost = one_time_purchase_cost / inputs.mortgage_term_years

    monthly_rate = inputs.annual_mortgage_rate / 12
    remaining_balance = mortgage_principal
    rows: List[YearlyHousingCost] = []

    for year in range(1, inputs.mortgage_term_years + 1):
        home_value = home_value_start * ((1 + inputs.annual_home_value_growth_rate) ** (year - 1))
        annual_interest_paid = 0.0
        annual_principal_paid = 0.0

        for _ in range(12):
            if remaining_balance <= 0:
                break

            monthly_interest = remaining_balance * monthly_rate
            monthly_principal = min(monthly_payment - monthly_interest, remaining_balance)
            remaining_balance -= monthly_principal

            annual_interest_paid += monthly_interest
            annual_principal_paid += monthly_principal

        annual_mortgage_payment = annual_interest_paid + annual_principal_paid
        annual_tax_benefit_hra = (
            annual_interest_paid
            * inputs.mortgage_interest_deductible_fraction
            * inputs.mortgage_interest_tax_rate
        )
        annual_property_tax = home_value * inputs.annual_property_tax_rate
        annual_maintenance = home_value * inputs.annual_maintenance_rate

        gross_imputed_rent = home_value * inputs.annual_imputed_rent_rate
        hillen_discount = gross_imputed_rent * inputs.wet_hillen_fraction
        annual_imputed_rent_tax = max(0.0, gross_imputed_rent - hillen_discount) * inputs.mortgage_interest_tax_rate

        annual_required_return_cost = home_value * inputs.annual_required_return_rate
        annual_expected_capital_gain = home_value * inputs.annual_home_value_growth_rate

        annual_user_cost_excluding_principal = (
            annual_interest_paid
            + annual_property_tax
            + annual_maintenance
            + annual_imputed_rent_tax
            + annual_required_return_cost
            + annualized_purchase_cost
            - annual_tax_benefit_hra
            - annual_expected_capital_gain
        )

        monthly_user_cost_excluding_principal = annual_user_cost_excluding_principal / 12
        monthly_cash_outflow_including_principal = (
            annual_mortgage_payment
            + annual_property_tax
            + annual_maintenance
            + annual_imputed_rent_tax
            + annualized_purchase_cost
            - annual_tax_benefit_hra
        ) / 12

        gross_household_income = inputs.gross_household_income_start * (
            (1 + inputs.annual_income_growth_rate) ** (year - 1)
        )
        user_cost_income_ratio = annual_user_cost_excluding_principal / gross_household_income

        rows.append(
            YearlyHousingCost(
                year=year,
                home_value=home_value,
                annual_interest_paid=annual_interest_paid,
                annual_principal_paid=annual_principal_paid,
                annual_mortgage_payment=annual_mortgage_payment,
                annual_tax_benefit_hra=annual_tax_benefit_hra,
                annual_property_tax=annual_property_tax,
                annual_maintenance=annual_maintenance,
                annual_imputed_rent_tax=annual_imputed_rent_tax,
                annual_required_return_cost=annual_required_return_cost,
                annual_expected_capital_gain=annual_expected_capital_gain,
                annualized_purchase_cost=annualized_purchase_cost,
                annual_user_cost_excluding_principal=annual_user_cost_excluding_principal,
                monthly_user_cost_excluding_principal=monthly_user_cost_excluding_principal,
                monthly_cash_outflow_including_principal=monthly_cash_outflow_including_principal,
                gross_household_income=gross_household_income,
                user_cost_income_ratio=user_cost_income_ratio,
            )
        )

    return rows
