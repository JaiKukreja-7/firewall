# Deploy without local software installation

Render hosts the live Python read-only reporting API and static dashboard. Vercel hosts the static dashboard, documents and recorded SQLite evidence. Both can import this GitHub repository through their browser UI; no Mac CLI or package installation is required. The Render API runs real SQLite queries on a synthetic local fixture, not industrial network traffic. Vercel has no live database service in this configuration.

## Render

Import `JaiKukreja-7/firewall` as a Blueprint and select `render.yaml`, or create a Python Web Service with build command `python3 tools/build_site.py && python3 -m unittest discover -s tests -v`, start command `python3 server.py --host 0.0.0.0`, and health path `/health`. No secrets are required. `PORT` is supplied by the host. No custom installation commands are needed. The temporary SQLite fixture initializes at startup and uses synthetic telemetry. Persistence is unnecessary.

The manifest selects Render's free plan; account eligibility and current limits must be checked in Render. A free service may sleep when idle and take time to wake. This configuration makes no claim about currently published platform pricing.

## Vercel

Import the repository, choose Other framework and the repository root, and use `vercel.json`. Static files are prebuilt in `site/`; no build or install command is necessary. Run `python3 tools/build_site.py` in the existing cloud environment to refresh checked-in assets after source updates. The reporting page explicitly labels build-time evidence instead of claiming live database checks.

## Hosting validation

Check `/`, `/reporting.html`, `/submission.html` and the report/presentation downloads. On Render require `/health` HTTP 200, reporting mode `Live SQLite read-only checks`, and 13/13 reporting results. On Vercel require the reporting page to show recorded static evidence. The network dashboard must still pass 20/20 policy checks. No hosted frontend result establishes Packet Tracer validation.

Hosting account authentication is required to create a project or deploy. A source push, prepared manifest, or local test does not prove a live deployment. Record the platform URL and test it after actual publication.
