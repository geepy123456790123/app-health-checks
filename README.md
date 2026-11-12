# Public application health checks

Samewhere's public production health endpoint is checked hourly at 17 minutes past the hour (UTC). GitHub may delay scheduled jobs. Use the latest Actions run for the latest check result.

The check requires both `status: ok` and `release: production`, and retries transient failures before failing the job. Real failures retain GitHub Actions failure notifications.

`status.json` records a daily snapshot and any status change. Daily status commits also maintain repository activity so GitHub does not disable this otherwise quiet repository's scheduled workflow for inactivity.

The workflow uses standard runners in a public repository, which are free and do not consume the private-repository Actions allowance. It accesses only the public health endpoint and requires no application secrets or private source checkout.

Run manually from Actions, or locally with `python3 check_health.py`. Run the monitor's tests with `python3 -m unittest -v`.
