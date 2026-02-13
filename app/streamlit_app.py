from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.housing_user_cost import HousingCostInput, simulate_yearly_housing_costs


st.set_page_config(page_title="Woonkosten Simulator", layout="wide")
st.title("Woonkosten Simulator")
st.caption("Koop (user cost) vs markthuur, inclusief belasting- en woningwaarde-scenario's.")

with st.sidebar:
    st.header("Woning en inkomen")
    floor_area_m2 = st.slider("Oppervlakte (m²)", min_value=30, max_value=250, value=85, step=1)
    purchase_price_per_m2 = st.slider(
        "Verkoopprijs per m² (€)", min_value=2000, max_value=12000, value=4500, step=100
    )
    annual_mortgage_rate = st.slider("Hypotheekrente (% p.j.)", 0.0, 10.0, 4.0, 0.1) / 100
    annual_home_value_growth_rate = st.slider("Stijging woningwaarde (% p.j.)", -2.0, 8.0, 2.0, 0.1) / 100
    gross_household_income_start = st.slider(
        "Bruto aanvangsinkomen huishouden (€)", min_value=20_000, max_value=200_000, value=60_000, step=1_000
    )
    annual_income_growth_rate = st.slider("CAO/inkomensgroei (% p.j.)", 0.0, 8.0, 3.0, 0.1) / 100

    st.header("Koopkosten")
    annual_property_tax_rate = st.slider("OZB (% WOZ)", 0.0, 1.0, 0.1, 0.01) / 100
    annual_maintenance_rate = st.slider("Onderhoud (% woningwaarde)", 0.0, 3.0, 1.0, 0.1) / 100
    annual_imputed_rent_rate = st.slider("Eigenwoningforfait (% WOZ)", 0.0, 2.0, 0.35, 0.01) / 100
    mortgage_interest_deductible_fraction = st.slider("Aftrekbaarheid HRA (%)", 0, 100, 100, 1) / 100
    mortgage_interest_tax_rate = st.slider("Belastingtarief HRA/EWF (%)", 0.0, 60.0, 37.0, 0.5) / 100

    st.header("Markthuurbenchmark")
    annual_market_rent_per_m2 = st.slider(
        "Markthuur per m² per jaar (€)", min_value=60, max_value=600, value=220, step=5
    )
    annual_market_rent_growth_rate = st.slider("Markthuurstijging (% p.j.)", 0.0, 8.0, 2.0, 0.1) / 100

    st.header("Beleidswijziging")
    enable_policy_change = st.checkbox("Beleidswijziging aanzetten", value=False)
    tax_policy_change_year = None
    post_change_annual_imputed_rent_rate = None
    post_change_mortgage_interest_deductible_fraction = None
    post_change_annual_home_value_growth_rate_delta = 0.0

    if enable_policy_change:
        tax_policy_change_year = st.slider("Ingangsjaar beleidswijziging", 2, 30, 10, 1)
        post_change_annual_imputed_rent_rate = (
            st.slider("EWF na wijziging (% WOZ)", 0.0, 2.0, 0.6, 0.01) / 100
        )
        post_change_mortgage_interest_deductible_fraction = (
            st.slider("Aftrekbaarheid HRA na wijziging (%)", 0, 100, 70, 1) / 100
        )
        post_change_annual_home_value_growth_rate_delta = (
            st.slider("Effect op woningwaardegroei (procentpunt p.j.)", -3.0, 3.0, -0.5, 0.1) / 100
        )

inputs = HousingCostInput(
    floor_area_m2=floor_area_m2,
    purchase_price_per_m2=purchase_price_per_m2,
    annual_mortgage_rate=annual_mortgage_rate,
    annual_home_value_growth_rate=annual_home_value_growth_rate,
    gross_household_income_start=gross_household_income_start,
    annual_income_growth_rate=annual_income_growth_rate,
    annual_property_tax_rate=annual_property_tax_rate,
    annual_maintenance_rate=annual_maintenance_rate,
    annual_imputed_rent_rate=annual_imputed_rent_rate,
    mortgage_interest_deductible_fraction=mortgage_interest_deductible_fraction,
    mortgage_interest_tax_rate=mortgage_interest_tax_rate,
    annual_market_rent_per_m2=annual_market_rent_per_m2,
    annual_market_rent_growth_rate=annual_market_rent_growth_rate,
    tax_policy_change_year=tax_policy_change_year,
    post_change_annual_imputed_rent_rate=post_change_annual_imputed_rent_rate,
    post_change_mortgage_interest_deductible_fraction=post_change_mortgage_interest_deductible_fraction,
    post_change_annual_home_value_growth_rate_delta=post_change_annual_home_value_growth_rate_delta,
)

rows = simulate_yearly_housing_costs(inputs)
df = pd.DataFrame([row.__dict__ for row in rows])

col1, col2, col3, col4 = st.columns(4)
col1.metric("Start woningwaarde", f"€ {inputs.floor_area_m2 * inputs.purchase_price_per_m2:,.0f}")
col2.metric("Jaar 1 koop user cost/mnd", f"€ {df.iloc[0]['monthly_user_cost_excluding_principal']:,.0f}")
col3.metric("Jaar 1 markthuur/mnd", f"€ {df.iloc[0]['monthly_market_rent_cost']:,.0f}")
col4.metric("Jaar 1 verschil koop-huur", f"€ {df.iloc[0]['monthly_owner_user_cost_minus_renter_market_cost']:,.0f}")

fig_compare = px.line(
    df,
    x="year",
    y=[
        "monthly_user_cost_excluding_principal",
        "monthly_market_rent_cost",
        "monthly_owner_user_cost_minus_renter_market_cost",
    ],
    labels={"value": "€ per maand", "year": "Jaar", "variable": "Reeks"},
    title="Koop vs markthuur benchmark",
)
st.plotly_chart(fig_compare, use_container_width=True)

fig_tax = px.line(
    df,
    x="year",
    y=["annual_tax_benefit_hra", "annual_imputed_rent_tax", "home_value"],
    labels={"value": "Waarde", "year": "Jaar", "variable": "Reeks"},
    title="Belastingcomponenten en woningwaarde",
)
st.plotly_chart(fig_tax, use_container_width=True)

fig_ratio = px.line(
    df,
    x="year",
    y="user_cost_income_ratio",
    labels={"user_cost_income_ratio": "Ratio", "year": "Jaar"},
    title="User cost als aandeel van bruto inkomen",
)
st.plotly_chart(fig_ratio, use_container_width=True)

st.subheader("Data")
st.dataframe(
    df[
        [
            "year",
            "home_value",
            "monthly_user_cost_excluding_principal",
            "monthly_market_rent_cost",
            "monthly_owner_user_cost_minus_renter_market_cost",
            "annual_tax_benefit_hra",
            "annual_imputed_rent_tax",
            "annual_interest_paid",
            "annual_property_tax",
            "annual_maintenance",
            "user_cost_income_ratio",
        ]
    ].round(2),
    use_container_width=True,
)
