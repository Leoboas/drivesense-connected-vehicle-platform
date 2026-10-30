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

The dashboard contains Vehicle Overview, Connectivity, HMI/Proximity, Data Quality and Route Intelligence tabs. It is an interview presentation layer, not an operational control plane or a real-time vehicle application.

## Streamlit Community Cloud

Use the GitHub repository `Leoboas/drivesense-connected-vehicle-platform`, branch `develop`, and main file `app/dashboard.py`. The public application uses only the versioned synthetic sample; it does not receive AWS credentials or access the project S3 buckets.
