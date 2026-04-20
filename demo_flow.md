# EPOWER Energy Intelligence Demo — Questions

A guided walkthrough of EPOWER's AI-powered energy intelligence platform. Each act builds on the previous one, progressing from basic business data to the core VPP value proposition.

**EPOWER Energy** is a German energy retailer (20K customers) pursuing a 360° energy strategy: Supply, Generate, Store, Heat, Drive, Optimize. The demo's centerpiece is the **ePulse Virtual Power Plant (VPP)** — ~4,050 residential battery systems that charge when electricity is cheap and discharge when expensive, creating arbitrage value split 70% customer / 30% EPOWER.

---

### Act 1: Know Your Business

> Start with the basics. Show how the agent understands EPOWER's core business data across 6 product categories (Solar, Battery Storage, Heat Pumps, E-Mobility, Smart Home, Electricity/Gas tariffs).

**1. Product Portfolio**

*"Gib mir einen Überblick über unser Produktportfolio. Welche Kategorien und Produkte bieten wir an?"*

> Uses: `energy_sales_analyst` → product_dim (15 products, 6 categories, CAPEX/OPEX pricing)

**2. Sales Performance**

*"Zeige mir die Top 5 Produkte nach Umsatz in 2024."*

> Uses: `energy_sales_analyst` → sales_fact + product_dim (~80K contracts)

**3. Customer Segments**

*"How many residential vs. business customers do we have? What's the revenue split?"*

> Uses: `energy_sales_analyst` → customer_dim + sales_fact (20K customers)

---

### Act 2: Customer Intelligence

> Drill into customer behavior — combining structured data with document search. This demonstrates how the agent seamlessly routes between SQL (Cortex Analyst) and RAG (Cortex Search).

**4. Consumption Patterns**

*"Was ist der durchschnittliche Stromverbrauch für Kunden mit Wärmepumpen im Vergleich zu Kunden ohne?"*

> Uses: `customer_energy_analyst` → billing_history + customer_products (heat pump owners vs. non-owners)

**5. Service Insights**

*"Zeige mir die häufigsten Beschwerde-Themen bei Service-Tickets mit negativem Sentiment."*

> Uses: `service_analyst` → service_logs (~10K tickets with topic, sentiment, priority)

**6. Document + Data (RAG)**

*"Welche Kunden haben hohen Verbrauch über 6000 kWh und welche Energiespartipps aus unserer Dokumentation wären relevant?"*

> Uses: `billing_analyst` (SQL) + `energy_docs_search` (RAG) — combines structured data with unstructured documents

---

### Act 3: The Virtual Power Plant

> Transition to the VPP — this is where it gets interesting. The demo has 90 days of real EPEX day-ahead prices and price-reactive IoT telemetry from ~4,500 battery devices.

**7. VPP Fleet Overview**

*"How many devices are enrolled in our ePulse Virtual Power Plant? Show the breakdown by region."*

> Uses: `vpp_telemetry_analyst` → fct_epulse_telemetry / stg_devices

**8. Day-Ahead Prices**

*"What were the day-ahead electricity prices for the last 7 days? Show the price range and average."*

> Uses: `market_prices_analyst` → mart_day_ahead_prices (real EPEX DE-LU spot prices, 15-min intervals)

**9. Price vs. Battery Correlation**

*"Show me how battery state-of-charge correlates with day-ahead prices. Do VPP devices charge when prices are low?"*

> Uses: `vpp_telemetry_analyst` + `market_prices_analyst` — this is the key insight: batteries react to real market prices

**Follow-up:** *"Visualize this as a chart — battery SOC vs. price over the last 24 hours."*

---

### Act 4: Smart Energy Strategy

> The payoff — show how price-reactive battery management creates measurable financial value. The dbt pipeline (`mart_vpp_price_optimization`) joins telemetry with prices to compute arbitrage margins.

**10. Arbitrage Margins**

*"What is the total battery arbitrage margin across all VPP devices? Break it down by price zone (negative, low, medium, high)."*

> Uses: `vpp_telemetry_analyst` → mart_vpp_price_optimization (price_zone, net_margin_eur)

