from housing_user_cost import HousingCostInput, simulate_yearly_housing_costs


def test_returns_30_years_by_default() -> None:
    rows = simulate_yearly_housing_costs(HousingCostInput(floor_area_m2=80, purchase_price_per_m2=4000))
    assert len(rows) == 30


def test_interest_declines_over_time_in_annuity() -> None:
    rows = simulate_yearly_housing_costs(HousingCostInput(floor_area_m2=80, purchase_price_per_m2=4000))
    assert rows[0].annual_interest_paid_real > rows[-1].annual_interest_paid_real


def test_market_rent_benchmark_is_in_output() -> None:
    rows = simulate_yearly_housing_costs(
        HousingCostInput(
            floor_area_m2=100,
            purchase_price_per_m2=4000,
            annual_market_rent_per_m2=240,
            annual_market_rent_growth_rate=0.0,
        )
    )
    assert rows[0].monthly_market_rent_cost_real == 2000.0


def test_cashflow_equals_wallet_logic_without_oppcost_and_no_capital_gain() -> None:
    rows = simulate_yearly_housing_costs(
        HousingCostInput(
            floor_area_m2=80,
            purchase_price_per_m2=4000,
            annual_home_value_growth_rate=0.0,
            annual_discount_rate=0.0,
            annual_market_rent_growth_rate=0.0,
            annual_inflation_rate=0.0,
        )
    )
    row = rows[0]
    expected = (
        row.annual_mortgage_payment_real
        + row.annual_property_tax_real
        + row.annual_maintenance_real
        + row.annualized_purchase_cost_real
        + row.annual_box1_tax_effect_real
    )
    assert abs(row.annual_cashflow_cost_real - expected) < 1e-6


def test_user_cost_includes_oppcost_and_subtracts_expected_appreciation() -> None:
    rows = simulate_yearly_housing_costs(
        HousingCostInput(
            floor_area_m2=90,
            purchase_price_per_m2=4500,
            annual_discount_rate=0.04,
            annual_home_value_growth_rate=0.03,
            annual_inflation_rate=0.0,
        )
    )
    row = rows[0]
    expected = (
        row.annual_interest_paid_real
        + row.annual_property_tax_real
        + row.annual_maintenance_real
        + row.annualized_purchase_cost_real
        + row.annual_box1_tax_effect_real
        + row.annual_total_opportunity_cost_real
        - row.annual_expected_capital_gain_real
    )
    assert abs(row.annual_user_cost_real - expected) < 1e-6


def test_less_hra_deductibility_makes_buy_relatively_more_expensive_vs_rent() -> None:
    base = simulate_yearly_housing_costs(
        HousingCostInput(
            floor_area_m2=85,
            purchase_price_per_m2=4500,
            annual_market_rent_per_m2=220,
            annual_market_rent_growth_rate=0.02,
        )
    )
    policy = simulate_yearly_housing_costs(
        HousingCostInput(
            floor_area_m2=85,
            purchase_price_per_m2=4500,
            annual_market_rent_per_m2=220,
            annual_market_rent_growth_rate=0.02,
            tax_policy_change_year=2,
            post_change_mortgage_interest_deductible_fraction=0.0,
        )
    )
    assert policy[2].monthly_owner_user_cost_minus_renter_market_cost_real > base[2].monthly_owner_user_cost_minus_renter_market_cost_real


def test_higher_ewf_makes_buy_relatively_more_expensive_vs_rent() -> None:
    base = simulate_yearly_housing_costs(
        HousingCostInput(floor_area_m2=85, purchase_price_per_m2=4500, annual_imputed_rent_rate=0.0035)
    )
    high_ewf = simulate_yearly_housing_costs(
        HousingCostInput(floor_area_m2=85, purchase_price_per_m2=4500, annual_imputed_rent_rate=0.01)
    )
    assert high_ewf[0].monthly_owner_user_cost_minus_renter_market_cost_real > base[0].monthly_owner_user_cost_minus_renter_market_cost_real


def test_higher_inflation_reduces_late_year_real_costs() -> None:
    low = simulate_yearly_housing_costs(
        HousingCostInput(floor_area_m2=85, purchase_price_per_m2=4500, annual_inflation_rate=0.0)
    )
    high = simulate_yearly_housing_costs(
        HousingCostInput(floor_area_m2=85, purchase_price_per_m2=4500, annual_inflation_rate=0.04)
    )
    assert high[-1].monthly_cashflow_cost_real < low[-1].monthly_cashflow_cost_real
