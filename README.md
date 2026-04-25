# 🗺️ Philam Geosystems
### Technical Geospatial & Survey Management Platform
**Private Survey Firm Edition · Philippines**

---

## Features

| Module | Description |
|--------|-------------|
| 📊 Dashboard | KPI overview, interactive map, live GPS feed |
| 🗂 Land Survey & Parcels | Register, search, filter, and export land parcels |
| 📡 GPS/GNSS Collection | Log control points, live receiver status, CSV import |
| 🗺️ Map Visualization | Toggle GIS layers, basemap selection, parcel + GPS overlay |
| 📄 Report Generation | Generate DENR-compliant survey reports, manage firm details |

---

## Deploy to Streamlit Cloud

1. **Fork or push** this folder to a GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io) and click **New app**.
3. Connect your GitHub repo, set **Main file path** to `app.py`.
4. Click **Deploy** — Streamlit Cloud installs `requirements.txt` automatically.

---

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Coordinate System
- Horizontal: **PRS92 / Philippines Zone III** (EPSG:3123)
- Vertical: **Mean Sea Level (MPSS)**
- GPS: **WGS84** (converted on import)

---

## Standards
- DENR Administrative Order No. 98-12
- NAMRIA Technical Standards for Geodetic Surveys
- LRA Requirements for Land Titling

---

**Philam Geosystems** · PRC-Accredited Geodetic Engineering Firm · © 2026
