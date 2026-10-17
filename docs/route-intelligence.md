# Route Intelligence baseline

Each route segment carries distance, travel time, positive elevation change, connectivity score and energy cost. The V1 score is deliberately explainable: it subtracts penalties for distance-weighted predicted offline probability, time, energy and uphill elevation from 100. It is an experimental prioritization heuristic, not a scientific model or navigation recommendation.

When the calculated offline probability exceeds a configurable threshold (default 0.40), the platform emits the equivalent of an `OFFLINE_ZONE_PREDICTED` decision: cache map data, route instructions and POI data before entry. V1 simulates those cache flags rather than distributing real maps.

