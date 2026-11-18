import datetime as dt
import json
from pathlib import Path
from urllib.parse import urlsplit

from collect import canonical_url

ROOT = Path(__file__).resolve().parents[1]
ids = set()
job_urls = set()
for kind in ("jobs", "opportunities", "events"):
    rows = json.loads((ROOT / "data" / f"{kind}.json").read_text(encoding="utf-8"))
    assert isinstance(rows, list), kind
    for row in rows:
        assert row["id"] and row["title"] and row["org"], row
        assert row["id"] not in ids, row["id"]
        ids.add(row["id"])
        assert urlsplit(row["url"]).hostname, row["url"]
        canonical_url(row["url"])
        dt.date.fromisoformat(row["last_checked"])
        if row.get("deadline"):
            dt.date.fromisoformat(row["deadline"])
        if kind == "jobs":
            assert row["status"] in {"접수 중", "마감", "확인 필요"}, row
            assert all(row[field] for field in ("work_mode", "korea_eligible", "visa", "region")), row
            url = canonical_url(row["url"])
            assert url not in job_urls, url
            job_urls.add(url)
    print(kind, len(rows))

config = json.loads((ROOT / "config/sources.json").read_text(encoding="utf-8"))
for provider in ("greenhouse", "lever", "manual"):
    for source in config[provider]:
        assert source["name"] and source["region"] in {"한국", "해외"}, source
        canonical_url(source["url"])
        if provider != "manual":
            assert source["token"] and source["focus"] in {"graphics", "visualization"}, source
