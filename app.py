import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="AstroWatch | Near-Earth Object Explorer",
    page_icon="☄️",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = Path(__file__).parent / "asteroid_close_approaches_2021_2025.csv"

# ---------- Theme ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root { --bg:#080d1b; --panel:#111a2e; --panel2:#151f36; --muted:#94a3b8; --cyan:#5eead4; --blue:#60a5fa; }
.stApp { background: radial-gradient(ellipse at 10% 0%, #17264a 0%, #080d1b 48%, #070b16 100%); color:#edf4ff; font-family:'DM Sans',sans-serif; }
h1,h2,h3 { font-family:'Space Grotesk',sans-serif !important; letter-spacing:-.5px; }
.block-container { padding-top:1.7rem; padding-bottom:2rem; max-width:1500px; }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#111a2e,#0b1120); border-right:1px solid #25314b; }
[data-testid="stMetric"] { background:linear-gradient(135deg,rgba(26,41,69,.94),rgba(16,26,46,.94)); border:1px solid #2b3b5a; padding:17px 18px; border-radius:16px; box-shadow:0 10px 30px rgba(0,0,0,.12); }
[data-testid="stMetricLabel"] { color:#a8b7d0 !important; }
[data-testid="stMetricValue"] { color:#f8fbff !important; font-family:'Space Grotesk',sans-serif; }
.hero { padding:26px 30px; border:1px solid #2c4267; border-radius:22px; background:linear-gradient(115deg,rgba(29,53,91,.9),rgba(17,27,48,.85) 60%,rgba(18,48,66,.8)); margin-bottom:20px; }
.hero-tag { display:inline-block; color:#7dd3fc; border:1px solid #346080; background:#132d45; padding:5px 10px; border-radius:20px; font-size:12px; letter-spacing:1.1px; text-transform:uppercase; }
.hero h1 { font-size:2.45rem; margin:.55rem 0 .25rem; color:#f8fbff; }
.hero p { color:#bac8dd; font-size:1.02rem; margin:0; max-width:850px; }
.section-head { color:#edf4ff; font-family:'Space Grotesk',sans-serif; font-size:1.22rem; font-weight:600; margin:8px 0 12px; }
.info-card { background:rgba(17,26,46,.82); border:1px solid #263652; padding:18px 20px; border-radius:16px; height:100%; }
.info-card h3 { margin-top:0; color:#7dd3fc; font-size:1.05rem; }
.info-card p, .info-card li { color:#b8c6dc; line-height:1.6; }
div[data-testid="stTabs"] button { color:#b9c7dc; }
div[data-testid="stTabs"] button[aria-selected="true"] { color:#5eead4; border-bottom-color:#5eead4; }
div[data-testid="stDataFrame"] { border:1px solid #293956; border-radius:12px; overflow:hidden; }
.small-note { color:#91a1ba; font-size:.85rem; }
</style>
""", unsafe_allow_html=True)

PLOT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#dbe7f7", family="DM Sans"),
    margin=dict(l=18,r=18,t=45,b=18),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)
GRID = dict(gridcolor="rgba(148,163,184,.15)", zerolinecolor="rgba(148,163,184,.18)")

@st.cache_data
def load_data():
    data = pd.read_csv(DATA_FILE)
    data["approach_date"] = pd.to_datetime(data["approach_date"], errors="coerce")
    numeric = [
        "approach_year", "approach_month", "miss_distance_au",
        "miss_distance_million_km", "minimum_distance_million_km",
        "maximum_distance_million_km", "relative_velocity_km_s",
        "infinity_velocity_km_s", "absolute_magnitude_h", "orbit_id"
    ]
    for col in numeric:
        data[col] = pd.to_numeric(data[col], errors="coerce")
    return data

try:
    df = load_data()
except Exception as exc:
    st.error(f"Could not load the dataset: {exc}")
    st.stop()

if df.empty:
    st.error("The dataset is empty.")
    st.stop()

# ---------- Sidebar controls ----------
st.sidebar.markdown("## ☄️ AstroWatch")
st.sidebar.caption("NEAR-EARTH OBJECT ANALYTICS")
st.sidebar.markdown("---")
st.sidebar.markdown("### Filter your view")

years = sorted(df["approach_year"].dropna().astype(int).unique().tolist())
chosen_years = st.sidebar.multiselect("Approach year", years, default=years)
bands = sorted(df["distance_band"].dropna().unique().tolist())
chosen_bands = st.sidebar.multiselect("Distance band", bands, default=bands)

min_date = df["approach_date"].min().date()
max_date = df["approach_date"].max().date()
date_range = st.sidebar.date_input("Approach date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)

vmin, vmax = float(df["relative_velocity_km_s"].min()), float(df["relative_velocity_km_s"].max())
velocity_range = st.sidebar.slider(
    "Relative velocity (km/s)", min_value=float(round(vmin, 1)),
    max_value=float(round(vmax, 1)), value=(float(round(vmin, 1)), float(round(vmax, 1))), step=0.5
)

dmin, dmax = float(df["miss_distance_million_km"].min()), float(df["miss_distance_million_km"].max())
distance_range = st.sidebar.slider(
    "Miss distance (million km)", min_value=float(round(dmin, 2)),
    max_value=float(round(dmax, 2)), value=(float(round(dmin, 2)), float(round(dmax, 2))), step=0.1
)
search = st.sidebar.text_input("Find asteroid by name / ID", placeholder="e.g. 2021 AS1")
if st.sidebar.button("Reset all filters", use_container_width=True):
    st.rerun()

filtered = df[df["approach_year"].isin(chosen_years) & df["distance_band"].isin(chosen_bands)]
if len(date_range) == 2:
    filtered = filtered[(filtered["approach_date"].dt.date >= date_range[0]) & (filtered["approach_date"].dt.date <= date_range[1])]
filtered = filtered[
    filtered["relative_velocity_km_s"].between(velocity_range[0], velocity_range[1]) &
    filtered["miss_distance_million_km"].between(distance_range[0], distance_range[1])
]
if search.strip():
    filtered = filtered[filtered["asteroid_name_or_id"].astype(str).str.contains(search.strip(), case=False, na=False)]

# ---------- Hero ----------
st.markdown("""
<div class="hero">
  <span class="hero-tag">SPACE DATA • 2021—2025</span>
  <h1>AstroWatch <span style="color:#5eead4">/</span> Near-Earth Object Explorer</h1>
  <p>Explore asteroid close approaches through interactive analytics. Track distance, speed, yearly patterns, and individual objects using one searchable dashboard.</p>
</div>
""", unsafe_allow_html=True)

if filtered.empty:
    st.warning("No records match the current filters. Widen the filters in the sidebar.")
    st.stop()

# ---------- KPIs ----------
total = len(filtered)
unique_objects = filtered["asteroid_name_or_id"].nunique()
median_vel = filtered["relative_velocity_km_s"].median()
closest = filtered["miss_distance_million_km"].min()
fastest = filtered["relative_velocity_km_s"].max()
k1,k2,k3,k4,k5 = st.columns(5)
k1.metric("Close approaches", f"{total:,}", help="Number of rows matching the selected filters.")
k2.metric("Unique asteroid IDs", f"{unique_objects:,}")
k3.metric("Median speed", f"{median_vel:.2f} km/s" if pd.notna(median_vel) else "—")
k4.metric("Closest recorded pass", f"{closest:.3f} million km" if pd.notna(closest) else "—")
k5.metric("Maximum speed", f"{fastest:.2f} km/s" if pd.notna(fastest) else "—")

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
overview, trends, explorer, guide = st.tabs(["✦ Overview", "◷ Trends & Patterns", "⌕ Asteroid Explorer", "ⓘ Project Guide"])

# Shared chart helper
def style(fig, height=360):
    fig.update_layout(**PLOT, height=height)
    fig.update_xaxes(**GRID)
    fig.update_yaxes(**GRID)
    return fig

with overview:
    c1,c2 = st.columns([1.15, 1])
    with c1:
        st.markdown('<div class="section-head">Approaches over time</div>', unsafe_allow_html=True)
        yearly = filtered.groupby("approach_year", as_index=False).size().rename(columns={"size":"approaches"})
        fig = px.bar(yearly, x="approach_year", y="approaches", text="approaches",
                     color="approaches", color_continuous_scale=["#2563eb","#5eead4"],
                     labels={"approach_year":"Year","approaches":"Recorded approaches"})
        fig.update_traces(textposition="outside", marker_line_width=0)
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(style(fig, 350), use_container_width=True)
    with c2:
        st.markdown('<div class="section-head">Share by distance band</div>', unsafe_allow_html=True)
        band_counts = filtered["distance_band"].value_counts().rename_axis("Distance band").reset_index(name="Approaches")
        fig = px.pie(band_counts, names="Distance band", values="Approaches", hole=.62,
                     color_discrete_sequence=["#5eead4","#60a5fa","#a78bfa","#fbbf24"])
        fig.update_traces(textposition="outside", textinfo="percent+label", pull=[0.025]*len(band_counts))
        st.plotly_chart(style(fig, 350), use_container_width=True)

    c3,c4 = st.columns(2)
    with c3:
        st.markdown('<div class="section-head">How fast are recorded asteroids moving?</div>', unsafe_allow_html=True)
        fig = px.histogram(filtered, x="relative_velocity_km_s", nbins=28,
                           labels={"relative_velocity_km_s":"Relative velocity (km/s)", "count":"Number of records"},
                           color_discrete_sequence=["#38bdf8"])
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(style(fig, 340), use_container_width=True)
    with c4:
        st.markdown('<div class="section-head">Miss-distance distribution</div>', unsafe_allow_html=True)
        fig = px.histogram(filtered, x="miss_distance_million_km", nbins=26,
                           labels={"miss_distance_million_km":"Miss distance (million km)", "count":"Number of records"},
                           color_discrete_sequence=["#a78bfa"])
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(style(fig, 340), use_container_width=True)

    st.markdown('<div class="section-head">Quick readout</div>', unsafe_allow_html=True)
    q1,q2,q3 = st.columns(3)
    with q1:
        st.markdown(f"""<div class="info-card"><h3>📍 Distance</h3><p>The closest record in the current selection is <b>{closest:.3f} million km</b> away. Smaller miss distance means a closer recorded pass—not automatically a collision risk.</p></div>""", unsafe_allow_html=True)
    with q2:
        st.markdown(f"""<div class="info-card"><h3>⚡ Speed</h3><p>The median relative velocity is <b>{median_vel:.2f} km/s</b>. The median is a typical midpoint and is less affected by extreme values than the mean.</p></div>""", unsafe_allow_html=True)
    with q3:
        most_common = filtered["distance_band"].mode().iloc[0] if not filtered["distance_band"].mode().empty else "—"
        st.markdown(f"""<div class="info-card"><h3>🛰️ Most common band</h3><p><b>{most_common}</b> is the most frequent distance band in the current selection. Use the sidebar to compare years and bands.</p></div>""", unsafe_allow_html=True)

with trends:
    st.markdown('<div class="section-head">Monthly approach activity</div>', unsafe_allow_html=True)
    monthly = filtered.dropna(subset=["approach_date"]).set_index("approach_date").resample("MS").size().reset_index(name="approaches")
    fig = px.line(monthly, x="approach_date", y="approaches", markers=True,
                  labels={"approach_date":"Month","approaches":"Recorded approaches"})
    fig.update_traces(line=dict(color="#5eead4", width=3), marker=dict(size=5))
    st.plotly_chart(style(fig, 360), use_container_width=True)

    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-head">Velocity spread by year</div>', unsafe_allow_html=True)
        velocity_year = filtered.groupby("approach_year")["relative_velocity_km_s"].agg(
            Median="median", P25=lambda x:x.quantile(.25), P75=lambda x:x.quantile(.75), P95=lambda x:x.quantile(.95)
        ).reset_index().melt(id_vars="approach_year", var_name="Statistic", value_name="Velocity (km/s)")
        fig = px.line(velocity_year, x="approach_year", y="Velocity (km/s)", color="Statistic", markers=True,
                      color_discrete_map={"Median":"#5eead4","P25":"#a78bfa","P75":"#60a5fa","P95":"#fbbf24"})
        fig.update_layout(legend_title_text="")
        st.plotly_chart(style(fig, 350), use_container_width=True)
    with c2:
        st.markdown('<div class="section-head">Speed vs. miss distance</div>', unsafe_allow_html=True)
        # sample for responsive rendering; the full data is still used in the KPI and tables
        scatter = filtered if len(filtered) <= 2500 else filtered.sample(2500, random_state=7)
        fig = px.scatter(scatter, x="miss_distance_million_km", y="relative_velocity_km_s",
                         color="distance_band", hover_name="asteroid_name_or_id",
                         hover_data=["approach_date","approach_year","miss_distance_au"],
                         labels={"miss_distance_million_km":"Miss distance (million km)",
                                 "relative_velocity_km_s":"Relative velocity (km/s)"},
                         color_discrete_sequence=["#5eead4","#60a5fa","#c084fc"])
        fig.update_traces(marker=dict(size=6, opacity=.72))
        st.plotly_chart(style(fig, 350), use_container_width=True)

    st.markdown('<div class="section-head">Average speed by distance band</div>', unsafe_allow_html=True)
    band_velocity = filtered.groupby("distance_band", as_index=False)["relative_velocity_km_s"].mean().sort_values("relative_velocity_km_s", ascending=False)
    fig = px.bar(band_velocity, x="distance_band", y="relative_velocity_km_s", text_auto=".2f",
                 labels={"distance_band":"Distance band","relative_velocity_km_s":"Average relative velocity (km/s)"},
                 color="relative_velocity_km_s", color_continuous_scale=["#2563eb","#5eead4"])
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(style(fig, 330), use_container_width=True)

with explorer:
    st.markdown('<div class="section-head">Searchable close-approach records</div>', unsafe_allow_html=True)
    st.caption("Use the global filters in the sidebar, or search this table by asteroid name/ID. Dates and measurements come from the supplied CSV.")
    search_table = st.text_input("Search records", key="table_search", placeholder="Type part of an asteroid ID…")
    table = filtered.copy()
    if search_table.strip():
        table = table[table["asteroid_name_or_id"].astype(str).str.contains(search_table.strip(), case=False, na=False)]
    cols = [
        "asteroid_name_or_id","approach_date","approach_year","approach_month_name",
        "miss_distance_au","miss_distance_million_km","relative_velocity_km_s",
        "infinity_velocity_km_s","absolute_magnitude_h","distance_band","orbit_id"
    ]
    table = table[cols].sort_values("approach_date", ascending=False)
    st.markdown(f"**{len(table):,} records**")
    st.dataframe(
        table.rename(columns={
            "asteroid_name_or_id":"Asteroid ID","approach_date":"Approach date","approach_year":"Year",
            "approach_month_name":"Month","miss_distance_au":"Miss distance (AU)",
            "miss_distance_million_km":"Miss distance (million km)",
            "relative_velocity_km_s":"Relative velocity (km/s)",
            "infinity_velocity_km_s":"Velocity at infinity (km/s)",
            "absolute_magnitude_h":"Absolute magnitude (H)","distance_band":"Distance band","orbit_id":"Orbit ID"
        }),
        use_container_width=True, hide_index=True, height=440
    )
    st.download_button("⬇️ Download filtered records as CSV", data=table.to_csv(index=False).encode("utf-8"),
                       file_name="astrowatch_filtered_records.csv", mime="text/csv")

    st.markdown('<div class="section-head">Inspect one asteroid record</div>', unsafe_allow_html=True)
    options = sorted(table["asteroid_name_or_id"].dropna().astype(str).unique().tolist())
    if options:
        selected = st.selectbox("Choose an asteroid ID", options)
        record = table[table["asteroid_name_or_id"].astype(str) == selected].iloc[0]
        a,b,c = st.columns(3)
        a.metric("Approach date", record["approach_date"].strftime("%d %b %Y") if pd.notna(record["approach_date"]) else "—")
        b.metric("Miss distance", f'{record["miss_distance_million_km"]:.3f} million km')
        c.metric("Relative velocity", f'{record["relative_velocity_km_s"]:.2f} km/s')
        st.caption("An asteroid ID may appear in more than one row/date; the details above show the latest matching row in the filtered table.")

with guide:
    st.markdown('<div class="section-head">What is AstroWatch?</div>', unsafe_allow_html=True)
    a,b = st.columns(2)
    with a:
        st.markdown("""
        <div class="info-card">
        <h3>🎯 Project objective</h3>
        <p>AstroWatch is an interactive data-visualisation project that explores recorded asteroid close approaches from 2021 to 2025. It turns a CSV dataset into a dashboard that helps users compare activity across time, distance bands, and relative speeds.</p>
        <h3>🧩 Main features</h3>
        <ul>
          <li>Interactive filters for year, date, speed, and distance</li>
          <li>KPI cards for record count, unique IDs, median speed, and closest pass</li>
          <li>Charts for yearly/monthly activity and value distributions</li>
          <li>Searchable data explorer and filtered CSV download</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    with b:
        st.markdown("""
        <div class="info-card">
        <h3>🛠️ Technology stack</h3>
        <ul>
          <li><b>Frontend/UI:</b> Streamlit + custom CSS</li>
          <li><b>Data processing:</b> Python and Pandas</li>
          <li><b>Interactive charts:</b> Plotly Express</li>
          <li><b>Data source:</b> supplied asteroid_close_approaches_2021_2025.csv</li>
        </ul>
        <h3>🔬 What questions can it answer?</h3>
        <ul>
          <li>How many approaches were recorded each year or month?</li>
          <li>How are relative velocities distributed?</li>
          <li>Which distance band appears most often?</li>
          <li>Do velocity and miss distance show an obvious relationship?</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('<div class="section-head">Understand the key columns</div>', unsafe_allow_html=True)
    definitions = pd.DataFrame([
        ["approach_date","Calendar date associated with the recorded close approach."],
        ["miss_distance_au","Miss distance in astronomical units (AU); 1 AU is approximately the average Earth–Sun distance."],
        ["miss_distance_million_km","Miss distance expressed in million kilometres."],
        ["minimum_distance_million_km / maximum_distance_million_km","Lower and upper distance values recorded for the approach."],
        ["relative_velocity_km_s","Relative speed of the asteroid during the close approach, in kilometres per second."],
        ["infinity_velocity_km_s","Velocity-at-infinity field supplied in the dataset; a modelled orbital velocity measure."],
        ["absolute_magnitude_h","Absolute magnitude, a measure related to the asteroid's intrinsic brightness and often used as a rough size proxy."],
        ["distance_band","Category grouping the miss distance into a band, useful for comparisons."],
        ["orbit_id","Orbit identifier included in the source dataset."],
    ], columns=["Column","Meaning"])
    st.dataframe(definitions, use_container_width=True, hide_index=True)
    st.info("Important: this is an educational visualisation of recorded close approaches, not an official impact-risk assessment or an orbital prediction tool.")

st.markdown("---")
st.markdown("<div class='small-note'>ASTROWATCH • Academic Data Visualisation Project • Built with Python, Pandas, Streamlit and Plotly</div>", unsafe_allow_html=True)
