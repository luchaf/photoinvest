import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pandas as pd

def calculate_total_lifetime_benefit(annual_benefits, years, maintenance_costs):
    return sum(annual_benefits[i] - maintenance_costs for i in range(years))

def calculate_annual_return(total_benefit, total_costs, years):
    average_annual_benefit = total_benefit / years
    annual_return_percent = (average_annual_benefit / total_costs) * 100
    return annual_return_percent

def calculate_roi(total_benefits, total_costs):
    return (total_benefits - total_costs) / total_costs * 100

# App-Konfiguration
st.title("Wirtschaftlichkeit einer Photovoltaik-Investition")

st.header("Annahme über aktuellen Strompreis und die Strompreisentwicklung")
electricity_price_buy = st.slider("Strompreis für den Bezug (Cent pro kWh)", 0.0, 50.0, 25.0, 0.1)
electricity_price_increase = st.slider("Jährliche Steigerung des Strompreises (%)", -10.0, 20.0, 2.0, 0.1) / 100
# Calculate future electricity prices
years = list(range(2024, 2055))
prices = [electricity_price_buy * (1 + electricity_price_increase)**(year - 2024) for year in years]
# Plot the electricity price development
fig_price = go.Figure()
fig_price.add_trace(go.Scatter(x=years, y=prices, mode='lines+markers', name='Strompreisentwicklung'))
fig_price.update_layout(title='Angenommene Strompreisentwicklung über die Jahre',
                        xaxis_title='Jahr',
                        yaxis_title='Strompreis (Cent pro kWh)',
                        hovermode='x unified')
st.plotly_chart(fig_price)

# Alte Anlage: Volleinspeisung
st.header("Alte Anlage: Volleinspeisung")
electricity_price_sell_old = st.slider("Vergütung für die alte Anlage (Cent pro kWh)", 0.0, 50.0, 8.2, 0.1)
old_annual_kwh = st.slider("Jahresproduktion der alten Anlage (kWh)", 0.0, 20000.0, 208.0, 10.0)
old_earnings = (old_annual_kwh * electricity_price_sell_old) / 100
maintenance_costs_old = st.slider("Jährliche Kosten (€) der alten Anlage (Wartung, Versicherung)", 0.0, 5000.0, 0.0, 10.0)
yearly_net_old_income = old_earnings - maintenance_costs_old

# Neue Anlage
st.header("Parameter und Annahmen über neue Photovoltaikanlage")
new_annual_kwh = st.slider("Jahresproduktion der neuen Anlage (kwh)", 0.0, 30000.0, 1800.0, 100.0)
lifetime_years = st.slider("Erwartete Lebensdauer der Photovoltaikanlage (Jahre)", 10, 30, 25, 1)
cost_new_plant = st.slider("Kosten für Einkauf und Montage der neuen Photovoltaikanlage (€)", 0.0, 50000.0, 2000.0, 100.0)
maintenance_costs_new = st.slider("Jährliche Wartungskosten (€) der neuen Anlage", 0.0, 500.0, 50.0, 10.0)
module_degradation = st.slider("Jährliche Degradation der PV-Module (%)", 0.0, 5.0, 0.25) / 100

# Neue Anlage: Volleinspeisung
st.header("Neue Anlage: Volleinspeisung")
electricity_price_sell_new_full = st.slider("Vergütung für die neue Anlage (Cent pro kWh)", 0.0, 30.0, 12.73, 0.1)
# Anpassungen für steigende Strompreise und Berechnungen
annual_benefits_full_feed = []
for year in range(lifetime_years):
    # Apply degradation to the kWh output of the new system each year
    effective_annual_kwh = new_annual_kwh * (1 - module_degradation)**year
    # Calculate earnings from the degraded output
    new_earnings = (effective_annual_kwh * electricity_price_sell_new_full) / 100
    # Calculate benefits
    annual_benefit_full = new_earnings - maintenance_costs_new
    annual_benefits_full_feed.append(annual_benefit_full)
# Gesamtnutzen und ROI Berechnungen für neue Anlagen
total_lifetime_benefit_full = calculate_total_lifetime_benefit(annual_benefits_full_feed, lifetime_years, maintenance_costs_new)
roi_full = calculate_roi(total_lifetime_benefit_full, cost_new_plant)
annual_return_full = calculate_annual_return(total_lifetime_benefit_full, cost_new_plant, lifetime_years)

# Einblendbare Tabelle für Volleinspeisung
with st.expander("Berechnungen für Volleinspeisung"):
    df_full_feed = pd.DataFrame({
        "Jahr": list(range(1, lifetime_years + 1)),
        "Effektive Jahresproduktion (kWh)": [new_annual_kwh * (1 - module_degradation)**year for year in range(lifetime_years)],
        "Jährliche Einnahmen (€)": [(new_annual_kwh * (1 - module_degradation)**year * electricity_price_sell_new_full) / 100 for year in range(lifetime_years)],
        "Jährliche Wartungskosten (€)": [maintenance_costs_new] * lifetime_years,
        "Jährlicher Nettogewinn (€)": annual_benefits_full_feed
    })
    st.write(df_full_feed)

st.write(f"Gesamter Nutzen über die Lebensdauer der Anlage (Volleinspeisung): {total_lifetime_benefit_full:.2f} €")
st.write(f"Return on Investment (ROI) über die Lebensdauer (Volleinspeisung): {roi_full:.2f} %")
st.write(f"Jährliche Rendite in Prozent der Investitionskosten (Volleinspeisung): {annual_return_full:.2f} %")

