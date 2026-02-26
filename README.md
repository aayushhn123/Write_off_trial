# 📊 Write-Off Portfolio Monitor

A Streamlit dashboard for credit recovery analytics — visualise POS balances, recovery rates, and vintage trends across your charge-off portfolio.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-name.streamlit.app)

---

## 🖥️ Live Demo

👉 [your-app-name.streamlit.app](https://your-app-name.streamlit.app)

---

## ✨ Features

- **CSV Upload** — drag and drop your portfolio file directly in the browser
- **4 Dimensions** — slice data by POS bucket, Vintage, State, or CIBIL score band
- **$ Value / # Accounts** toggle — switch between balance view and account count view
- **Sub-filters** — drill into a specific bucket (e.g. only Maharashtra, only V3)
- **Dual-panel charts** — POS Balances & Contribution + Recovery with ATS/RoR% overlay
- **KPI summary row** — Total POS, Total Recovery, RoR%, Unique Accounts, Months Covered
- **Summary table** — latest month breakdown with RoR% colour gradient
- **All-dimensions view** — render all 4 tabs at once for reporting

---

## 📁 Repository Structure

```
writeoff-portfolio-monitor/
│
├── writeoff_dashboard.py   # Main Streamlit app
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── config.toml         # Streamlit theme config
└── README.md               # This file
```

---

## 🚀 Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/writeoff-portfolio-monitor.git
cd writeoff-portfolio-monitor
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run the app**
```bash
streamlit run writeoff_dashboard.py
```

The app opens at `http://localhost:8501`

---

## ☁️ Deploy on Streamlit Cloud (Free)

1. Push this repo to GitHub (must be **public** for free tier)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app**
4. Select your repo, branch (`main`), and file (`writeoff_dashboard.py`)
5. Click **Deploy** — live in ~2 minutes

---

## 📊 Expected CSV Format

Your CSV should contain these columns (names are configurable in the sidebar):

| Column | Description |
|--------|-------------|
| `mis_date` | MIS / reporting date (DD-MM-YYYY) |
| `cm11` | Account ID |
| `cycle_opening_balance(current_balance)` | POS / outstanding balance (INR) |
| `last_payment_amount` | Recovery amount (INR) |
| `charge_off_month` | Date account was charged off (DD-MM-YYYY) |
| `state` | State name (e.g. MAHARASHTRA) |
| `cibil_score` | Bureau score (numeric) |

> Column names can be remapped in the sidebar without editing any code.

---

## 📐 Bucket Definitions

**POS Buckets**

| Bucket | Range |
|--------|-------|
| `<1L` | ₹0 – ₹1,00,000 |
| `1L-5L` | ₹1,00,001 – ₹5,00,000 |
| `5L-10L` | ₹5,00,001 – ₹10,00,000 |
| `10L+` | ₹10,00,001+ |

**Vintage Buckets** (months since charge-off)

| Bucket | Range |
|--------|-------|
| V1 | 0 – 30 days |
| V2 | 31 – 60 days |
| V3 | 61 – 90 days |
| V4 | 91 – 120 days |
| V5 | 121 – 150 days |
| V6 | 151 – 180 days |
| **V7** | **181+ days (V7+)** |

**CIBIL Score Buckets**

| Bucket | Range |
|--------|-------|
| `<500` | Below 500 |
| `500-700` | 500 to 699 |
| `700+` | 700 and above |
| `Unknown` | Missing / invalid score |

---

## 🛠️ Tech Stack

- [Streamlit](https://streamlit.io) — web app framework
- [Pandas](https://pandas.pydata.org) — data processing
- [NumPy](https://numpy.org) — numerical operations
- [Matplotlib](https://matplotlib.org) — charting

---

## 📝 Notes

- All balances displayed in **INR Millions**
- Data is processed entirely in-memory — no data is stored or sent anywhere
- CIBIL scores outside 300–900 are treated as invalid and bucketed as `Unknown`
- Negative POS values are clipped to zero

---

## 📄 License

MIT License — free to use and modify.
