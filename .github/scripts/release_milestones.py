#!/usr/bin/env python3
"""Keep GitHub milestones in step with the `release: *` labels.

One milestone per upcoming release, titled with its version ("7.2.0") and
due on its release-train date (docs/release-policy.md section 6, ADR 0148).
The label is the only input: milestones are never set by hand, every run
recomputes them for all unreleased labelled issues.

Usage (GITHUB_TOKEN and GITHUB_REPOSITORY in the environment):
  release_milestones.py sync            assign/clear milestones
  release_milestones.py release vX.Y.Z  close the milestones a release shipped, then sync
  release_milestones.py selftest        check the date and version rules, no network
DRY_RUN=1 prints the changes without making them.
"""
import datetime as dt
import json
import os
import re
import sys
import urllib.parse
import urllib.request

LEVELS = ("patch", "minor", "major")
VERSION = re.compile(r"\d+\.\d+\.\d+")
DESCRIPTION = "Planned, not promised. Set automatically from the release labels (docs/release-policy.md)."


# --- the rules (pure, covered by selftest) ---------------------------------

def parse_version(text):
    return tuple(int(x) for x in text.lstrip("v").split("."))


def next_versions(last_tag):
    major, minor, patch = parse_version(last_tag)
    return {"patch": f"{major}.{minor}.{patch + 1}",
            "minor": f"{major}.{minor + 1}.0",
            "major": f"{major + 1}.0.0"}


def train_day(year, month):
    """The 15th; a weekend moves it to the next Monday (same rule as release-reminders.yml)."""
    day = dt.date(year, month, 15)
    return day + dt.timedelta(days={5: 2, 6: 1}.get(day.weekday(), 0))


def due_date(level, today):
    if level == "patch":  # every other Monday: even ISO weeks
        day = today + dt.timedelta(days=(7 - today.weekday()) % 7)
        while day.isocalendar()[1] % 2:  # a loop, not +7: week 53 is followed by week 1
            day += dt.timedelta(days=7)
        return day
    if level == "minor":
        year, month = today.year, today.month
        if train_day(year, month) < today:
            year, month = (year + 1, 1) if month == 12 else (year, month + 1)
        return train_day(year, month)
    day = train_day(today.year, 12)  # major: the yearly 15 December slot
    return day if day >= today else train_day(today.year + 1, 12)


def highest(levels):
    return max(levels, key=LEVELS.index)


def target_level(own, merged):
    """An issue ships with the highest level already merged (policy section 3:
    a patch due while minor work is on main is released as a minor)."""
    return highest([own, *merged])


def selftest():
    d = dt.date.fromisoformat
    assert next_versions("v7.1.0") == {"patch": "7.1.1", "minor": "7.2.0", "major": "8.0.0"}
    assert due_date("minor", d("2026-11-28")) == d("2026-12-15")
    assert due_date("minor", d("2026-12-15")) == d("2026-12-15")       # due today still counts
    assert due_date("minor", d("2026-12-16")) == d("2027-01-15")       # December rolls into January
    assert due_date("minor", d("2027-05-01")) == d("2027-05-17")       # Saturday 15th -> Monday
    assert due_date("minor", d("2027-08-01")) == d("2027-08-16")       # Sunday 15th -> Monday
    assert due_date("minor", d("2026-11-16")) == d("2026-11-16")       # Sunday 15th, Monday the 16th
    assert due_date("patch", d("2026-11-28")) == d("2026-12-07")       # week 49 is odd -> week 50
    assert due_date("patch", d("2026-12-07")) == d("2026-12-07")       # an even Monday is due itself
    assert due_date("patch", d("2026-12-22")) == d("2027-01-11")       # week 53, week 1 both odd
    assert due_date("major", d("2026-11-28")) == d("2026-12-15")
    assert due_date("major", d("2026-12-16")) == d("2027-12-15")
    assert target_level("patch", []) == "patch"
    assert target_level("patch", ["patch", "minor"]) == "minor"
    assert target_level("major", ["minor"]) == "major"
    print("selftest ok")


# --- GitHub ------------------------------------------------------------------

def api(method, path, body=None):
    if method != "GET" and os.environ.get("DRY_RUN"):  # DRY_RUN=1: read the repo, print, write nothing
        return {"number": f"new {body and body.get('title')}", "title": body and body.get("title")}
    request = urllib.request.Request(
        f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}{path}",
        method=method,
        data=None if body is None else json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
                 "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28"})
    with urllib.request.urlopen(request) as response:
        data = response.read()
    return json.loads(data) if data else None


