# Lowell School Bus Tracker (LSBT)

An **unofficial, experimental** Home Assistant custom integration for Lowell Public Schools' published school bus data.

**Source limitation:** The district's PM data is on [published Smartsheet](https://publish.smartsheet.com/803c65334ef44a12aced1cbfeaf05927). The prototype handles publicly accessible CSV exports and HTML tables; a Smartsheet JavaScript-only viewer is **not yet supported**. Live source compatibility has not been verified. Do not depend on this integration for student safety or pickup decisions.

## Install

Add this repository as a HACS custom repository (category **Integration**) or copy `custom_components/lsbt` into Home Assistant's `custom_components` directory. Restart Home Assistant, then visit **Settings → Devices & services → Add integration → Lowell School Bus Tracker**.

Configure a route, its school, AM or PM schedule, a public source URL, and polling interval (30–3600 seconds, default 60). PM defaults to the known published Smartsheet page. For AM you must supply the actual AM source URL. Multiple schools/routes may be added as separate entries.

Sensors: minutes late, covering bus, and status. Blank delay cells are interpreted as **0 minutes late / on_time** for LSBT reporting. A covering bus still produces **covering_bus** status; malformed delay values remain unknown. This reflects the published sheet convention, not a guarantee of actual arrival time. Fetch and parsing failures mark entities unavailable instead of returning a false on-time value. HA automations can notify on state changes through the companion app or Telegram.

## Tests

`pip install pytest beautifulsoup4 && pytest -q tests`

## License / attribution

Not affiliated with Lowell Public Schools or Smartsheet. No credentials required.
