from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class HousingCostInput:
    floor_area_m2: float
    purchase_price_per_m2: float

    down_payment_fraction: float = 0.0
    annual_mortgage_rate: float = 0.04
    mortgage_term_years: int = 30

    annual_home_value_growth_rate: float = 0.02
    annual_market_rent_per_m2: float = 220.0
    annual_market_rent_growth_rate: float = 0.02

    annual_income_growth_rate: float = 0.03
    gross_household_income_start: float = 60_000.0

    annual_inflation_rate: float = 0.02
    annual_discount_rate: float = 0.03

    annual_property_tax_rate: float = 0.001
    annual_maintenance_rate: float = 0.01

    annual_imputed_rent_rate: float = 0.0035
    mortgage_interest_deductible_fraction: float = 1.0
    mortgage_interest_tax_rate: float = 0.37
    wet_hillen_fraction: float = 0.0

    transfer_tax_rate_owner_occupier: float = 0.02
    other_purchase_cost_rate: float = 0.03

    tax_policy_change_year: Optional[int] = None
    post_change_annual_imputed_rent_rate: Optional[float] = None
    post_change_mortgage_interest_deductible_fraction: Optional[float] = None
    post_change_annual_home_value_growth_rate_delta: float = 0.0


@dataclass(frozen=True)
class YearlyHousingCost:
    year: int

    home_value_real: float
    gross_household_income_real: float

    annual_interest_paid_real: float
    annual_principal_paid_real: float
    annual_mortgage_payment_real: float

    annual_property_tax_real: float
    annual_maintenance_real: float
    annualized_purchase_cost_real: float

    annual_expected_capital_gain_real: float
    cumulative_principal_repaid_real: float
    cumulative_capital_gain_real: float

    annual_opportunity_cost_principal_real: float
    annual_opportunity_cost_capital_gain_real: float
    annual_total_opportunity_cost_real: float

    annual_box1_taxable_income_real: float
    annual_box1_tax_effect_real: float

    annual_user_cost_real: float
    monthly_user_cost_real: float

    annual_cashflow_cost_real: float
    monthly_cashflow_cost_real: float

    annual_market_rent_cost_real: float
    monthly_market_rent_cost_real: float
    monthly_owner_user_cost_minus_renter_market_cost_real: float

    user_cost_income_ratio: float


def _annuity_monthly_payment(loan_principal: float, annual_rate: float, months: int) -> float:
    if months <= 0:
        raise ValueError("months must be > 0")
    if annual_rate == 0:
        return loan_principal / months

    monthly_rate = annual_rate / 12
    factor = (1 + monthly_rate) ** months
    return loan_principal * (monthly_rate * factor) / (factor - 1)


def _has_policy_change(inputs: HousingCostInput, year: int) -> bool:
    return inputs.tax_policy_change_year is not None and year >= inputs.tax_policy_change_year


def _current_policy_rates(inputs: HousingCostInput, year: int) -> tuple[float, float, float]:
    policy_active = _has_policy_change(inputs, year)

    imputed_rent_rate = (
        inputs.post_change_annual_imputed_rent_rate
        if policy_active and inputs.post_change_annual_imputed_rent_rate is not None
        else inputs.annual_imputed_rent_rate
    )
    hra_deductible_fraction = (
        inputs.post_change_mortgage_interest_deductible_fraction
        if policy_active and inputs.post_change_mortgage_interest_deductible_fraction is not None
        else inputs.mortgage_interest_deductible_fraction
    )
    home_value_growth_rate = inputs.annual_home_value_growth_rate + (
        inputs.post_change_annual_home_value_growth_rate_delta if policy_active else 0.0
    )

    return imputed_rent_rate, hra_deductible_fraction, home_value_growth_rate


