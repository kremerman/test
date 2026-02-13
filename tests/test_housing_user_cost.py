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
