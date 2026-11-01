# Dashboard

The portfolio UI is a local Streamlit application. It deliberately has no public endpoint and does not run AWS compute continuously.

Install the optional UI dependencies and start it from the repository root:

```powershell
pip install -e ".[ui]"
streamlit run app/dashboard.py
```

By default it reads a small versioned synthetic sample suitable for public hosting. To demonstrate the `DEMO_SMALL` Silver layer, point it at a downloaded Parquet file or a local partition glob:

```powershell
$env:DRIVESENSE_DASHBOARD_DATA = "data/silver/*.parquet"
streamlit run app/dashboard.py
```

The dashboard contains Vehicle Overview, Connectivity, HMI/Proximity, Data Quality and Route Intelligence tabs. Its versioned sample contains four synthetic geographic scenarios: São Paulo urban, the São Paulo–Florianópolis corridor, Florianópolis trails, and connectivity variation along the corridor. The São Paulo–Florianópolis envelope follows declared BR-116/BR-101 waypoints and the bridge access to the island; trail points follow declared land corridors. It is an interview presentation layer, not an operational control plane or a real-time vehicle application.

## Interview lens

The Premium Mobility tab turns synthetic telemetry into a concise product discussion: safety
warning delivery, low-distraction interaction, continuity of connected services, vehicle health,
and electric-mobility context. These themes are intentionally aligned with premium-mobility
product conversations, but the project is independent and makes no claim about a real OEM,
vehicle, driver, or performance result.

The dashboard accepts both the current enriched contract and legacy Silver extracts. Missing
optional enrichment fields receive explicit display defaults, so a valid older dataset cannot
crash the interface.

## Streamlit Community Cloud

Use the GitHub repository `Leoboas/drivesense-connected-vehicle-platform`, branch `main`, and main file `app/dashboard.py`. The public application uses only the versioned synthetic sample; it does not receive AWS credentials or access the project S3 buckets. Publish only after the reviewed `develop` to `main` release PR has merged, so the public source and public dashboard stay aligned.
