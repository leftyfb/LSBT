"""Parse plain published HTML tables and CSV route exports.

Does not support JavaScript-only Smartsheet pages. Rejects unreadable pages
instead of silently treating missing data as an on-time bus.
"""
import csv
from io import StringIO
from bs4 import BeautifulSoup

def parse_routes(content, content_type="text/html"):
    if "csv" in content_type.lower() or (not content.lstrip().startswith("<") and "," in content[:200]):
        rows = list(csv.reader(StringIO(content)))
    else:
        soup = BeautifulSoup(content, "html.parser")
        rows = []
        for table in soup.select("table"):
            candidate = [[cell.get_text(" ", strip=True) for cell in tr.select("th,td")] for tr in table.select("tr")]
            if candidate and any("school" in cell.lower() for cell in candidate[0]):
                rows = candidate
                break
    if not rows:
        raise ValueError("No accessible route table (possibly a JavaScript-only page)")
    headers = [" ".join(c.lower().split()) for c in rows[0]]
    route_column = next((i for i, name in enumerate(headers) if "route" in name or name in ("bus", "bus #")), None)
    if route_column is None:
        raise ValueError("Route column not found")
    schools = [i for i, name in enumerate(headers) if "school" in name and "late" not in name]
    if not schools:
        raise ValueError("School columns not found")
    result = []
    for cells in rows[1:]:
        if len(cells) <= route_column or not cells[route_column].strip():
            continue
        record = {"route": cells[route_column].strip(), "schools": []}
        for i, start in enumerate(schools):
            if start >= len(cells) or not cells[start].strip():
                continue
            end = schools[i + 1] if i + 1 < len(schools) else len(headers)
            delay, cover = None, None
            for j in range(start + 1, min(end, len(cells), len(headers))):
                name, value = headers[j], cells[j].strip()
                if ("late" in name or "delay" in name) and value:
                    try:
                        delay = int(value.lstrip("+").split()[0])
                    except ValueError:
                        pass
                if "cover" in name or "replacement" in name:
                    cover = value or None
            record["schools"].append({"school": cells[start].strip(), "minutes_late": delay, "covering_bus": cover})
        if record["schools"]:
            result.append(record)
    if not result:
        raise ValueError("No route records found")
    return result

def find_school(routes, route, school):
    for row in routes:
        if row["route"].casefold() != str(route).strip().casefold():
            continue
        for item in row["schools"]:
            if item["school"].casefold() == school.strip().casefold():
                delay = item["minutes_late"]
                status = ("delay_reported" if delay is not None and delay > 0
                          else "covering_bus" if item["covering_bus"] else "no_delay_reported")
                return {**item, "route": row["route"], "status": status}
    return None
