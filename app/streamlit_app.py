from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.housing_user_cost import HousingCostInput, simulate_yearly_housing_costs


st.set_page_config(page_title="Woonkosten Simulator", layout="wide")
st.title("Woonkosten Simulator")
st.caption("Koop (user cost + cashflow) vs markthuur, met box 1 fiscaliteit en beleidsscenario's.")
st.info("Alle getoonde bedragen zijn in huidige prijzen (reëel, gecorrigeerd voor inflatie).")

with st.sidebar:
    st.header("Woning en inkomen")
    floor_area_m2 = st.slider("Oppervlakte (m²)", 30, 250, 85, 1)
    purchase_price_per_m2 = st.slider("Verkoopprijs per m² (€)", 2000, 12000, 4500, 100)
    annual_mortgage_rate = st.slider("Hypotheekrente (% p.j.)", 0.0, 10.0, 4.0, 0.1) / 100
    annual_home_value_growth_rate = st.slider("Stijging woningwaarde (% p.j.)", -2.0, 8.0, 2.0, 0.1) / 100
    gross_household_income_start = st.slider("Bruto aanvangsinkomen (€)", 20_000, 200_000, 60_000, 1_000)
    annual_income_growth_rate = st.slider("Inkomensgroei (% p.j.)", 0.0, 8.0, 3.0, 0.1) / 100

    st.header("Prijzen en discontovoet")
    annual_inflation_rate = st.slider("Inflatie (% p.j.)", 0.0, 8.0, 2.0, 0.1) / 100
    annual_discount_rate = st.slider("Discontovoet / opportunity cost (% p.j.)", 0.0, 12.0, 3.0, 0.1) / 100

    st.header("Koopkosten en box 1")
    annual_property_tax_rate = st.slider("OZB (% WOZ)", 0.0, 1.0, 0.1, 0.01) / 100
    annual_maintenance_rate = st.slider("Onderhoud (% woningwaarde)", 0.0, 3.0, 1.0, 0.1) / 100
    annual_imputed_rent_rate = st.slider("Eigenwoningforfait (% WOZ)", 0.0, 2.0, 0.35, 0.01) / 100
    mortgage_interest_deductible_fraction = st.slider("Aftrekbaarheid HRA (%)", 0, 100, 100, 1) / 100
    mortgage_interest_tax_rate = st.slider("Belastingtarief box 1 (%)", 0.0, 60.0, 37.0, 0.5) / 100
    wet_hillen_fraction = st.slider("Wet Hillen correctie (%)", 0, 100, 0, 1) / 100

    st.header("Markthuurbenchmark")
    annual_market_rent_per_m2 = st.slider("Markthuur per m² per jaar (€)", 60, 600, 220, 5)
    annual_market_rent_growth_rate = st.slider("Markthuurstijging (% p.j.)", 0.0, 8.0, 2.0, 0.1) / 100

    st.header("Beleidswijziging")
    enable_policy_change = st.checkbox("Beleidswijziging aanzetten", value=False)
    tax_policy_change_year = None
    post_change_annual_imputed_rent_rate = None
    post_change_mortgage_interest_deductible_fraction = None
    post_change_annual_home_value_growth_rate_delta = 0.0

    if enable_policy_change:
        tax_policy_change_year = st.slider("Ingangsjaar beleidswijziging", 2, 30, 10, 1)
        post_change_annual_imputed_rent_rate = st.slider("EWF na wijziging (% WOZ)", 0.0, 2.0, 0.6, 0.01) / 100
        post_change_mortgage_interest_deductible_fraction = (
            st.slider("Aftrekbaarheid HRA na wijziging (%)", 0, 100, 70, 1) / 100
        )
        post_change_annual_home_value_growth_rate_delta = (
            st.slider("Effect op woningwaardegroei (procentpunt)", -3.0, 3.0, -0.5, 0.1) / 100
        )

inputs = HousingCostInput(
    floor_area_m2=floor_area_m2,
    purchase_price_per_m2=purchase_price_per_m2,
    annual_mortgage_rate=annual_mortgage_rate,
    annual_home_value_growth_rate=annual_home_value_growth_rate,
    gross_household_income_start=gross_household_income_start,
    annual_income_growth_rate=annual_income_growth_rate,
    annual_inflation_rate=annual_inflation_rate,
    annual_discount_rate=annual_discount_rate,
    annual_property_tax_rate=annual_property_tax_rate,
    annual_maintenance_rate=annual_maintenance_rate,
    annual_imputed_rent_rate=annual_imputed_rent_rate,
    mortgage_interest_deductible_fraction=mortgage_interest_deductible_fraction,
    mortgage_interest_tax_rate=mortgage_interest_tax_rate,
    wet_hillen_fraction=wet_hillen_fraction,
    annual_market_rent_per_m2=annual_market_rent_per_m2,
    annual_market_rent_growth_rate=annual_market_rent_growth_rate,
    tax_policy_change_year=tax_policy_change_year,
    post_change_annual_imputed_rent_rate=post_change_annual_imputed_rent_rate,
    post_change_mortgage_interest_deductible_fraction=post_change_mortgage_interest_deductible_fraction,
    post_change_annual_home_value_growth_rate_delta=post_change_annual_home_value_growth_rate_delta,
)

rows = simulate_yearly_housing_costs(inputs)
df = pd.DataFrame([row.__dict__ for row in rows])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Jaar 1 user cost/mnd", f"€ {df.iloc[0]['monthly_user_cost_real']:,.0f}")
c2.metric("Jaar 1 cashflow/mnd", f"€ {df.iloc[0]['monthly_cashflow_cost_real']:,.0f}")
c3.metric("Jaar 1 markthuur/mnd", f"€ {df.iloc[0]['monthly_market_rent_cost_real']:,.0f}")
c4.metric("Jaar 1 koop-huur", f"€ {df.iloc[0]['monthly_owner_user_cost_minus_renter_market_cost_real']:,.0f}")

fig_compare = px.line(
    df,
    x="year",
    y=["monthly_user_cost_real", "monthly_cashflow_cost_real", "monthly_market_rent_cost_real"],
    labels={"value": "€ per maand (reëel)", "year": "Jaar", "variable": "Reeks"},
    title="Vergelijking maandkosten: koop user cost, koop cashflow en markthuur",
)
st.plotly_chart(fig_compare, use_container_width=True)

fig_opp = px.line(
    df,
    x="year",
    y=["annual_opportunity_cost_principal_real", "annual_opportunity_cost_capital_gain_real"],
    labels={"value": "€ per jaar (reëel)", "year": "Jaar", "variable": "Component"},
    title="Opportunity cost uitgesplitst",
)
st.plotly_chart(fig_opp, use_container_width=True)

fig_box1 = px.line(
    df,
    x="year",
    y=["annual_box1_tax_effect_real", "annual_box1_taxable_income_real", "home_value_real"],
    labels={"value": "Waarde (reëel)", "year": "Jaar", "variable": "Reeks"},
    title="Box 1 effect en woningwaarde",
)
st.plotly_chart(fig_box1, use_container_width=True)

st.dataframe(
    df[
        [
            "year",
            "home_value_real",
            "monthly_user_cost_real",
            "monthly_cashflow_cost_real",
            "monthly_market_rent_cost_real",
            "monthly_owner_user_cost_minus_renter_market_cost_real",
            "annual_maintenance_real",
            "annual_opportunity_cost_principal_real",
            "annual_opportunity_cost_capital_gain_real",
            "annual_box1_tax_effect_real",
        ]
    ].round(2),
    use_container_width=True,
)
