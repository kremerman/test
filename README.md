# Woonkosten-simulator (koop vs markthuur)

Deze tool vergelijkt nu twee maatstaven:
1. **Koop: user cost of housing** (economische gebruikskosten)
2. **Huur: marktkosten benchmark** (markthuur per m² per jaar)

Daarnaast kun je **belastingbeleid** aanpassen (eigenwoningforfait, hypotheekrenteaftrek)
en een **effect op woningwaardegroei** invoeren.

## Snel starten (CLI)
```bash
python3 src/main.py
```

Voorbeeld met beleidswijziging vanaf jaar 8:
```bash
python3 src/main.py \
  --tax-policy-change-year 8 \
  --post-change-annual-imputed-rent-rate 0.006 \
  --post-change-mortgage-interest-deductible-fraction 0.6 \
  --post-change-annual-home-value-growth-rate-delta -0.005
```

Output:
- Terminal: eerste 5 jaren met koop vs huur
- CSV: `output/yearly_housing_costs.csv`

## GUI met sliders en grafieken
```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

In de GUI kun je direct schuiven met:
- woning/inkomen
- markthuurbenchmark
- belastingparameters (EWF/HRA)
- beleidswijziging + effect op woningwaardegroei

## Kernvariabelen (nieuw)
- `annual_market_rent_per_m2`: markthuur per m² per jaar
- `annual_market_rent_growth_rate`: jaarlijkse huurstijging
- `tax_policy_change_year`: jaar waarin beleid verandert
- `post_change_annual_imputed_rent_rate`: EWF na beleidswijziging
- `post_change_mortgage_interest_deductible_fraction`: aftrekbaarheid HRA na wijziging
- `post_change_annual_home_value_growth_rate_delta`: extra effect op waardegroei vanaf wijzigingsjaar

## Belangrijkste outputkolommen
- `monthly_user_cost_excluding_principal`: koop user cost / maand
- `monthly_market_rent_cost`: markthuur / maand
- `monthly_owner_user_cost_minus_renter_market_cost`: verschil koop-huur / maand
- `annual_tax_benefit_hra`: jaarlijks HRA-voordeel
- `annual_imputed_rent_tax`: jaarlijkse EWF-gerelateerde belastingpost
- `home_value`: woningwaarde door de tijd
