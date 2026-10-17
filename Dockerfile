FROM python:3.11-slim AS builder
WORKDIR /build
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir --prefix=/install .

FROM python:3.11-slim
RUN addgroup --system drivesense && adduser --system --ingroup drivesense drivesense
WORKDIR /app
COPY --from=builder /install /usr/local
COPY scripts ./scripts
USER drivesense
ENTRYPOINT ["python", "scripts/generate_telemetry.py"]

