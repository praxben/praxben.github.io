"""Refresh data/feed.json from the PraxBen YouTube channel and Substack.

Runs nightly in GitHub Actions (see .github/workflows/update-feeds.yml) and can be
run by hand: python .github/scripts/update_feeds.py
Standard library only. Keeps everything it has seen before, so long-form videos
don't disappear when they scroll out of YouTube's 15-item feed.
"""
import json, os, urllib.request, urllib.error, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html import unescape

CHANNEL_ID = "UCyUa016YoiY3cExu1mYDU6g"
SUBSTACK = "https://praxben.substack.com/feed"
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "data", "feed.json")
UA = {"User-Agent": "Mozilla/5.0 (compatible; praxben-site-feed/1.0)"}
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015", "media": "http://search.yahoo.com/mrss/"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return r.read()


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def is_short(video_id):
    """YouTube serves /shorts/<id> directly for Shorts and redirects for normal videos."""
    opener = urllib.request.build_opener(NoRedirect)
    req = urllib.request.Request(f"https://www.youtube.com/shorts/{video_id}", headers=UA, method="HEAD")
    try:
        return opener.open(req, timeout=20).status == 200
    except urllib.error.HTTPError:
        return False


def load_old():
    try:
        with open(OUT, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"videos": [], "shorts": [], "posts": []}


def merge(old, new, key):
    seen = {item[key]: item for item in old}
    for item in new:
        seen[item[key]] = {**seen.get(item[key], {}), **item}
    return sorted(seen.values(), key=lambda x: x["published"], reverse=True)


def youtube(old):
    root = ET.fromstring(get(f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"))
    known = {v["id"]: "video" for v in old["videos"]} | {v["id"]: "short" for v in old["shorts"]}
    videos, shorts = [], []
    for e in root.findall("a:entry", NS):
        vid = e.findtext("yt:videoId", namespaces=NS)
        item = {"id": vid, "title": e.findtext("a:title", namespaces=NS), "published": e.findtext("a:published", namespaces=NS)}
        kind = known.get(vid) or ("short" if is_short(vid) else "video")
        (shorts if kind == "short" else videos).append(item)
    return videos, shorts


def substack():
    root = ET.fromstring(get(SUBSTACK))
    posts = []
    for it in root.iter("item"):
        pub = datetime.strptime(it.findtext("pubDate"), "%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=timezone.utc)
        posts.append({
            "url": it.findtext("link"),
            "title": unescape(it.findtext("title") or ""),
            "subtitle": unescape(it.findtext("description") or ""),
            "published": pub.isoformat(),
        })
    return posts


def main():
    old = load_old()
    data = dict(old)
    try:
        v, s = youtube(old)
        data["videos"], data["shorts"] = merge(old["videos"], v, "id"), merge(old["shorts"], s, "id")
    except Exception as ex:  # keep last good data if YouTube is down
        print("YouTube update failed:", ex)
    try:
        data["posts"] = merge(old["posts"], substack(), "url")
    except Exception as ex:
        print("Substack update failed:", ex)
    data["updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f"{len(data['videos'])} videos, {len(data['shorts'])} shorts, {len(data['posts'])} posts")


if __name__ == "__main__":
    main()
