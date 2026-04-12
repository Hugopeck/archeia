# observability

Metrics collection, monitoring, and tracing infrastructure. Provides Prometheus metrics, SLO tracking, OpenTelemetry span export, and application-specific metric collectors.

## Key Concepts

- **Prometheus metrics** -- `metrics.py` defines custom counters and histograms. `http_middleware.py` collects HTTP request metrics.
- **Remote write** -- `remote_write.py` pushes Prometheus metrics to a remote endpoint for centralized monitoring.
- **SLO tracking** -- `slo.py` and `slo_report/` track service-level objectives for checkout, API latency, and error rates.
- **Checkout metrics** -- `checkout_metrics.py` tracks checkout funnel conversion and error rates.
- **S3 span exporter** -- `s3_span_exporter.py` exports OpenTelemetry spans to S3 for Athena-based analysis.

## Usage

Middleware is mounted in `app.py`. Metrics are scraped by Prometheus or pushed via remote write. SLO reports are generated for operational dashboards.

## Learnings

_No learnings recorded yet._
