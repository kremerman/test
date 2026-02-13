# Woonkosten-simulator (koop vs huur, in huidige prijzen)

Deze tool vergelijkt:
1. **Koop – user cost** (standaard gebruikskostenbenadering)
2. **Koop – cashflowkosten** (portemonnee-benadering)
3. **Huur – marktkostenbenchmark**

Alle uitkomsten zijn **reëel** (in huidige prijzen), dus gecorrigeerd voor inflatie.

## Wat zit in het model?

### User cost (koop)
User cost telt o.a. mee:
- rente
- OZB
- onderhoud
- geannualiseerde kosten koper
- box 1 belastingeffect
- opportunity cost (obv discontovoet)

En trekt af:
- verwachte waardestijging

### Opportunity cost (uitgesplitst)
- `annual_opportunity_cost_principal_real` = opportunity cost op cumulatieve aflossingen
- `annual_opportunity_cost_capital_gain_real` = opportunity cost op cumulatieve waardestijgingen

### Cashflowkosten (koop)
Cashflowkosten zijn de traditionele kasuitstroom:
- **wel** aflossingen
- **geen** waardestijging
- **geen** opportunity cost

### Box 1 fiscaliteit
Gesimuleerd via:
- eigenwoningforfait (`annual_imputed_rent_rate`)
- aftrekbare rente (`mortgage_interest_deductible_fraction`)
- belastingtarief (`mortgage_interest_tax_rate`)
- Wet Hillen-correctie (`wet_hillen_fraction`)

## Beleidswijzigingen
Vanaf een gekozen jaar kun je aanpassen:
- EWF (`post_change_annual_imputed_rent_rate`)
- HRA-aftrekbaarheid (`post_change_mortgage_interest_deductible_fraction`)
- effect op woningwaardegroei (`post_change_annual_home_value_growth_rate_delta`)

## Inflatie en huidige prijzen
Het model simuleert nominale paden en defleert alle uitkomsten met:
`(1 + annual_inflation_rate)^(jaar-1)`

Daarom zijn alle gerapporteerde bedragen vergelijkbaar in koopkracht van jaar 1.

## CLI
```bash
python3 src/main.py
```

Voorbeeld scenario:
```bash
python3 src/main.py \
  --annual-discount-rate 0.04 \
  --annual-inflation-rate 0.025 \
  --tax-policy-change-year 8 \
  --post-change-annual-imputed-rent-rate 0.006 \
  --post-change-mortgage-interest-deductible-fraction 0.6 \
  --post-change-annual-home-value-growth-rate-delta -0.005
```

## GUI
```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

GUI bevat sliders + grafieken voor:
- koop user cost vs koop cashflow vs markthuur
- opportunity cost opgesplitst
- box 1 effect en woningwaarde
