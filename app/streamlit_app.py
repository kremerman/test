from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.housing_user_cost import HousingCostInput, simulate_yearly_housing_costs


st.set_page_config(page_title="Woonkosten Simulator", layout="wide")
st.title("Woonkosten Simulator")
st.caption("Simpel model: annuïtaire hypotheek (30 jaar), vaste rente, user cost of housing.")

with st.sidebar:
    st.header("Inputs")
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
    annual_property_tax_rate = st.slider("OZB (% WOZ)", 0.0, 1.0, 0.1, 0.01) / 100
    annual_maintenance_rate = st.slider("Onderhoud (% woningwaarde)", 0.0, 3.0, 1.0, 0.1) / 100

inputs = HousingCostInput(
    floor_area_m2=floor_area_m2,
    purchase_price_per_m2=purchase_price_per_m2,
    annual_mortgage_rate=annual_mortgage_rate,
    annual_home_value_growth_rate=annual_home_value_growth_rate,
    gross_household_income_start=gross_household_income_start,
    annual_income_growth_rate=annual_income_growth_rate,
    annual_property_tax_rate=annual_property_tax_rate,
    annual_maintenance_rate=annual_maintenance_rate,
)

rows = simulate_yearly_housing_costs(inputs)
df = pd.DataFrame([row.__dict__ for row in rows])

col1, col2, col3 = st.columns(3)
col1.metric("Start woningwaarde", f"€ {inputs.floor_area_m2 * inputs.purchase_price_per_m2:,.0f}")
col2.metric("Jaar 1 user cost / maand", f"€ {df.iloc[0]['monthly_user_cost_excluding_principal']:,.0f}")
col3.metric("Jaar 1 cash-out / maand", f"€ {df.iloc[0]['monthly_cash_outflow_including_principal']:,.0f}")

fig_costs = px.line(
    df,
    x="year",
    y=["monthly_user_cost_excluding_principal", "monthly_cash_outflow_including_principal"],
    labels={"value": "€ per maand", "year": "Jaar", "variable": "Reeks"},
    title="Maandlasten over tijd",
)
st.plotly_chart(fig_costs, use_container_width=True)

fig_components = px.line(
    df,
    x="year",
    y=["annual_interest_paid", "annual_property_tax", "annual_maintenance", "annual_tax_benefit_hra"],
    labels={"value": "€ per jaar", "year": "Jaar", "variable": "Component"},
    title="Belangrijkste jaarlijkse componenten",
)
st.plotly_chart(fig_components, use_container_width=True)

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
            "monthly_user_cost_excluding_principal",
            "monthly_cash_outflow_including_principal",
            "annual_interest_paid",
            "annual_principal_paid",
            "annual_property_tax",
            "annual_maintenance",
            "annual_tax_benefit_hra",
            "user_cost_income_ratio",
        ]
    ].round(2),
    use_container_width=True,
)