def simulate_yearly_housing_costs(inputs: HousingCostInput) -> List[YearlyHousingCost]:
    if not 0 <= inputs.down_payment_fraction < 1:
        raise ValueError("down_payment_fraction must be in [0, 1)")

    home_value_start_nominal = inputs.floor_area_m2 * inputs.purchase_price_per_m2
    mortgage_principal = home_value_start_nominal * (1 - inputs.down_payment_fraction)
    total_months = inputs.mortgage_term_years * 12
    monthly_payment = _annuity_monthly_payment(mortgage_principal, inputs.annual_mortgage_rate, total_months)

    one_time_purchase_cost = home_value_start_nominal * (
        inputs.transfer_tax_rate_owner_occupier + inputs.other_purchase_cost_rate
    )
    annualized_purchase_cost_nominal = one_time_purchase_cost / inputs.mortgage_term_years

    monthly_rate = inputs.annual_mortgage_rate / 12
    remaining_balance = mortgage_principal

    home_value_nominal = home_value_start_nominal
    market_rent_per_m2_nominal = inputs.annual_market_rent_per_m2

    cumulative_principal_repaid_real = 0.0
    cumulative_capital_gain_real = 0.0

    rows: List[YearlyHousingCost] = []

    for year in range(1, inputs.mortgage_term_years + 1):
        inflation_index = (1 + inputs.annual_inflation_rate) ** (year - 1)

        annual_interest_paid_nominal = 0.0
        annual_principal_paid_nominal = 0.0

        for _ in range(12):
            if remaining_balance <= 0:
                break
            monthly_interest = remaining_balance * monthly_rate
            monthly_principal = min(monthly_payment - monthly_interest, remaining_balance)
            remaining_balance -= monthly_principal
            annual_interest_paid_nominal += monthly_interest
            annual_principal_paid_nominal += monthly_principal

        (
            current_imputed_rent_rate,
            current_hra_deductible_fraction,
            current_home_value_growth_rate,
        ) = _current_policy_rates(inputs, year)

        annual_mortgage_payment_nominal = annual_interest_paid_nominal + annual_principal_paid_nominal

        annual_property_tax_nominal = home_value_nominal * inputs.annual_property_tax_rate
        annual_maintenance_nominal = home_value_nominal * inputs.annual_maintenance_rate

        annual_imputed_rent_nominal = home_value_nominal * current_imputed_rent_rate
        annual_hra_deductible_interest_nominal = (
            annual_interest_paid_nominal * current_hra_deductible_fraction
        )

        taxable_base_before_hillen_nominal = annual_imputed_rent_nominal - annual_hra_deductible_interest_nominal
        hillen_reduction_nominal = max(0.0, taxable_base_before_hillen_nominal) * inputs.wet_hillen_fraction
        annual_box1_taxable_income_nominal = taxable_base_before_hillen_nominal - hillen_reduction_nominal

        # positief = extra belasting betalen, negatief = belastingvoordeel / teruggave
        annual_box1_tax_effect_nominal = annual_box1_taxable_income_nominal * inputs.mortgage_interest_tax_rate

        annual_expected_capital_gain_nominal = home_value_nominal * current_home_value_growth_rate

        home_value_real = home_value_nominal / inflation_index
        annual_interest_paid_real = annual_interest_paid_nominal / inflation_index
        annual_principal_paid_real = annual_principal_paid_nominal / inflation_index
        annual_mortgage_payment_real = annual_mortgage_payment_nominal / inflation_index
        annual_property_tax_real = annual_property_tax_nominal / inflation_index
        annual_maintenance_real = annual_maintenance_nominal / inflation_index
        annualized_purchase_cost_real = annualized_purchase_cost_nominal / inflation_index
        annual_box1_taxable_income_real = annual_box1_taxable_income_nominal / inflation_index
        annual_box1_tax_effect_real = annual_box1_tax_effect_nominal / inflation_index
        annual_expected_capital_gain_real = annual_expected_capital_gain_nominal / inflation_index

        cumulative_principal_repaid_real += annual_principal_paid_real
        cumulative_capital_gain_real += annual_expected_capital_gain_real

        annual_opportunity_cost_principal_real = cumulative_principal_repaid_real * inputs.annual_discount_rate
        annual_opportunity_cost_capital_gain_real = cumulative_capital_gain_real * inputs.annual_discount_rate
        annual_total_opportunity_cost_real = (
            annual_opportunity_cost_principal_real + annual_opportunity_cost_capital_gain_real
        )

        annual_user_cost_real = (
            annual_interest_paid_real
            + annual_property_tax_real
            + annual_maintenance_real
            + annualized_purchase_cost_real
            + annual_box1_tax_effect_real
            + annual_total_opportunity_cost_real
            - annual_expected_capital_gain_real
        )
        monthly_user_cost_real = annual_user_cost_real / 12

        annual_cashflow_cost_real = (
            annual_mortgage_payment_real
            + annual_property_tax_real
            + annual_maintenance_real
            + annualized_purchase_cost_real
            + annual_box1_tax_effect_real
        )
        monthly_cashflow_cost_real = annual_cashflow_cost_real / 12

        annual_market_rent_cost_nominal = inputs.floor_area_m2 * market_rent_per_m2_nominal
        annual_market_rent_cost_real = annual_market_rent_cost_nominal / inflation_index
        monthly_market_rent_cost_real = annual_market_rent_cost_real / 12

        monthly_owner_user_cost_minus_renter_market_cost_real = (
            monthly_user_cost_real - monthly_market_rent_cost_real
        )

        gross_household_income_real = (
            inputs.gross_household_income_start * ((1 + inputs.annual_income_growth_rate) ** (year - 1))
        ) / inflation_index
        user_cost_income_ratio = annual_user_cost_real / gross_household_income_real

        rows.append(
            YearlyHousingCost(
                year=year,
                home_value_real=home_value_real,
                gross_household_income_real=gross_household_income_real,
                annual_interest_paid_real=annual_interest_paid_real,
                annual_principal_paid_real=annual_principal_paid_real,
                annual_mortgage_payment_real=annual_mortgage_payment_real,
                annual_property_tax_real=annual_property_tax_real,
                annual_maintenance_real=annual_maintenance_real,
                annualized_purchase_cost_real=annualized_purchase_cost_real,
                annual_expected_capital_gain_real=annual_expected_capital_gain_real,
                cumulative_principal_repaid_real=cumulative_principal_repaid_real,
                cumulative_capital_gain_real=cumulative_capital_gain_real,
                annual_opportunity_cost_principal_real=annual_opportunity_cost_principal_real,
                annual_opportunity_cost_capital_gain_real=annual_opportunity_cost_capital_gain_real,
                annual_total_opportunity_cost_real=annual_total_opportunity_cost_real,
                annual_box1_taxable_income_real=annual_box1_taxable_income_real,
                annual_box1_tax_effect_real=annual_box1_tax_effect_real,
                annual_user_cost_real=annual_user_cost_real,
                monthly_user_cost_real=monthly_user_cost_real,
                annual_cashflow_cost_real=annual_cashflow_cost_real,
                monthly_cashflow_cost_real=monthly_cashflow_cost_real,
                annual_market_rent_cost_real=annual_market_rent_cost_real,
                monthly_market_rent_cost_real=monthly_market_rent_cost_real,
                monthly_owner_user_cost_minus_renter_market_cost_real=monthly_owner_user_cost_minus_renter_market_cost_real,
                user_cost_income_ratio=user_cost_income_ratio,
            )
        )

        home_value_nominal = home_value_nominal * (1 + current_home_value_growth_rate)
        market_rent_per_m2_nominal = market_rent_per_m2_nominal * (1 + inputs.annual_market_rent_growth_rate)

    return rows
