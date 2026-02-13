# Woonkosten-simulator (simpel startmodel)

Dit project bevat een **eerste simpele tool** om per jaar de maandelijkse woonkosten te berekenen voor:
- een **annuïtaire hypotheek**
- **30 jaar looptijd**
- **vaste rente**
- focus op **user cost of housing** (gebruikskosten)

> Geen onzekerheid/Monte Carlo in deze versie.

## Wat rekent de tool uit?
Per jaar (1 t/m 30):
- maandelijkse gebruikskosten (**exclusief aflossing**)
- maandelijkse cash-out (**inclusief aflossing**)

Belangrijkste onderdelen in het model:
- hypotheekrente
- OZB (onroerendezaakbelasting)
- onderhoud
- eigenwoningforfait (vereenvoudigd)
- HRA-belastingvoordeel
- rendementseis op woningwaarde
- verwachte waardestijging (als negatieve kostenpost)
- geannualiseerde kosten koper

## Logische variabele namen
In `src/housing_user_cost.py` staat alles in duidelijke variabelen, o.a.:
- `floor_area_m2`
- `purchase_price_per_m2`
- `annual_mortgage_rate`
- `annual_home_value_growth_rate`
- `gross_household_income_start`
- `annual_property_tax_rate`
- `annual_maintenance_rate`
- `annual_required_return_rate`
- `annual_imputed_rent_rate`
- `mortgage_interest_deductible_fraction`
- `mortgage_interest_tax_rate`
- `wet_hillen_fraction`

## Projectstructuur
- `src/housing_user_cost.py` – rekenmodel
- `src/main.py` – simpele CLI die CSV exporteert
- `tests/test_housing_user_cost.py` – basistests

## Snel starten
```bash
python3 src/main.py
```

Met eigen parameters:
```bash
python3 src/main.py \
  --floor-area-m2 95 \
  --purchase-price-per-m2 5200 \
  --annual-mortgage-rate 0.038 \
  --annual-home-value-growth-rate 0.02 \
  --gross-household-income-start 70000 \
  --annual-income-growth-rate 0.03
```

Output:
- console-preview van eerste 5 jaren
- CSV op `output/yearly_housing_costs.csv`

## Opmerkingen over modelkeuzes
Dit is bewust een **startversie**. Een paar onderdelen zijn vereenvoudigd:
- Wet Hillen wordt als eenvoudige kortingsfactor gemodelleerd.
- Fiscale regels zijn versimpeld tot percentage-benadering.
- Geen huur-/WWS-logica in deze eerste versie.

Als volgende stap kunnen we hier direct grafieken aan toevoegen (bijv. met Plotly/Streamlit).
