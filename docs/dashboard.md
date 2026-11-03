# Dashboard

The interface uses an original cockpit-inspired visual system: graphite surfaces, electric-blue
accents, compact executive cards and a journey-first navigation hierarchy. It does not reproduce
or imply any OEM visual identity.

## Brand customization

Adjust `BRAND_TOKENS` near the top of `app/dashboard.py` to change the product name, eyebrow
label and visual tokens in one place. `accent`, `accent_deep`, `background`, `surface`, `border`,
`text`, `text_muted`, and `success` are applied as CSS custom properties across the hero, sidebar,
metric cards, tabs and journey-status badge. Use original colours and typography; do not use an
OEM logo, proprietary asset, or wording that implies an official affiliation.

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

## Digital twin and latency timeline

The Digital Twin tab is a synthetic replay of a selected vehicle's journey. It presents battery,
range, connectivity, road conditions and multimedia interaction in a product-friendly 2D view.
The optional 3D plot is intended for technical exploration: its axes are battery state, latency
and energy per event; colour is connection state and size is speed. It is not a real-time digital
twin or navigation system.

The Journey Event speed, battery state, range and connection cards are scenario estimates. The
demo uses a land-based route envelope but does not consume live road speed limits, traffic,
elevation, weather, OEM battery data, or a real vehicle position. Their labels deliberately say
`Scenario`, `Simulated`, `Modelled`, and `Synthetic` to prevent them being interpreted as
operational measurements.

Latency is aggregated by minute rather than by date. The demo dataset occurs on one synthetic
date, so daily aggregation would correctly but unhelpfully produce only one point.

### Fleet labels and technical maps

The dashboard maps synthetic fleet identifiers such as `vehicle-0000` to a presentation-only
catalogue of BMW models offered in Brazil. The identifier remains visible beside the model name;
this association is synthetic and does not describe a real vehicle, customer, or BMW fleet.

The Vehicle Systems Map is an original conceptual diagram of connected-vehicle subsystems. Its
markers summarize telematics connectivity, battery-temperature context, tyre status, and the
active HMI screen for the selected synthetic event. It is neither a physical vehicle schematic
nor an OEM diagnostic result.

The Technical 3D Connectivity Incident Map shows only `DEGRADED` and `OFFLINE` events for the
selected synthetic journey. Its horizontal axes are the generated longitude and latitude and its
vertical axis is service latency. Hover details retain six-decimal coordinate precision, route
segment, road class, packet loss, and offline duration. The geography is a declared synthetic
route envelope, not a record of real vehicle positions.

## Streamlit Community Cloud

Use the GitHub repository `Leoboas/drivesense-connected-vehicle-platform`, branch `main`, and main file `app/dashboard.py`. The public application uses only the versioned synthetic sample; it does not receive AWS credentials or access the project S3 buckets. Publish only after the reviewed `develop` to `main` release PR has merged, so the public source and public dashboard stay aligned.
