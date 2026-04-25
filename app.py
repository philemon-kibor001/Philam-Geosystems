import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime, date
import json
import io
import random
import math

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Philam Geosystems",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Global */
[data-testid="stAppViewContainer"] { background: #f5f7fa; }
[data-testid="stSidebar"] { background: #0d2137; }
[data-testid="stSidebar"] * { color: #c9d8e8 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #ffffff !important; }

/* Header banner */
.pg-header {
    background: linear-gradient(135deg, #0d2137 0%, #1a4b7a 100%);
    padding: 18px 28px; border-radius: 12px; margin-bottom: 20px;
    display: flex; align-items: center; gap: 16px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.12);
}
.pg-header h1 { color: #ffffff; margin: 0; font-size: 26px; font-weight: 700; }
.pg-header p { color: #90b8d8; margin: 0; font-size: 13px; }

/* KPI cards */
.kpi-card {
    background: #ffffff; border-radius: 10px; padding: 18px 20px;
    border-left: 4px solid #1a6fba; box-shadow: 0 1px 6px rgba(0,0,0,0.07);
    text-align: center;
}
.kpi-val { font-size: 32px; font-weight: 700; color: #0d2137; margin: 4px 0; }
.kpi-label { font-size: 12px; color: #5a7a9a; text-transform: uppercase; letter-spacing: .04em; }
.kpi-delta { font-size: 12px; color: #2e7d32; margin-top: 4px; }

/* Section card */
.section-card {
    background: #ffffff; border-radius: 12px;
    padding: 22px 26px; margin-bottom: 18px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06);
}

/* Status badges */
.badge {
    display: inline-block; padding: 3px 10px; border-radius: 4px;
    font-size: 11px; font-weight: 600; letter-spacing: .03em;
}
.badge-active { background: #e8f5e9; color: #2e7d32; }
.badge-review { background: #fff3e0; color: #e65100; }
.badge-done   { background: #e3f2fd; color: #1565c0; }

/* Footer */
.pg-footer {
    text-align: center; color: #8aacca; font-size: 11px;
    margin-top: 32px; padding: 12px 0;
    border-top: 1px solid #dde6ef;
}
</style>
""", unsafe_allow_html=True)

# ── Session state init ───────────────────────────────────────────────────────
if "parcels" not in st.session_state:
    st.session_state.parcels = pd.DataFrame([
        {"Lot No": "LOT-001", "Classification": "Residential", "Owner": "Santos, Maria",
         "Area (m²)": 320, "Barangay": "Brgy. Malaya", "Municipality": "Quezon City",
         "Province": "Metro Manila", "TCT No": "TCT-12345", "Survey Date": "2026-03-10",
         "Geodetic Engineer": "Eng. Reyes", "Status": "Registered", "Lat": 14.5950, "Lng": 121.0520},
        {"Lot No": "LOT-002", "Classification": "Agricultural", "Owner": "Dela Cruz, Jose",
         "Area (m²)": 5100, "Barangay": "Brgy. Sta. Ana", "Municipality": "Antipolo",
         "Province": "Rizal", "TCT No": "OCT-98765", "Survey Date": "2026-02-18",
         "Geodetic Engineer": "Eng. Gomez", "Status": "Active Survey", "Lat": 14.5880, "Lng": 121.0610},
        {"Lot No": "LOT-003", "Classification": "Commercial", "Owner": "Aquino Holdings Corp",
         "Area (m²)": 850, "Barangay": "Brgy. Bagong Silang", "Municipality": "Caloocan",
         "Province": "Metro Manila", "TCT No": "TCT-44321", "Survey Date": "2026-04-01",
         "Geodetic Engineer": "Eng. Reyes", "Status": "In Review", "Lat": 14.6010, "Lng": 121.0430},
        {"Lot No": "LOT-004", "Classification": "Residential", "Owner": "Garcia, Luis",
         "Area (m²)": 410, "Barangay": "Brgy. San Isidro", "Municipality": "Marikina",
         "Province": "Metro Manila", "TCT No": "TCT-77001", "Survey Date": "2026-04-15",
         "Geodetic Engineer": "Eng. Santos", "Status": "Registered", "Lat": 14.6350, "Lng": 121.1020},
    ])

if "gps_points" not in st.session_state:
    st.session_state.gps_points = pd.DataFrame([
        {"Point ID": "CP-001", "Type": "Control Point", "Lat": 14.5950, "Lng": 121.0520,
         "Elevation (m)": 47.83, "HDOP": 0.72, "Fix": "RTK Fixed", "Accuracy (m)": 0.01,
         "Satellites": 12, "Logged": "2026-04-24 08:12", "Description": "Main control point"},
        {"Point ID": "BC-002", "Type": "Boundary Corner", "Lat": 14.5880, "Lng": 121.0610,
         "Elevation (m)": 48.12, "HDOP": 0.85, "Fix": "RTK Fixed", "Accuracy (m)": 0.01,
         "Satellites": 11, "Logged": "2026-04-24 09:05", "Description": "NE corner boundary"},
        {"Point ID": "TP-003", "Type": "Traverse Point", "Lat": 14.5910, "Lng": 121.0570,
         "Elevation (m)": 46.95, "HDOP": 1.20, "Fix": "DGNSS", "Accuracy (m)": 0.30,
         "Satellites": 9, "Logged": "2026-04-24 10:30", "Description": "Traverse station 3"},
        {"Point ID": "RM-004", "Type": "Reference Mark", "Lat": 14.5970, "Lng": 121.0490,
         "Elevation (m)": 49.10, "HDOP": 0.68, "Fix": "RTK Fixed", "Accuracy (m)": 0.01,
         "Satellites": 13, "Logged": "2026-04-25 07:45", "Description": "Benchmark RM-A"},
    ])

if "reports" not in st.session_state:
    st.session_state.reports = [
        {"Report": "Survey Plan – LOT-001", "Project": "Brgy. Malaya", "Date": "2026-04-24", "Format": "PDF", "Engineer": "Eng. Reyes"},
        {"Report": "GNSS Control Network Summary", "Project": "QC Control Network", "Date": "2026-04-22", "Format": "CSV", "Engineer": "Eng. Gomez"},
        {"Report": "Technical Description – LOT-003", "Project": "Bagong Silang", "Date": "2026-04-18", "Format": "PDF", "Engineer": "Eng. Reyes"},
    ]

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🗺️ Philam Geosystems")
    st.markdown("*Private Survey Edition*")
    st.divider()

    module = st.selectbox(
        "Navigation",
        ["📊 Dashboard", "🗂 Land Survey & Parcels", "📡 GPS/GNSS Collection",
         "🗺️ Map Visualization", "📄 Report Generation"],
        label_visibility="collapsed"
    )
    st.divider()

    st.markdown("**📐 Coordinate System**")
    st.selectbox("Projection", ["PRS92 / Philippines Zone III", "PRS92 / Zone I", "WGS84 UTM 51N", "WGS84 Geographic"], key="proj")
    st.selectbox("Vertical Datum", ["Mean Sea Level (MPSS)", "EGM2008 Geoid"], key="datum")
    st.divider()

    # Live GPS ticker
    now = datetime.now()
    lat_live = 14.0 + 35/60 + (42.18 + math.sin(now.second * 0.3) * 0.003) / 3600
    lng_live = 121.0 + 3/60 + (18.74 + math.cos(now.second * 0.25) * 0.002) / 3600
    elev_live = 47.83 + math.sin(now.second * 0.1) * 0.05

    st.markdown("**📡 Live GPS Feed**")
    st.code(
        f"Lat:  14° 35' 42\" N\n"
        f"Lng: 121° 03' 18\" E\n"
        f"Elev: {elev_live:.2f} m\n"
        f"Fix:  RTK Fixed\n"
        f"Sats: 12/14  HDOP:0.72",
        language=None
    )
    st.caption(f"Updated: {now.strftime('%H:%M:%S')}")
    st.divider()
    st.markdown("**Firm:** Philam Geosystems")
    st.markdown("**PRC Accredited** · Est. 2010")

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="pg-header">
  <div style="font-size:40px">🗺️</div>
  <div>
    <h1>Philam Geosystems</h1>
    <p>Technical Geospatial & Survey Management Platform · Private Survey Firm Edition · Philippines</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# MODULE 1 – DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
if module == "📊 Dashboard":
    parcels = st.session_state.parcels
    gps = st.session_state.gps_points

    # KPI row
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Active Projects</div>
            <div class="kpi-val">5</div>
            <div class="kpi-delta">↑ +2 this month</div></div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Parcels Registered</div>
            <div class="kpi-val">{len(parcels)}</div>
            <div class="kpi-delta">↑ +{len(parcels)} on record</div></div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">GPS Points Logged</div>
            <div class="kpi-val">{len(gps)}</div>
            <div class="kpi-delta">↑ +{len(gps)} total</div></div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Reports Generated</div>
            <div class="kpi-val">{len(st.session_state.reports)}</div>
            <div class="kpi-delta">this quarter</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Map + Recent surveys
    col_map, col_list = st.columns([3, 2])

    with col_map:
        st.subheader("🗺️ Survey Area Map")
        center_lat = parcels["Lat"].mean()
        center_lng = parcels["Lng"].mean()
        m = folium.Map(location=[center_lat, center_lng], zoom_start=13,
                       tiles="CartoDB Positron")

        colors = {"Residential": "blue", "Agricultural": "green",
                  "Commercial": "orange", "Industrial": "red"}

        for _, row in parcels.iterrows():
            color = colors.get(row["Classification"], "gray")
            folium.CircleMarker(
                location=[row["Lat"], row["Lng"]],
                radius=14,
                color=color, fill=True, fill_color=color, fill_opacity=0.4,
                tooltip=f"<b>{row['Lot No']}</b><br>{row['Classification']}<br>{row['Area (m²)']} m²<br>{row['Owner']}",
                popup=folium.Popup(
                    f"<b>{row['Lot No']}</b><br>Owner: {row['Owner']}<br>"
                    f"Area: {row['Area (m²)']} m²<br>Status: {row['Status']}", max_width=200)
            ).add_to(m)

        for _, row in gps.iterrows():
            folium.Marker(
                location=[row["Lat"], row["Lng"]],
                icon=folium.Icon(color="red", icon="map-pin", prefix="fa"),
                tooltip=f"<b>{row['Point ID']}</b><br>{row['Type']}<br>Fix: {row['Fix']}"
            ).add_to(m)

        st_folium(m, width=None, height=380)

    with col_list:
        st.subheader("📋 Recent Surveys")
        status_map = {
            "Active Survey": "badge-active",
            "In Review": "badge-review",
            "Registered": "badge-done",
        }
        for _, row in parcels.iterrows():
            cls = status_map.get(row["Status"], "badge-done")
            st.markdown(f"""
            <div style="background:#fff;border-radius:8px;padding:10px 14px;margin-bottom:8px;border:1px solid #e8edf2;">
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <b style="font-size:13px;color:#0d2137">{row['Lot No']}</b>
                <span class="badge {cls}">{row['Status']}</span>
              </div>
              <div style="font-size:12px;color:#5a7a9a;margin-top:3px;">
                {row['Owner']} · {row['Area (m²)']} m² · {row['Classification']}
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.subheader("📡 GPS Summary")
        fix_counts = gps["Fix"].value_counts()
        for fix, count in fix_counts.items():
            pct = int(count / len(gps) * 100)
            st.markdown(f"**{fix}** — {count} points ({pct}%)")
            st.progress(pct / 100)


# ════════════════════════════════════════════════════════════════════════════
# MODULE 2 – LAND SURVEY & PARCELS
# ════════════════════════════════════════════════════════════════════════════
elif module == "🗂 Land Survey & Parcels":
    st.subheader("🗂 Land Survey & Parcel Management")

    tab_view, tab_new, tab_edit = st.tabs(["📋 Registered Parcels", "➕ Add New Parcel", "🔍 Search & Filter"])

    with tab_view:
        df = st.session_state.parcels
        st.markdown(f"**{len(df)} parcels on record**")

        # Color-code status
        def style_status(val):
            color_map = {"Registered": "#e3f2fd", "Active Survey": "#e8f5e9", "In Review": "#fff3e0"}
            return f"background-color: {color_map.get(val, '#fff')}"

        styled = df.drop(columns=["Lat", "Lng"]).style.applymap(style_status, subset=["Status"])
        st.dataframe(styled, use_container_width=True, height=260)

        # Export
        csv = df.drop(columns=["Lat","Lng"]).to_csv(index=False).encode()
        st.download_button("📥 Export Parcels (CSV)", csv, "philam_parcels.csv", "text/csv")

        # Parcel stats
        st.markdown("---")
        st.markdown("**Area by Classification**")
        class_area = df.groupby("Classification")["Area (m²)"].sum().reset_index()
        st.bar_chart(class_area.set_index("Classification"))

    with tab_new:
        st.markdown("**Register a New Parcel**")
        with st.form("new_parcel_form"):
            c1, c2 = st.columns(2)
            with c1:
                lot_no = st.text_input("Lot Number *", placeholder="e.g. LOT-005, Block 3")
                classification = st.selectbox("Land Classification *", ["Residential","Agricultural","Commercial","Industrial","Timberland"])
                owner = st.text_input("Owner Name *", placeholder="Last, First MI")
                area = st.number_input("Area (sq. m) *", min_value=0.0, step=0.01)
                tct = st.text_input("TCT / OCT Number", placeholder="Title number")
            with c2:
                barangay = st.text_input("Barangay *")
                municipality = st.text_input("Municipality *")
                province = st.text_input("Province *")
                survey_date = st.date_input("Survey Date *", value=date.today())
                engineer = st.text_input("Geodetic Engineer *", placeholder="Eng. Full Name, PRC No.")
            lat_in = st.number_input("Latitude (decimal degrees)", value=14.5950, format="%.6f")
            lng_in = st.number_input("Longitude (decimal degrees)", value=121.0520, format="%.6f")
            survey_type = st.selectbox("Survey Type", ["Land Titling","Subdivision","Consolidation","Topographic","Cadastral"])
            remarks = st.text_area("Remarks / Annotations", height=80)
            status = st.selectbox("Status", ["Active Survey","In Review","Registered"])

            submitted = st.form_submit_button("💾 Save Parcel", type="primary")
            if submitted:
                if lot_no and owner and barangay:
                    new_row = {
                        "Lot No": lot_no, "Classification": classification, "Owner": owner,
                        "Area (m²)": area, "Barangay": barangay, "Municipality": municipality,
                        "Province": province, "TCT No": tct, "Survey Date": str(survey_date),
                        "Geodetic Engineer": engineer, "Status": status, "Lat": lat_in, "Lng": lng_in
                    }
                    st.session_state.parcels = pd.concat(
                        [st.session_state.parcels, pd.DataFrame([new_row])], ignore_index=True)
                    st.success(f"✅ Parcel **{lot_no}** registered successfully!")
                    st.rerun()
                else:
                    st.error("Please fill in all required fields (*)")

    with tab_edit:
        st.markdown("**Search & Filter Parcels**")
        c1, c2, c3 = st.columns(3)
        search_owner = c1.text_input("Filter by owner", placeholder="Name...")
        filter_class = c2.selectbox("Classification", ["All"] + list(st.session_state.parcels["Classification"].unique()))
        filter_status = c3.selectbox("Status", ["All"] + list(st.session_state.parcels["Status"].unique()))

        filtered = st.session_state.parcels.copy()
        if search_owner:
            filtered = filtered[filtered["Owner"].str.contains(search_owner, case=False, na=False)]
        if filter_class != "All":
            filtered = filtered[filtered["Classification"] == filter_class]
        if filter_status != "All":
            filtered = filtered[filtered["Status"] == filter_status]

        st.dataframe(filtered.drop(columns=["Lat","Lng"]), use_container_width=True)
        st.caption(f"{len(filtered)} result(s) found")


# ════════════════════════════════════════════════════════════════════════════
# MODULE 3 – GPS/GNSS
# ════════════════════════════════════════════════════════════════════════════
elif module == "📡 GPS/GNSS Collection":
    st.subheader("📡 GPS/GNSS Data Collection")

    tab_live, tab_log, tab_import = st.tabs(["📡 Live Receiver", "📍 Log Point", "📂 Import Data"])

    with tab_live:
        st.markdown("**Live GNSS Receiver Status**")
        now = datetime.now()
        lat_d = 14 + 35/60 + (42.18 + math.sin(now.second * 0.3) * 0.005)/3600
        lng_d = 121 + 3/60 + (18.74 + math.cos(now.second * 0.25) * 0.003)/3600
        elev_d = 47.83 + math.sin(now.second * 0.1) * 0.05

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Fix Type", "RTK Fixed", "Excellent")
        m2.metric("Satellites", "12 / 14", "+2")
        m3.metric("HDOP", "0.72", delta=None)
        m4.metric("Accuracy", "±0.01 m", delta=None)

        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        c1.metric("Latitude", f"14° 35' 42.18\" N")
        c2.metric("Longitude", f"121° 03' 18.74\" E")
        c3.metric("Elevation", f"{elev_d:.2f} m MSL")

        st.info(f"🕐 Last updated: {now.strftime('%Y-%m-%d %H:%M:%S')} PHT | Coordinate System: PRS92 / Phil. Zone III")

        # Mini map
        m_gps = folium.Map(location=[lat_d, lng_d], zoom_start=16, tiles="OpenStreetMap")
        folium.Marker(
            [lat_d, lng_d],
            icon=folium.Icon(color="red", icon="crosshairs", prefix="fa"),
            tooltip="Current Position"
        ).add_to(m_gps)
        folium.Circle([lat_d, lng_d], radius=1, color="red", fill=True, fill_opacity=0.2).add_to(m_gps)
        st_folium(m_gps, width=None, height=280)

    with tab_log:
        st.markdown("**Log a New GPS/GNSS Point**")
        with st.form("gps_form"):
            c1, c2 = st.columns(2)
            with c1:
                pt_id = c1.text_input("Point ID *", placeholder="e.g. CP-005")
                pt_type = c1.selectbox("Point Type *", ["Control Point","Boundary Corner","Traverse Point","Reference Mark","Spot Elevation"])
                pt_lat = c1.number_input("Latitude (DD) *", value=14.5950, format="%.8f")
                pt_lng = c1.number_input("Longitude (DD) *", value=121.0520, format="%.8f")
            with c2:
                pt_elev = c2.number_input("Elevation (m)", value=47.83, format="%.3f")
                pt_fix = c2.selectbox("Fix Type", ["RTK Fixed","RTK Float","DGNSS","Autonomous"])
                pt_hdop = c2.number_input("HDOP", value=0.72, format="%.2f")
                pt_sats = c2.number_input("No. of Satellites", value=12, min_value=0, max_value=40)
            pt_acc = st.selectbox("Accuracy Class", ["±0.01 m (RTK)","±0.10 m (DGNSS)","±1.00 m (Autonomous)"])
            pt_desc = st.text_input("Description / Remarks")

            if st.form_submit_button("📍 Log Point", type="primary"):
                if pt_id:
                    acc_val = float(pt_acc.split("±")[1].split(" m")[0])
                    new_pt = {
                        "Point ID": pt_id, "Type": pt_type, "Lat": pt_lat, "Lng": pt_lng,
                        "Elevation (m)": pt_elev, "HDOP": pt_hdop, "Fix": pt_fix,
                        "Accuracy (m)": acc_val, "Satellites": int(pt_sats),
                        "Logged": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Description": pt_desc
                    }
                    st.session_state.gps_points = pd.concat(
                        [st.session_state.gps_points, pd.DataFrame([new_pt])], ignore_index=True)
                    st.success(f"✅ Point **{pt_id}** logged successfully!")
                    st.rerun()
                else:
                    st.error("Point ID is required.")

        st.markdown("---")
        st.markdown("**Logged Points**")
        st.dataframe(st.session_state.gps_points, use_container_width=True, height=220)
        gps_csv = st.session_state.gps_points.to_csv(index=False).encode()
        st.download_button("📥 Export GPS Points (CSV)", gps_csv, "philam_gps_points.csv", "text/csv")

    with tab_import:
        st.markdown("**Import GPS Data**")
        uploaded = st.file_uploader("Upload CSV with columns: Point ID, Lat, Lng, Elevation, Fix", type=["csv"])
        if uploaded:
            try:
                imported = pd.read_csv(uploaded)
                st.success(f"Preview: {len(imported)} rows loaded")
                st.dataframe(imported.head(10))
                if st.button("➕ Append to GPS Points"):
                    st.session_state.gps_points = pd.concat(
                        [st.session_state.gps_points, imported], ignore_index=True)
                    st.success("Data appended!")
                    st.rerun()
            except Exception as e:
                st.error(f"Error reading file: {e}")

        st.markdown("---")
        st.markdown("**Expected CSV Format:**")
        sample = pd.DataFrame([{
            "Point ID": "CP-001", "Type": "Control Point",
            "Lat": 14.595000, "Lng": 121.052000, "Elevation (m)": 47.83,
            "Fix": "RTK Fixed", "Accuracy (m)": 0.01, "Satellites": 12
        }])
        st.dataframe(sample)


# ════════════════════════════════════════════════════════════════════════════
# MODULE 4 – MAP VISUALIZATION
# ════════════════════════════════════════════════════════════════════════════
elif module == "🗺️ Map Visualization":
    st.subheader("🗺️ Map Visualization & GIS Layers")

    col_ctrl, col_map = st.columns([1, 3])

    with col_ctrl:
        st.markdown("**Layer Controls**")
        show_parcels = st.checkbox("🗂 Land Parcels", value=True)
        show_gps = st.checkbox("📡 GPS/GNSS Points", value=True)
        show_labels = st.checkbox("🏷 Labels", value=True)
        st.markdown("---")
        st.markdown("**Map Style**")
        basemap = st.radio("Basemap", ["CartoDB Positron", "OpenStreetMap", "CartoDB Dark Matter", "Stamen Terrain"])
        st.markdown("---")
        st.markdown("**Classification Filter**")
        show_res = st.checkbox("Residential", value=True)
        show_agri = st.checkbox("Agricultural", value=True)
        show_comm = st.checkbox("Commercial", value=True)
        show_ind = st.checkbox("Industrial", value=True)
        st.markdown("---")
        st.markdown("**Coordinate System**")
        st.info("PRS92 / Philippines Zone III\n\nVertical: MSL (MPSS)")

    with col_map:
        parcels = st.session_state.parcels
        gps = st.session_state.gps_points

        tile_map = {
            "CartoDB Positron": "CartoDB positron",
            "OpenStreetMap": "OpenStreetMap",
            "CartoDB Dark Matter": "CartoDB dark_matter",
            "Stamen Terrain": "Stamen Terrain"
        }
        tile = tile_map.get(basemap, "CartoDB positron")

        center_lat = parcels["Lat"].mean() if len(parcels) > 0 else 14.59
        center_lng = parcels["Lng"].mean() if len(parcels) > 0 else 121.05

        m = folium.Map(location=[center_lat, center_lng], zoom_start=13, tiles=tile)

        color_map = {"Residential": "blue", "Agricultural": "green", "Commercial": "orange", "Industrial": "red"}
        class_filter = []
        if show_res: class_filter.append("Residential")
        if show_agri: class_filter.append("Agricultural")
        if show_comm: class_filter.append("Commercial")
        if show_ind: class_filter.append("Industrial")

        if show_parcels:
            for _, row in parcels.iterrows():
                if row["Classification"] not in class_filter:
                    continue
                color = color_map.get(row["Classification"], "gray")
                tooltip = f"<b>{row['Lot No']}</b><br>{row['Classification']}<br>{row['Area (m²)']} m²" if show_labels else None
                folium.CircleMarker(
                    location=[row["Lat"], row["Lng"]],
                    radius=16, color=color, fill=True,
                    fill_color=color, fill_opacity=0.35, weight=2,
                    tooltip=tooltip,
                    popup=folium.Popup(
                        f"<b>{row['Lot No']}</b><br>Owner: {row['Owner']}<br>"
                        f"Area: {row['Area (m²)']} m²<br>Classification: {row['Classification']}<br>"
                        f"Status: {row['Status']}<br>GE: {row['Geodetic Engineer']}", max_width=220)
                ).add_to(m)

        if show_gps:
            for _, row in gps.iterrows():
                fix_color = {"RTK Fixed": "red", "RTK Float": "orange", "DGNSS": "blue", "Autonomous": "gray"}
                fc = fix_color.get(row["Fix"], "red")
                folium.Marker(
                    location=[row["Lat"], row["Lng"]],
                    icon=folium.Icon(color=fc, icon="map-marker", prefix="fa"),
                    tooltip=f"<b>{row['Point ID']}</b><br>{row['Type']}<br>Elev: {row['Elevation (m)']} m<br>Fix: {row['Fix']}" if show_labels else None
                ).add_to(m)

        # Legend
        legend_html = """
        <div style="position:fixed;bottom:30px;left:30px;z-index:1000;
            background:white;padding:12px 16px;border-radius:8px;
            box-shadow:0 2px 8px rgba(0,0,0,0.2);font-size:12px;font-family:Arial;">
          <b>Legend</b><br>
          <span style="color:blue">●</span> Residential &nbsp;
          <span style="color:green">●</span> Agricultural<br>
          <span style="color:orange">●</span> Commercial &nbsp;
          <span style="color:red">📍</span> GPS Point
        </div>"""
        m.get_root().html.add_child(folium.Element(legend_html))

        result = st_folium(m, width=None, height=520)

        if result and result.get("last_object_clicked"):
            st.info(f"📍 Clicked: {result['last_object_clicked']}")


# ════════════════════════════════════════════════════════════════════════════
# MODULE 5 – REPORT GENERATION
# ════════════════════════════════════════════════════════════════════════════
elif module == "📄 Report Generation":
    st.subheader("📄 Report Generation & Export")

    tab_gen, tab_hist, tab_firm = st.tabs(["⚙️ Generate Report", "📁 Report History", "🏢 Firm Settings"])

    with tab_gen:
        st.markdown("**Configure & Generate Survey Report**")
        c1, c2 = st.columns(2)
        with c1:
            report_type = st.selectbox("Report Type", [
                "Survey Plan (Technical Description)",
                "Geodetic Control Network Report",
                "Subdivision Plan",
                "Topographic Survey Report",
                "GPS/GNSS Data Summary",
                "As-Built Survey Report",
            ])
            project = st.selectbox("Select Project / Parcel",
                st.session_state.parcels["Lot No"].tolist() + ["All Projects"])
            output_fmt = st.selectbox("Output Format", ["PDF (Signed & Sealed)", "CSV / Excel", "KML / GeoJSON", "AutoCAD DXF"])

        with c2:
            include_map = st.checkbox("Include Map / Plan Sketch", value=True)
            include_coords = st.checkbox("Include Coordinate Table", value=True)
            include_signature = st.checkbox("Include GE Signature Block", value=True)
            report_date = st.date_input("Report Date", value=date.today())
            ref_no = st.text_input("Reference Number", placeholder="e.g. PGS-2026-0042")

        st.markdown("---")

        if st.button("📄 Generate Report", type="primary"):
            with st.spinner("Generating report..."):
                import time; time.sleep(1.2)

            # Build CSV report content
            parcels = st.session_state.parcels
            gps = st.session_state.gps_points
            sel_parcel = parcels[parcels["Lot No"] == project] if project != "All Projects" else parcels

            report_lines = [
                "PHILAM GEOSYSTEMS",
                "Technical Geospatial & Survey Report",
                "=" * 60,
                f"Report Type : {report_type}",
                f"Reference No: {ref_no or 'PGS-2026-XXXX'}",
                f"Date        : {report_date}",
                f"Projection  : PRS92 / Philippines Zone III",
                f"Datum       : Mean Sea Level (MPSS)",
                "=" * 60,
                "",
                "PARCEL DETAILS",
                "-" * 40,
            ]
            for _, r in sel_parcel.iterrows():
                report_lines += [
                    f"Lot No       : {r['Lot No']}",
                    f"Classification: {r['Classification']}",
                    f"Owner        : {r['Owner']}",
                    f"Area         : {r['Area (m²)']} sq. m",
                    f"Location     : {r['Barangay']}, {r['Municipality']}, {r['Province']}",
                    f"TCT/OCT No   : {r['TCT No']}",
                    f"Survey Date  : {r['Survey Date']}",
                    f"GE           : {r['Geodetic Engineer']}",
                    f"Status       : {r['Status']}",
                    "",
                ]
            if include_coords:
                report_lines += ["GPS/GNSS CONTROL POINTS", "-" * 40]
                for _, r in gps.iterrows():
                    report_lines.append(
                        f"{r['Point ID']} | {r['Type']} | Lat:{r['Lat']:.6f} | Lng:{r['Lng']:.6f} | "
                        f"Elev:{r['Elevation (m)']}m | Fix:{r['Fix']} | Acc:±{r['Accuracy (m)']}m"
                    )
            if include_signature:
                report_lines += ["", "=" * 60,
                    "Certified correct by:",
                    "Signature: ___________________________",
                    "Geodetic Engineer / PRC Accredited",
                    "Date: " + str(report_date),
                ]

            report_text = "\n".join(report_lines)
            st.success("✅ Report generated successfully!")
            st.text_area("Report Preview", report_text, height=320)

            fname = f"philam_report_{ref_no or 'PGS-2026'}_{report_date}.txt"
            st.download_button("📥 Download Report", report_text.encode(), fname, "text/plain")

            # Save to history
            st.session_state.reports.append({
                "Report": report_type,
                "Project": project,
                "Date": str(report_date),
                "Format": output_fmt.split(" ")[0],
                "Engineer": "On record"
            })

    with tab_hist:
        st.markdown("**Report History**")
        if st.session_state.reports:
            reports_df = pd.DataFrame(st.session_state.reports)
            st.dataframe(reports_df, use_container_width=True, hide_index=True)
            rpt_csv = reports_df.to_csv(index=False).encode()
            st.download_button("📥 Export Report Log", rpt_csv, "philam_report_log.csv", "text/csv")
        else:
            st.info("No reports generated yet.")

    with tab_firm:
        st.markdown("**Firm Letterhead & Settings**")
        with st.form("firm_form"):
            c1, c2 = st.columns(2)
            firm_name = c1.text_input("Firm Name", value="Philam Geosystems")
            prc_no = c1.text_input("PRC Accreditation No.", placeholder="e.g. GE-PH-001234")
            ge_name = c1.text_input("Licensed Geodetic Engineer", placeholder="Full Name, PRC No.")
            address = c2.text_area("Office Address", placeholder="Street, Barangay\nCity, Province", height=80)
            phone = c2.text_input("Phone", placeholder="+63 XXX XXX XXXX")
            email = c2.text_input("Email", placeholder="info@philamgeo.com.ph")
            website = c2.text_input("Website", placeholder="www.philamgeo.com.ph")
            if st.form_submit_button("💾 Save Firm Settings", type="primary"):
                st.success("✅ Firm settings saved!")

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="pg-footer">
  Philam Geosystems · Technical Geospatial & Survey Management Platform ·
  PRS92 Compliant · DENR-NAMRIA Standards · © 2026
</div>
""", unsafe_allow_html=True)
