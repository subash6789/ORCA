import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin

from db_connection import get_connection


BASE_URL = "https://www.incois.gov.in/MarineFisheries/"

HOME_URL = (
    "https://www.incois.gov.in/"
    "MarineFisheries/TextDataHome"
    "?mfid=1&request_locale=en"
)


SECTORS = {
    "SEC001": "Gujarat",
    "SEC002": "Maharashtra",
    "SEC003": "Goa",
    "SEC004": "Karnataka",
    "SEC005": "Kerala",
    "SEC006": "South Tamil Nadu",
    "SEC007": "North Tamil Nadu",
    "SEC008": "South Andhra Pradesh",
    "SEC009": "North Andhra Pradesh",
    "SEC010": "Odisha",
    "SEC011": "West Bengal",
    "SEC012": "Andaman",
    "SEC013": "Nicobar",
    "SEC014": "Lakshadweep",
}


def create_pfz_table():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pfz_advisory (
            id SERIAL PRIMARY KEY,

            advisory_date DATE,
            valid_upto DATE,

            sector VARCHAR(100),
            landing_centre VARCHAR(200),

            direction VARCHAR(20),
            bearing_deg DOUBLE PRECISION,

            distance_from_km DOUBLE PRECISION,
            distance_to_km DOUBLE PRECISION,

            depth_from_m DOUBLE PRECISION,
            depth_to_m DOUBLE PRECISION,

            latitude DOUBLE PRECISION,
            longitude DOUBLE PRECISION,

            source VARCHAR(200),
            data_status VARCHAR(50),

            retrieved_at TIMESTAMP NOT NULL,

            UNIQUE (
                valid_upto,
                sector,
                landing_centre,
                latitude,
                longitude
            )
        )
    """)

    conn.commit()

    cursor.close()
    conn.close()

    print("PFZ advisory table: READY")


def dms_to_decimal(value):

    if not value:
        return None

    value = value.strip()

    match = re.match(
        r"(\d+)\s+(\d+)\s+([\d.]+)\s*([NSEW])",
        value,
        re.IGNORECASE
    )

    if not match:
        return None

    degrees = float(match.group(1))
    minutes = float(match.group(2))
    seconds = float(match.group(3))

    direction = match.group(4).upper()

    decimal = (
        degrees
        + minutes / 60
        + seconds / 3600
    )

    if direction in ("S", "W"):
        decimal = -decimal

    return round(decimal, 6)


def parse_range(value):

    if not value:
        return None, None

    value = value.strip()

    value = value.replace("–", "-")
    value = value.replace("—", "-")

    match = re.match(
        r"([\d.]+)\s*-\s*([\d.]+)",
        value
    )

    if not match:
        return None, None

    return (
        float(match.group(1)),
        float(match.group(2))
    )


def extract_dates(text):

    if not text:
        return None, None

    matches = re.findall(
        r"\b(\d{1,2})\s+"
        r"(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)"
        r"\s+(\d{4})\b",
        text.upper()
    )

    dates = []

    for day, month, year in matches:

        try:

            value = datetime.strptime(
                f"{day} {month} {year}",
                "%d %b %Y"
            ).date()

            if value not in dates:
                dates.append(value)

        except ValueError:
            pass

    if len(dates) >= 2:

        return dates[0], dates[1]

    if len(dates) == 1:

        return dates[0], None

    return None, None


def fetch_sector(session, secid):

    sector_name = SECTORS.get(
        secid,
        secid
    )

    print()
    print(
        f"Processing {sector_name} "
        f"({secid})..."
    )

    home_response = session.get(
        HOME_URL,
        timeout=60
    )

    home_response.raise_for_status()

    soup = BeautifulSoup(
        home_response.text,
        "html.parser"
    )

    target_link = None

    for option in soup.find_all("option"):

        value = option.get(
            "value",
            ""
        )

        if secid in value:

            target_link = value
            break

    if not target_link:

        print(
            f"{sector_name}: "
            "sector link not found"
        )

        return []

    target_link = target_link.replace(
        "&amp;",
        "&"
    )

    detail_url = urljoin(
        BASE_URL,
        target_link
    )

    print(
        f"INCOIS endpoint found: "
        f"{detail_url}"
    )

    detail_response = session.get(
        detail_url,
        timeout=60
    )

    detail_response.raise_for_status()

    detail_soup = BeautifulSoup(
        detail_response.text,
        "html.parser"
    )

    page_text = detail_soup.get_text(
        " ",
        strip=True
    )

    advisory_date, valid_upto = extract_dates(
        page_text
    )

    print(
        f"Advisory date: "
        f"{advisory_date}"
    )

    print(
        f"Valid upto: "
        f"{valid_upto}"
    )

    results = []

    for table in detail_soup.find_all("table"):

        headers = [
            th.get_text(
                " ",
                strip=True
            ).lower()
            for th in table.find_all("th")
        ]

        header_text = " ".join(headers)

        required_headers = (
            "from the coast of",
            "direction",
            "bearing",
            "distance",
            "depth",
            "latitude",
            "longitude"
        )

        if not all(
            item in header_text
            for item in required_headers
        ):
            continue

        rows = table.find_all("tr")

        for row in rows:

            cells = row.find_all("td")

            if len(cells) < 7:
                continue

            values = [
                cell.get_text(
                    " ",
                    strip=True
                )
                for cell in cells
            ]

            landing_centre = values[0]
            direction = values[1]

            try:

                bearing = float(
                    values[2]
                )

            except ValueError:

                continue

            distance_from, distance_to = (
                parse_range(values[3])
            )

            depth_from, depth_to = (
                parse_range(values[4])
            )

            latitude = dms_to_decimal(
                values[5]
            )

            longitude = dms_to_decimal(
                values[6]
            )

            if not landing_centre:
                continue

            if latitude is None:
                continue

            if longitude is None:
                continue

            results.append({
                "advisory_date": advisory_date,
                "valid_upto": valid_upto,

                "sector": sector_name,

                "landing_centre": landing_centre,

                "direction": direction,

                "bearing_deg": bearing,

                "distance_from_km": distance_from,
                "distance_to_km": distance_to,

                "depth_from_m": depth_from,
                "depth_to_m": depth_to,

                "latitude": latitude,
                "longitude": longitude,

                "source": (
                    "INCOIS Potential Fishing "
                    "Zone Advisory"
                ),

                "data_status": "CURRENT_ADVISORY",

                "retrieved_at": datetime.now()
            })

        break

    print(
        f"{sector_name}: "
        f"{len(results)} PFZ rows detected"
    )

    return results


def save_pfz(results):

    if not results:

        print(
            "No PFZ rows available "
            "for database update."
        )

        return

    conn = get_connection()
    cursor = conn.cursor()

    inserted = 0
    updated = 0

    for item in results:

        cursor.execute(
            """
            INSERT INTO pfz_advisory (
                advisory_date,
                valid_upto,
                sector,
                landing_centre,
                direction,
                bearing_deg,
                distance_from_km,
                distance_to_km,
                depth_from_m,
                depth_to_m,
                latitude,
                longitude,
                source,
                data_status,
                retrieved_at
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            )
            ON CONFLICT (
                advisory_date,
                sector,
                landing_centre,
                latitude,
                longitude
            )
            DO UPDATE SET
                valid_upto = EXCLUDED.valid_upto,
                direction = EXCLUDED.direction,
                bearing_deg = EXCLUDED.bearing_deg,
                distance_from_km = EXCLUDED.distance_from_km,
                distance_to_km = EXCLUDED.distance_to_km,
                depth_from_m = EXCLUDED.depth_from_m,
                depth_to_m = EXCLUDED.depth_to_m,
                source = EXCLUDED.source,
                data_status = EXCLUDED.data_status,
                retrieved_at = EXCLUDED.retrieved_at
            RETURNING xmax
            """,
            (
                item["advisory_date"],
                item["valid_upto"],
                item["sector"],
                item["landing_centre"],
                item["direction"],
                item["bearing_deg"],
                item["distance_from_km"],
                item["distance_to_km"],
                item["depth_from_m"],
                item["depth_to_m"],
                item["latitude"],
                item["longitude"],
                item["source"],
                item["data_status"],
                item["retrieved_at"]
            )
        )

        result = cursor.fetchone()

        if result and result[0] == 0:
            inserted += 1
        else:
            updated += 1

    conn.commit()

    cursor.close()
    conn.close()

    print()
    print(
        "PFZ database update completed."
    )

    print(
        f"Inserted: {inserted}"
    )

    print(
        f"Updated: {updated}"
    )


def collect_pfz():

    print()
    print("=" * 60)
    print(
        "ORCA REAL PFZ DATA PIPELINE"
    )
    print(
        "Source: INCOIS Potential Fishing Zone Advisory"
    )
    print("=" * 60)

    session = requests.Session()

    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/142.0 Safari/537.36"
        )
    })

    all_results = []

    for secid in SECTORS:

        try:

            results = fetch_sector(
                session,
                secid
            )

            all_results.extend(
                results
            )

        except Exception as error:

            print(
                f"{SECTORS[secid]}: "
                f"ERROR - {error}"
            )

    print()
    print(
        f"Total PFZ rows collected: "
        f"{len(all_results)}"
    )

    save_pfz(
        all_results
    )

    return all_results


if __name__ == "__main__":

    create_pfz_table()

    results = collect_pfz()

    print()
    print(
        "ORCA INCOIS PFZ processing "
        "completed."
    )

    print(
        f"Total records: "
        f"{len(results)}"
    )