from housing_user_cost import HousingCostInput, simulate_yearly_housing_costs


def test_returns_30_years_by_default() -> None:
    rows = simulate_yearly_housing_costs(HousingCostInput(floor_area_m2=80, purchase_price_per_m2=4000))
    assert len(rows) == 30


def test_interest_declines_over_time_in_annuity() -> None:
    rows = simulate_yearly_housing_costs(HousingCostInput(floor_area_m2=80, purchase_price_per_m2=4000))
    assert rows[0].annual_interest_paid > rows[-1].annual_interest_paid


def test_zero_rate_has_no_interest_component() -> None:
    rows = simulate_yearly_housing_costs(
        HousingCostInput(
            floor_area_m2=80,
            purchase_price_per_m2=4000,
            annual_mortgage_rate=0.0,
        )
    )
    total_interest = sum(r.annual_interest_paid for r in rows)
    assert total_interest == 0.0


def test_market_rent_benchmark_is_in_output() -> None:
    rows = simulate_yearly_housing_costs(
        HousingCostInput(
            floor_area_m2=100,
            purchase_price_per_m2=4000,
            annual_market_rent_per_m2=240,
            annual_market_rent_growth_rate=0.0,
        )
    )
    assert rows[0].monthly_market_rent_cost == 2000.0


def test_tax_policy_change_reduces_hra_after_change_year() -> None:
    rows = simulate_yearly_housing_costs(
        HousingCostInput(
            floor_area_m2=80,
            purchase_price_per_m2=4000,
            tax_policy_change_year=2,
            post_change_mortgage_interest_deductible_fraction=0.0,
        )
    )
    assert rows[0].annual_tax_benefit_hra > 0
    assert rows[1].annual_tax_benefit_hra == 0


def test_policy_change_home_value_growth_delta_changes_later_home_value() -> None:
    base_rows = simulate_yearly_housing_costs(
        HousingCostInput(
            floor_area_m2=80,
            purchase_price_per_m2=4000,
            annual_home_value_growth_rate=0.02,
        )
    )
    policy_rows = simulate_yearly_housing_costs(
        HousingCostInput(
            floor_area_m2=80,
            purchase_price_per_m2=4000,
            annual_home_value_growth_rate=0.02,
            tax_policy_change_year=2,
            post_change_annual_home_value_growth_rate_delta=-0.02,
        )
    )
    assert policy_rows[-1].home_value < base_rows[-1].home_value