**11. Customer & Company Value**

*"Show me the average daily margin per VPP customer and EPOWER's share. What's the projected annual value?"*

> Uses: `vpp_telemetry_analyst` → mart_vpp_price_optimization (customer_margin_eur, epower_margin_eur)

**12. The Big Picture (wrap-up)**

*"Wie funktioniert das ePulse VPP Programm und welche Vorteile bietet es unseren Kunden?"*

> Uses: `energy_docs_search` (RAG — VPP Program Guide) — finishes with a document-grounded summary

---

## Additional Questions by Domain

### Sales & Contracts
- *"Which region has the highest sales for Heat Pump products?"*
- *"Zeige mir die monatlichen Vertragszahlen für 2024."*
- *"What's the average contract value for Solar installations vs. Battery Storage?"*

### Billing & Consumption
- *"Welche Kunden mit Solaranlagen haben den höchsten Stromverbrauch?"*
- *"Vergleiche den durchschnittlichen Stromverbrauch zwischen Kunden mit und ohne Wärmepumpe."*
- *"Show me the top 10 customers by electricity consumption this quarter."*

### Customer Service
- *"What are the most common service ticket topics? Show priority distribution."*
- *"Welche Tickets sind noch offen und haben hohe Priorität?"*
- *"How has customer sentiment changed over the last 6 months?"*

### Documents (RAG)
- *"Was sind die Voraussetzungen für die Wärmepumpen-Förderung 2024?"*
- *"Erkläre mir, wie ich meine Stromrechnung lesen kann."*
- *"Was ist der Unterschied zwischen einer Luft-Wasser und einer Sole-Wasser Wärmepumpe?"*

### VPP & Energy Market
- *"Which regions have the highest solar yield in the VPP fleet?"*
- *"Wann waren die Strompreise in den letzten 30 Tagen am höchsten?"*
- *"Show me the VPP fleet's net grid flow by hour of day — when do we export the most?"*
- *"What's the average battery state-of-charge during negative price hours?"*

### HR & Workforce
- *"Wie viele Mitarbeiter haben wir pro Abteilung? Wie hoch ist die Fluktuation im Vertrieb?"*
- *"What is the average salary by department?"*

---

## Tips for Presenters

- **Language**: The agent handles German and English seamlessly — mix languages to show multilingual capabilities
- **Follow-ups**: Ask follow-up questions naturally (e.g., "Break that down by region", "Show that as a chart")
- **Charts**: The agent can generate visualizations — ask for charts when showing trends or comparisons
- **Documents**: Questions about policies, technical guides, or FAQs trigger RAG search automatically
- **The Story Arc**: Acts 1-2 establish the business context, Act 3 introduces the VPP innovation, Act 4 proves its financial value — don't rush through, let the audience absorb each insight
- **Key Moment**: Question 9 (price vs. battery correlation) is the "aha" — it proves the VPP actually works with real market data

---

## Technical Components

| Component | Details |
|-----------|---------|
| **Database** | `EPOWER_DEMO` (EPOWER_BRONZE / EPOWER_SILVER / EPOWER_GOLD / EPOWER_OPS) |
| **Warehouse** | `EPOWER_COMPUTE` (SMALL) |
| **Semantic Views** | 7 (Sales, Billing, Service, Customer Energy, HR, VPP Telemetry, Market Prices) |
| **Cortex Search** | 9 services (4 document RAG + 5 high-cardinality column lookup) |
| **Agent** | `EPOWER_AGENT` (orchestrates all Semantic Views + Search Services) |
| **dbt Project** | `EPOWER_ANALYTICS_PROJECT` (6 models, medallion architecture Bronze → Silver → Gold) |
| **Daily Task** | `TASK_DAILY_DATA_REFRESH` (17:00 CET: prices → telemetry → dbt) |
| **MCP Server** | `EPOWER_MCP_SERVER` (12 tools: 1 agent + 7 analyst + 4 search) |

---

*EPOWER Energy Intelligence Demo — Powered by Snowflake Cortex*
