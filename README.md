# Woonkosten-simulator (simpel uitgelegd)

Dit project is een **rekenmachine** voor koopwoningen.
Je geeft een paar invoerwaarden (zoals m2-prijs en rente), en het model berekent voor elk jaar:

1. **maandelijkse gebruikskosten** (user cost, zonder aflossing)
2. **maandelijkse cash-out** (wat er echt uit je bankrekening gaat, mét aflossing)

> Deze versie is bewust simpel: annuïtaire hypotheek, 30 jaar, vaste rente, geen onzekerheidssimulatie.

---

## 1) Hoe je het gebruikt (in 20 seconden)

```bash
python3 src/main.py
```

Daarna krijg je:
- een korte tabel in de terminal (eerste 5 jaren)
- een bestand `output/yearly_housing_costs.csv` met alle 30 jaren

Eigen scenario draaien:

```bash
python3 src/main.py \
  --floor-area-m2 95 \
  --purchase-price-per-m2 5200 \
  --annual-mortgage-rate 0.038 \
  --annual-home-value-growth-rate 0.02 \
  --gross-household-income-start 70000 \
  --annual-income-growth-rate 0.03
```

---

## 2) Wat gebeurt er intern? (stap voor stap)

### Stap A — Woningwaarde en lening
- `home_value_start = floor_area_m2 * purchase_price_per_m2`
- `mortgage_principal = home_value_start * (1 - down_payment_fraction)`

### Stap B — Annuïteit per maand
Met rente + looptijd berekent het model één vaste maandbetaling.
Die bestaat elke maand uit:
- rente-deel
- aflossings-deel

In het begin is rente groot en aflossing klein; later draait dat om.

### Stap C — Per jaar kostencomponenten
Voor elk jaar telt het model o.a. op:
- betaalde hypotheekrente
- OZB (`annual_property_tax_rate * home_value`)
- onderhoud (`annual_maintenance_rate * home_value`)
- eigenwoningforfait-achtige post (`annual_imputed_rent_rate * home_value`, versimpeld)
- rendementseis op eigen vermogen (`annual_required_return_rate * home_value`)
- geannualiseerde kosten koper

En haalt er o.a. af:
- HRA-voordeel
- verwachte waardestijging (`annual_home_value_growth_rate * home_value`)

### Stap D — Twee uitkomsten per maand
1. `monthly_user_cost_excluding_principal`
   - economisch gebruikskostenbegrip
   - **zonder** aflossing

2. `monthly_cash_outflow_including_principal`
   - kasuitstroom
   - **met** aflossing

---

## 3) Waarom zijn er twee maandbedragen?

Omdat **aflossing geen “verbruikskosten” is** maar vermogensopbouw.

- User cost: wat wonen je “kost” als economische dienst.
- Cash-out: wat je feitelijk betaalt per maand.

Daarom is cash-out vaak hoger dan user cost in dit model.

---

## 4) Belangrijkste variabelen (met normale taal)

- `floor_area_m2`: aantal m2 woning
- `purchase_price_per_m2`: koopprijs per m2
- `annual_mortgage_rate`: hypotheekrente per jaar
- `annual_home_value_growth_rate`: verwachte woningwaardegroei per jaar
- `annual_property_tax_rate`: OZB-percentage
- `annual_maintenance_rate`: onderhoud als % van woningwaarde
- `annual_required_return_rate`: rendementseis op gebonden kapitaal
- `annual_imputed_rent_rate`: forfaitaire “huur”-component
- `mortgage_interest_deductible_fraction`: deel rente aftrekbaar
- `mortgage_interest_tax_rate`: belastingtarief voor aftrek/forfait
- `wet_hillen_fraction`: vereenvoudigde Hillen-correctie

---

## 5) Bestanden: wat moet je als beginner openen?

1. `src/main.py`
   - startpunt: leest CLI-argumenten, roept model aan, schrijft CSV

2. `src/housing_user_cost.py`
   - hier staat alle rekenlogica
   - begin met `HousingCostInput` en daarna `simulate_yearly_housing_costs`

3. `tests/test_housing_user_cost.py`
   - controleert dat basisgedrag klopt (30 jaren, rente daalt in de tijd, 0%-rente test)

---

## 6) Als je nog steeds twijfelt: mini-checklist

- Run eerst standaard: `python3 src/main.py`
- Open daarna CSV en kijk naar kolommen `year`, `monthly_user_cost_excluding_principal`, `monthly_cash_outflow_including_principal`
- Verander één parameter (bijv. rente naar 5%) en run opnieuw
- Vergelijk de twee CSV’s

Dan “voel” je snel wat het model doet.
