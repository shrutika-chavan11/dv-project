# AstroWatch — Near-Earth Object Explorer

AstroWatch is a small full-stack-style data visualisation project built with Streamlit. It uses your asteroid close-approaches dataset for 2021–2025 and includes a polished dark space-themed UI, interactive charts, filters, a searchable table, and CSV export.

## Run locally (Windows)

1. Install Python 3.10 or newer.
2. Extract the project ZIP into a folder.
3. Open PowerShell in that folder.
4. Create and activate a virtual environment (recommended):

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

5. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

6. Start the app:

   ```powershell
   streamlit run app.py
   ```

7. Streamlit will print a local URL, usually `http://localhost:8501`. Open it in your browser.

## What's included

- `app.py` — UI, filtering, data processing, charts and table interactions.
- `asteroid_close_approaches_2021_2025.csv` — the supplied dataset.
- `requirements.txt` — Python dependencies.

## Project architecture

- **Frontend:** Streamlit components + custom CSS theme.
- **Backend/data layer:** Python functions and Pandas filtering/aggregation.
- **Visualisation:** Plotly interactive charts.
- **Storage:** CSV file (no database required for this medium-sized college project).

## Suggested viva explanation

“Our project is AstroWatch, an interactive asteroid close-approach analytics dashboard. We used Python and Pandas to clean and filter the provided CSV dataset, Streamlit to build the interface and user interactions, and Plotly to create interactive visualisations. Users can filter records by year, date, distance band, velocity and asteroid ID, then explore yearly trends, distributions, and individual records. The objective is to make the dataset easier to understand rather than just showing raw rows.”

## Notes

- The dashboard is an educational data-visualisation tool, not a collision prediction system.
- The app calculates its KPI values from the records currently selected by the filters.
- The `infinity_velocity_km_s` field is displayed as supplied in the source dataset; interpretation depends on the original data provider's definition.