# Neue Anlage: Überschusseinspeisung
st.header("Neue Anlage: Überschusseinspeisung")
consumption_coverage_rate = st.slider("Annahme über Anteil des selbstverbrauchten Stroms (%)", 0, 100, 30) / 100
electricity_price_sell_new_surplus = st.slider("Vergütung für die neue Anlage (Cent pro kWh)", 0.0, 30.0, 8.2, 0.1)
new_self_consumed_kwh = new_annual_kwh * consumption_coverage_rate
new_surplus_kwh = new_annual_kwh - new_self_consumed_kwh
# Anpassungen für steigende Strompreise und Berechnungen
annual_benefits_surplus_feed = []
current_electricity_price = electricity_price_buy
for year in range(lifetime_years):
    # Apply degradation to the kWh output of the new system each year
    effective_surplus_kwh = new_surplus_kwh * (1 - module_degradation)**year
    # Calculate earnings from the degraded output
    annual_surplus_earnings = (effective_surplus_kwh * electricity_price_sell_new_surplus) / 100
    # Savings calculation based on non-degrading self-consumption rate but degrading production
    annual_savings = new_self_consumed_kwh * (1 - module_degradation)**year * current_electricity_price / 100
    # Calculate benefits
    annual_benefit_surplus = annual_surplus_earnings + annual_savings - maintenance_costs_new
    annual_benefits_surplus_feed.append(annual_benefit_surplus)
    current_electricity_price *= (1 + electricity_price_increase)
# Gesamtnutzen und ROI Berechnungen für neue Anlagen
total_lifetime_benefit_surplus = calculate_total_lifetime_benefit(annual_benefits_surplus_feed, lifetime_years, maintenance_costs_new)
roi_surplus = calculate_roi(total_lifetime_benefit_surplus, cost_new_plant)
annual_return_surplus = calculate_annual_return(total_lifetime_benefit_surplus, cost_new_plant, lifetime_years)

# Einblendbare Tabelle für Überschusseinspeisung
with st.expander("Berechnungen für Überschusseinspeisung"):
    df_surplus_feed = pd.DataFrame({
        "Jahr": list(range(1, lifetime_years + 1)),
        "Effektive Jahresproduktion (kWh)": [new_surplus_kwh * (1 - module_degradation)**year for year in range(lifetime_years)],
        "Selbst verbrauchte kWh": [new_self_consumed_kwh * (1 - module_degradation)**year for year in range(lifetime_years)],
        "Einnahmen aus Überschuss (€)": [(new_surplus_kwh * (1 - module_degradation)**year * electricity_price_sell_new_surplus) / 100 for year in range(lifetime_years)],
        "Ersparnisse durch Eigenverbrauch (€)": [new_self_consumed_kwh * (1 - module_degradation)**year * (electricity_price_buy * (1 + electricity_price_increase)**year) / 100 for year in range(lifetime_years)],
        "Jährliche Wartungskosten (€)": [maintenance_costs_new] * lifetime_years,
        "Jährlicher Nettogewinn (€)": annual_benefits_surplus_feed
    })
    st.write(df_surplus_feed)

st.write(f"Gesamter Nutzen über die Lebensdauer der Anlage (Überschusseinspeisung): {total_lifetime_benefit_surplus:.2f} €")
st.write(f"Return on Investment (ROI) über die Lebensdauer (Überschusseinspeisung): {roi_surplus:.2f} %")
st.write(f"Jährliche Rendite in Prozent der Investitionskosten (Überschusseinspeisung): {annual_return_surplus:.2f} %")

# Zinssatz für die Alternativinvestition
st.header("Alternativinvestition, z.B. Festgeld, ETF etc.")
alternative_interest_rate = st.slider("Jährlicher Zinssatz der Alternativinvestition (%)", 0.0, 20.0, 5.0, 0.1) / 100

# Kumulative Erträge berechnen
years = list(range(lifetime_years))
cumulative_old_earnings = [0]
for year in range(1, lifetime_years):
    cumulative_old_earnings.append(cumulative_old_earnings[-1] + yearly_net_old_income)

cumulative_earnings_full_feed = [-cost_new_plant]
cumulative_earnings_surplus_feed = [-cost_new_plant]
for year in range(1, lifetime_years):
    cumulative_earnings_full_feed.append(cumulative_earnings_full_feed[-1] + annual_benefits_full_feed[year - 1])
    cumulative_earnings_surplus_feed.append(cumulative_earnings_surplus_feed[-1] + annual_benefits_surplus_feed[year - 1])

# Berechnung der kumulativen Erträge der Alternativinvestition
cumulative_alternative_investment = [cost_new_plant]
for year in range(1, lifetime_years):
    last_amount = cumulative_alternative_investment[-1]
    new_amount = last_amount * (1 + alternative_interest_rate)
    cumulative_alternative_investment.append(new_amount)

# Plotting
fig = go.Figure()
fig.add_trace(go.Scatter(x=years, y=cumulative_old_earnings, mode='lines', name='Alte Anlage', line=dict(color='blue')))
fig.add_trace(go.Scatter(x=years, y=cumulative_earnings_full_feed, mode='lines', name='Neue Anlage - Volleinspeisung', line=dict(color='green')))
fig.add_trace(go.Scatter(x=years, y=cumulative_earnings_surplus_feed, mode='lines', name='Neue Anlage - Überschusseinspeisung', line=dict(color='orange')))
fig.add_trace(go.Scatter(x=years, y=cumulative_alternative_investment, mode='lines', name='Alternativinvestition', line=dict(color='red')))
fig.update_layout(title='Kumulierte Nettoerträge: Vergleich über die Jahre', xaxis_title='Jahre', yaxis_title='Kumulierte Nettoerträge (€)', hovermode='x unified')
st.plotly_chart(fig)
