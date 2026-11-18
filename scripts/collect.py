#!/usr/bin/env python3
"""Refresh jobs from public Greenhouse and Lever boards."""
import datetime as dt
import hashlib
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
TODAY = dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).date().isoformat()
MEDICAL = re.compile(r"medical illustrat|scientific illustrat|medical animat|biomedical visual|medical visual|medical imaging|medical 3d|surgical simulat|anatomical artist|3d slicer|biomedical animat", re.I)
VISUAL = re.compile(r"scientific visual|volume render|vtk(?:\.js)?\b|paraview|visualization engineer|visualization software", re.I)
GRAPHICS = re.compile(r"webgl|webgpu|three\.js|graphics engine|graphics engineer|rendering engineer|rendering engine|gpu rendering|shader development|glsl", re.I)
TECHNICAL_TITLE = re.compile(r"engineer|developer|scientist|research|artist|illustrator|animator|graphics|rendering", re.I)


def canonical_url(url):
    parts = urlsplit(url)
    if parts.scheme != "https" or not parts.hostname:
        raise ValueError("Expected an HTTPS posting URL")
    query = sorted((key, value) for key, value in parse_qsl(parts.query)
                   if not key.lower().startswith("utm_") and key not in {"gh_src", "source", "lever-source"})
    return urlunsplit(("https", parts.netloc.lower(), parts.path.rstrip("/"), urlencode(query), ""))


def clean_markup(value):
    return " ".join(re.sub(r"<[^>]+>", " ", html.unescape(value or "")).split())


def fetch_rows(provider, token):
    slug = quote(token, safe="")
    url = {
        "greenhouse": f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true",
        "lever": f"https://api.lever.co/v0/postings/{slug}?mode=json",
    }[provider]
    request = Request(url, headers={"User-Agent": "BioMedicalVisualizationCareers/1.0", "Accept": "application/json"})
    with urlopen(request, timeout=25) as response:
        payload = json.load(response)
    rows = payload["jobs"] if provider == "greenhouse" else payload
    fields = ("id", "title", "absolute_url") if provider == "greenhouse" else ("id", "text", "hostedUrl")
    if not isinstance(rows, list) or any(not isinstance(row, dict) or not all(row.get(key) for key in fields) for row in rows):
        raise ValueError("Invalid posting list")
    if provider == "greenhouse" and payload.get("meta", {}).get("total", len(rows)) != len(rows):
        raise ValueError("Incomplete posting list")
    return rows


def normalize(provider, board, row):
    source = f"{provider}/{board['token']}"
    if provider == "greenhouse":
        title, raw_url = row["title"], row["absolute_url"]
        description = clean_markup(row.get("content"))
        location = (row.get("location") or {}).get("name")
        workplace = employment = None
    else:
        title, raw_url = row["text"], row["hostedUrl"]
        description = " ".join((row.get("descriptionPlain") or "").split())
        categories = row.get("categories") or {}
        location = categories.get("location")
        workplace = row.get("workplaceType")
        employment = categories.get("commitment")

    content = f"{title} {description}"
    if not TECHNICAL_TITLE.search(title):
        return None
    if MEDICAL.search(content):
        category = "의료 일러스트" if re.search(r"illustrat|animat|artist", title, re.I) else "의료 시각화 개발"
    elif board["focus"] == "visualization" and VISUAL.search(content):
        category = "과학 시각화"
    elif board["focus"] == "graphics" and GRAPHICS.search(content):
        category = "WebGL·그래픽스"
    else:
        return None

    url = canonical_url(raw_url)
    identifier = hashlib.sha256(f"{source}/{row['id']}".encode()).hexdigest()[:20]
    mode = {"remote": "원격", "hybrid": "하이브리드", "on-site": "현장", "onsite": "현장"}
    employment_types = {"full time": "풀타임", "part time": "파트타임", "contract": "계약직",
                        "internship": "인턴·연구", "freelance": "프리랜서"}
    return {
        "id": f"j-{identifier}", "title": title, "org": board["name"], "category": category,
        "type": employment_types.get((employment or "").lower().replace("-", " "), "확인 필요"),
        "location": location or "확인 필요", "region": board["region"],
        "work_mode": mode.get((workplace or "").lower(), "확인 필요"),
        "korea_eligible": "확인 필요", "visa": "확인 필요",
        "status": "접수 중", "source": source, "source_url": board["url"], "url": url,
        "first_seen": TODAY, "last_checked": TODAY, "tags": [provider.title()],
    }


def collect(config, previous):
    refreshed = {}
    checked_sources = set()
    failed_sources = set()
    prior_ids = {item["id"]: item for item in previous}
    prior_urls = {canonical_url(item["url"]): item for item in previous if item.get("url")}
    for provider in ("greenhouse", "lever"):
        for board in config[provider]:
            source = f"{provider}/{board['token']}"
            try:
                board_jobs = [normalize(provider, board, row) for row in fetch_rows(provider, board["token"])]
            except (OSError, ValueError, KeyError, TypeError) as error:
                print(f"::warning::{source}: {error}", file=sys.stderr)
                failed_sources.add(source)
                continue
            checked_sources.add(source)
            for job in filter(None, board_jobs):
                prior = prior_ids.get(job["id"]) or prior_urls.get(job["url"])
                if prior:
                    job["id"] = prior["id"]
                    job["first_seen"] = prior.get("first_seen", TODAY)
                refreshed.setdefault(job["url"], job)

    if failed_sources and not checked_sources:
        raise SystemExit("All public boards failed. Keeping the previous snapshot.")

    refreshed_ids = {item["id"] for item in refreshed.values()}
    for old in previous:
        if old["id"] in refreshed_ids:
            continue
        item = dict(old)
        if old.get("source") in checked_sources:
            item.update(status="마감", last_checked=TODAY)
        elif old.get("source") and old["status"] != "마감":
            item["status"] = "확인 필요"
        if item.get("url"):
            refreshed.setdefault(canonical_url(item["url"]), item)
    print(f"Boards verified: {len(checked_sources)}. Failed: {len(failed_sources)}.")
    return sorted(refreshed.values(), key=lambda item: (item["status"] != "접수 중", item["org"], item["title"], item["id"]))


def main():
    config = json.loads((ROOT / "config/sources.json").read_text(encoding="utf-8"))
    target = ROOT / "data/jobs.json"
    previous = json.loads(target.read_text(encoding="utf-8"))
    jobs = collect(config, previous)
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(jobs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(target)


if __name__ == "__main__":
    main()
