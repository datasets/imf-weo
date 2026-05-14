#!/usr/bin/env python3
"""
Fetch the IMF World Economic Outlook (WEO) dataset via the IMF SDMX API.

Requires Python 3.8+ and:
    pip install sdmx1 pandas

Output: data/values.csv, data/indicators.csv, data/country.csv
"""
import csv
import json
import logging
import os
import urllib.request

import sdmx

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

SDMX_SOURCE = "IMF_DATA"
DATAFLOW = "WEO"
DATA_DIR = "data"
DATAMAPPER_BASE = "https://www.imf.org/external/datamapper/api/v1"


def _fetch_json(url, timeout=30):
    with urllib.request.urlopen(url, timeout=timeout) as f:
        return json.loads(f.read().decode())


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def discover_indicators(client):
    """Return sorted list of WEO indicator codes from SDMX (uses USA as probe)."""
    logger.info("Discovering available WEO indicators...")
    resp = client.data(DATAFLOW, key="USA..A")
    df = sdmx.to_pandas(resp)
    indicators = sorted(df.index.get_level_values("INDICATOR").unique().tolist())
    logger.info("  %d indicators found", len(indicators))
    return indicators


def fetch_indicator_metadata():
    """Return {id: {label, description, unit}} from IMF DataMapper API."""
    logger.info("Fetching indicator metadata from DataMapper API...")
    data = _fetch_json(f"{DATAMAPPER_BASE}/indicators")
    return data.get("indicators", {})


def fetch_country_names():
    """Return {iso3: name} from IMF DataMapper API."""
    logger.info("Fetching country names from DataMapper API...")
    data = _fetch_json(f"{DATAMAPPER_BASE}/countries")
    return {k: v.get("label", "") for k, v in data.get("countries", {}).items()}


def extract():
    _ensure_data_dir()
    client = sdmx.Client(SDMX_SOURCE)

    indicators = discover_indicators(client)

    # --- values.csv ---
    all_values = []
    countries_seen = set()

    for i, ind in enumerate(indicators, 1):
        logger.info("[%d/%d] Fetching %s ...", i, len(indicators), ind)
        try:
            resp = client.data(DATAFLOW, key=f".{ind}.A")
            df = sdmx.to_pandas(resp).reset_index()
        except Exception as e:
            logger.warning("  SKIP %s: %s", ind, e)
            continue

        for _, row in df.iterrows():
            country = row["COUNTRY"]
            countries_seen.add(country)
            all_values.append({
                "Country": country,
                "Indicator": ind,
                "Year": row["TIME_PERIOD"],
                "Value": row["value"],
            })
        logger.info("  -> %d rows across %d countries", len(df), df["COUNTRY"].nunique())

    values_path = os.path.join(DATA_DIR, "values.csv")
    with open(values_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Country", "Indicator", "Year", "Value"])
        writer.writeheader()
        writer.writerows(all_values)
    logger.info("Wrote %s (%d rows)", values_path, len(all_values))

    # --- indicators.csv ---
    meta = fetch_indicator_metadata()
    ind_path = os.path.join(DATA_DIR, "indicators.csv")
    with open(ind_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "title", "description", "units", "scale"])
        for ind in indicators:
            m = meta.get(ind, {})
            label = m.get("label", ind)
            unit = m.get("unit", "")
            title = f"{label} ({unit})" if unit else label
            writer.writerow([ind, title, m.get("description", ""), unit, ""])
    logger.info("Wrote %s", ind_path)

    # --- country.csv ---
    country_names = fetch_country_names()
    country_path = os.path.join(DATA_DIR, "country.csv")
    with open(country_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ISO", "Name"])
        for iso in sorted(countries_seen):
            writer.writerow([iso, country_names.get(iso, "")])
    logger.info("Wrote %s (%d countries)", country_path, len(countries_seen))

    logger.info("Extraction complete.")


if __name__ == "__main__":
    extract()
