![Main Screenshot](custom_components/lsbt/brand/icon.png)

# Lowell School Bus Tracker (LSBT)

An **unofficial, experimental** Home Assistant custom integration for Lowell Public Schools' published school bus data.

**Source limitation:** The district's PM data is on [published Smartsheet](https://publish.smartsheet.com/803c65334ef44a12aced1cbfeaf05927). The prototype handles publicly accessible CSV exports and HTML tables; a Smartsheet JavaScript-only viewer is **not yet supported**. Live source compatibility has not been verified. Do not depend on this integration for student safety or pickup decisions.

## Install

Add this repository as a HACS custom repository (category **Integration**) or copy `custom_components/lsbt` into Home Assistant's `custom_components` directory. Restart Home Assistant, then visit **Settings → Devices & services → Add integration → Lowell School Bus Tracker**.

Configure a route, its school, AM or PM schedule, a public source URL, and polling interval (30–3600 seconds, default 60). PM defaults to the known published Smartsheet page. For AM, the AM published sheet is selected automatically; PM uses a separate published sheet. The source URL may still be overridden during setup. Multiple schools/routes may be added as separate entries.

Sensors: minutes late, covering bus, and status. Blank covering-bus cells display **Not listed** rather than Unknown, with no implication of a delay. Blank delay cells are interpreted as **0 minutes late / on_time** for LSBT reporting. Covering-bus information is informational and does not change delay status; malformed delay values remain unknown. Status is **on_time** for zero delay, **delayed** for a positive delay, and **unknown** for an unreadable value. Notifications are user-created HA automations; the integration does not send alerts automatically. An optional covering-bus change alert can be configured separately. This reflects the published sheet convention, not a guarantee of actual arrival time. Fetch and parsing failures mark entities unavailable instead of returning a false on-time value. HA automations can notify on state changes through the companion app or Telegram.

## Tests

`pip install pytest beautifulsoup4 && pytest -q tests`

## License / attribution

Not affiliated with Lowell Public Schools or Smartsheet. No credentials required.

## Publishing and receiving updates

The integration version lives in `custom_components/lsbt/manifest.json`. For each new version:

1. Commit and push changes, increasing the manifest version (for example, from `0.1.0b1` to `0.1.0b2`).
2. Create and push a tag whose name **exactly matches** the manifest version, at the corresponding commit: `git tag 0.1.0b1 && git push origin 0.1.0b1`. Do not reuse a published tag.
3. GitHub Actions runs the parser tests and verifies the tag/version match, then publishes a GitHub release. Versions ending in `aN`, `bN`, or `rcN` become prereleases.
4. HACS users who enable **prerelease/beta versions** for this repository can receive beta update notices; normal release updates are offered through the integration's update entity. A GitHub release is required for HACS to use the release version.
5. In Home Assistant, open **Settings → Updates** (or the HACS repository page), install the offered update, and **restart Home Assistant**. HACS checks periodically; use the repository's **Update information** / **Redownload** action to refresh sooner.

HACS notification does **not** mean automatic installation, and restarting Home Assistant does not itself download code. If you installed the integration manually rather than through HACS, update the files manually instead.

This is currently an experimental custom repository and not an official HACS catalog entry.

## School selection

During setup, choose the schedule, route number, and source URL first. LSBT downloads the selected route's schools and offers them in a dropdown on the next screen. Names are taken verbatim from the source, so no manual school spelling is needed. If the source cannot be read or the route is absent, setup shows an error instead of offering misleading choices. Existing configured routes are unaffected.


### AM / PM configuration

Setup first asks for AM or PM, then defaults the URL to that schedule's public Smartsheet. Already-configured entries retain their saved URL; if an existing AM entry points to the PM sheet, remove and re-add that entry with the AM schedule or otherwise change its stored source. A blank covering-bus cell displays **Not listed**; the covering-bus sensor is informational only.
