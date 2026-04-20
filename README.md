# 📊 E-Commerce Executive & Operations Analytics Suite
### Power BI Portfolio Project — Built with an AI-Assisted Workflow

![Status](https://img.shields.io/badge/Status-In%20Progress-yellow)
![Power BI](https://img.shields.io/badge/Power%20BI-Desktop-F2C811?logo=powerbi)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)
![Figma](https://img.shields.io/badge/Figma-Design-F24E1E?logo=figma)

A fully end-to-end Power BI portfolio project simulating a mid-size direct-to-consumer e-commerce brand. Built to demonstrate real-world BI capability across data modeling, DAX, visual design, and analytics storytelling — for both full-time employment and freelance client pitches.

---

## 📸 Preview

### Executive Summary
> *KPI cards, rolling revenue trend, gauge visuals, and year/category slicers — all on a custom Figma-designed dark navy background.*

![Executive Summary](assets/executive_summary.png)

---

## 🗂️ Report Pages

| Page | Status | Description |
|---|---|---|
| Executive Summary | ✅ Complete | Revenue KPIs, Pulse Chart with rolling revenue, operational gauges |
| Sales Analysis | 🚧 In Progress | Channel, category, region breakdown, seasonal peaks |
| Customer Analytics | 🚧 In Progress | LTV:CAC, segments, acquisition channels, regional map |
| Operations | 🚧 In Progress | Fulfillment trends, return rate, refund analysis |

---

## 🏗️ Data Model

Star schema with 2 fact tables and 4 dimension tables — all data generated synthetically using Python.

```
dim_date ──────┐
dim_channel ───┤
dim_customer ──┼──► fact_orders ◄──► fact_returns
dim_product ───┘
```

| Table | Rows | Description |
|---|---|---|
| `fact_orders` | 6,000 | Order-grain, revenue totals, fulfillment metrics |
| `fact_returns` | 732 | Return events linked to orders |
| `dim_date` | 1,096 | Full date table, 2022–2024 |
| `dim_customer` | 800 | Segments, LTV, CAC, acquisition channel |
| `dim_product` | 120 | Category, subcategory, margin data |
| `dim_channel` | 8 | Acquisition channels with avg CAC |

**Key modeling notes:**
- FK column in fact tables is `PrimaryProductID` (not `ProductID`) — explicit relationship required
- `fact_returns → dim_date` relationship is **inactive** — activated via `USERELATIONSHIP()` in DAX
- `ReturnID` has non-contiguous gaps (expected, acceptable as unique key)

---

## 📐 DAX Measures Library

**Revenue & Volume**
- `Total Revenue`, `Total Orders`, `Avg Order Value`, `Total Quantity`

**Margin**
- `Total Gross Margin`, `Gross Margin %`

**Returns**
- `Total Returns`, `Return Rate %`, `Total Refunds`, `Avg Processing Days`

**Customers**
- `Unique Customers`, `Avg LTV`, `Avg LTV CAC Ratio`

**Fulfillment**
- `On-Time Delivery %`, `Avg Fulfillment Days`

**Time Intelligence**
- `Revenue MTD`, `Revenue YTD`, `Revenue YoY %`, `Revenue MoM %`
- `Revenue Rolling 3M`, `Revenue Rolling 12M`

**KPI Targets**
- `On-Time Delivery Target` (90% SLA benchmark)
- `Total Returns Target` (12% of orders)
- `Avg Fulfillment Days Target` (3.5 days)
- `Unique Customers Target` (YoY comparison)

---

## 🎨 Design

Custom report backgrounds designed in **Figma** at 1280×720px — exported as PNG and imported as canvas backgrounds in Power BI.

**Design system:**
- Background: `#0C101F` (deep navy)
- Primary accent: `#1E77FF` (vivid blue)
- Secondary accent: `#00D9FF` (electric cyan)
- Positive: `#1EE68E` (green)
- Negative: `#FF4E4E` (red)
- Text: `#FFFFFF` / `#7B9FFF` (dimmed)

Each page uses a unique accent colour for navigation orientation:
- Executive Summary → Blue
- Sales Analysis → Blue
- Customer Analytics → Cyan
- Operations → Amber

Figma file: [E-Commerce Analytics Backgrounds](https://www.figma.com/design/81z5tp1NjVxhBFqwHNaC10)

---

## 🔢 Benchmarks (from Perplexity Pro research)

| KPI | Target | Actual |
|---|---|---|
| Average Order Value | $130–160 | $149.16 ✅ |
| Return Rate | ~12% | 12.20% ✅ |
| On-Time Delivery | 85–92% | 88.53% ✅ |
| LTV:CAC Ratio | 2:1–4:1 | Varies by segment ✅ |
| Gross Margin | 50–65% | 55.46% ✅ |

---

## 🛠️ Tech Stack

| Tool | Role |
|---|---|
| **Power BI Desktop** | Report building, DAX, data modeling |
| **Python** | Synthetic data generation (pandas, faker, numpy) |
| **Figma** | Custom background design (via MCP) |
| **Claude** | DAX writing, strategy, project planning |
| **ChatGPT** | DAX debugging, M query work |
| **Perplexity Pro** | Industry research and KPI benchmarking |
| **GitHub Copilot / Cursor** | Python data generation scripts |

---

## 📁 Repository Structure

```
powerbi-ecommerce-analytics/
│
├── E-Commerce Dashboard.pbix       # Power BI report file
├── ecommerce_analytics_theme.json  # Custom Power BI theme
├── generate_ecommerce_data_v2.py   # Python data generator
│
├── data/
│   ├── dim_date.csv
│   ├── dim_channel.csv
│   ├── dim_customer.csv
│   ├── dim_product.csv
│   ├── fact_orders.csv
│   └── fact_returns.csv
│
└── assets/
    ├── executive_summary.png
    ├── sales_analysis.png
    ├── customer_analytics.png
    └── operations.png
```

---

## 🚀 How to Run

1. Clone the repository
2. Open `E-Commerce Dashboard.pbix` in Power BI Desktop
3. If prompted to reconnect data, point Power BI to the `/data` folder
4. Apply the theme: **View → Themes → Browse for themes** → select `ecommerce_analytics_theme.json`

**Python data regeneration (optional):**
```bash
pip install pandas numpy faker
python generate_ecommerce_data_v2.py
```

---

## 📅 Project Status

- [x] Data generation and validation
- [x] Star schema and relationships
- [x] Full DAX measures library
- [x] Custom Figma backgrounds (all 4 pages)
- [x] Executive Summary page — complete
- [ ] Sales Analysis page — in progress
- [ ] Customer Analytics page — in progress
- [ ] Operations page — in progress
- [ ] Slicers and cross-page interactions
- [ ] Page navigation buttons
- [ ] Portfolio documentation and walkthrough video

**Target completion:** May 1, 2026

---

## 👤 About

Built by **Mark Yafi** as a portfolio piece targeting BI/analytics roles and freelance clients.

- LinkedIn: [linkedin.com/in/markyafi](https://linkedin.com/in/markyafi)
- GitHub: [github.com/markyafi1991](https://github.com/markyafi1991)