def all_pages(path, **params):
    items, page = [], 1
    while True:
        query = urllib.parse.urlencode({**params, "per_page": 100, "page": page})
        chunk = api("GET", f"{path}?{query}")
        items += chunk
        if len(chunk) < 100:
            return items
        page += 1


def issue_level(issue):
    levels = [level for level in LEVELS
              if any(label["name"] == f"release: {level}" for label in issue["labels"])]
    return highest(levels) if levels else None


def unreleased_issues(since):
    """Open issues with a release label, plus labelled issues closed (as completed) since the last release."""
    found = {}
    for level in LEVELS:
        label = f"release: {level}"
        for issue in all_pages("/issues", state="open", labels=label):
            found[issue["number"]] = issue
        for issue in all_pages("/issues", state="closed", labels=label, since=since):
            if issue["closed_at"] > since and issue.get("state_reason") != "not_planned":
                found[issue["number"]] = issue
    return {n: i for n, i in found.items() if "pull_request" not in i}


class Milestones:
    def __init__(self):
        self.by_title = {m["title"]: m for m in all_pages("/milestones", state="open")}

    def get(self, title, due):
        if title not in self.by_title:
            print(f"create milestone {title} due {due}")
            self.by_title[title] = api("POST", "/milestones", {
                "title": title, "description": DESCRIPTION, "due_on": f"{due}T08:00:00Z"})
        return self.by_title[title]

    def versions(self):
        return {t: m for t, m in self.by_title.items() if VERSION.fullmatch(t)}


def set_milestone(issue, milestone):
    current = issue["milestone"]["number"] if issue["milestone"] else None
    wanted = milestone["number"] if milestone else None
    if current != wanted:
        print(f"#{issue['number']}: {issue['milestone'] and issue['milestone']['title']} -> {milestone and milestone['title']}")
        api("PATCH", f"/issues/{issue['number']}", {"milestone": wanted})


def sync(today):
    latest = api("GET", "/releases/latest")
    last_tag, since = latest["tag_name"], latest["published_at"]
    versions = next_versions(last_tag)
    issues = unreleased_issues(since)
    merged = [issue_level(i) for i in issues.values() if i["state"] == "closed"]
    milestones = Milestones()

    for issue in issues.values():
        level = target_level(issue_level(issue), merged)
        set_milestone(issue, milestones.get(versions[level], due_date(level, today)))

    # The label is the only input: an issue that lost it (or was closed as not
    # planned) leaves the milestone; a milestone left empty goes away.
    for title, milestone in milestones.versions().items():
        if not isinstance(milestone["number"], int):
            continue  # only created in a dry run
        kept = 0
        for issue in all_pages("/issues", milestone=milestone["number"], state="all"):
            if issue["number"] in issues:
                kept += 1
            elif "pull_request" in issue or (issue["state"] == "closed" and issue["closed_at"] <= since):
                kept += 1  # PRs and already-shipped history are not ours to clear
            else:
                set_milestone(issue, None)
        if not kept:
            print(f"delete empty milestone {title}")
            api("DELETE", f"/milestones/{milestone['number']}")


def release(tag, today):
    """Everything closed in a milestone up to this version shipped in it: move it
    into the milestone named after the tag and close that one and the old ones."""
    shipped = parse_version(tag)
    milestones = Milestones()
    old = {t: m for t, m in milestones.versions().items() if parse_version(t) <= shipped}
    if not old:
        print(f"no open milestones up to {tag}")
    else:
        target = milestones.get(tag.lstrip("v"), today)
        for milestone in old.values():
            if milestone is target:
                continue
            for issue in all_pages("/issues", milestone=milestone["number"], state="closed"):
                set_milestone(issue, target)
        for title, milestone in old.items():
            print(f"close milestone {title}")
            api("PATCH", f"/milestones/{milestone['number']}", {"state": "closed"})
        if target not in old.values():
            api("PATCH", f"/milestones/{target['number']}", {"state": "closed"})
    sync(today)  # open issues of the closed milestones move on to the next release


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    today = dt.datetime.now(dt.timezone.utc).date()
    if command == "selftest":
        selftest()
    elif command == "sync":
        sync(today)
    elif command == "release" and len(sys.argv) == 3:
        release(sys.argv[2], today)
    else:
        sys.exit(__doc__)
