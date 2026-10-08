**A damn vulnerable server!**

# FACTORY SECURITY LAB
```text
FACTORY SECURITY LAB
│
├── 01. SQL Injection
│   └── Login                      (demonstration only - no flag of its own)
│
├── 02. SQL Injection
│   └── Employee Search            -> flag_001
│
├── 03. IDOR
│   └── Employee Profiles          -> flag_002
│
├── 04. IDOR
│   └── Grievances                 -> flag_003
│
├── 05. Path Traversal
│   └── Factory Documents          -> flag_004
│
├── 06. Broken Access Control
│   └── Factory Admin Panel        (no flag of its own - exposes flag_002 again)
│
└── Bonus. Inspect Element
    └── CCTV Page                  -> flag_005
```

## Bonus flag (optional, not required for the reward page)

`/robots.txt` is public (no login needed) and carries a standalone bonus flag
in a comment. It is unrelated to flag_001-005 and is not part of `FINAL_FLAGS`
or the reward-page URL - finding it has no effect on reaching the final page.

Each flag ends in `_NNN` (e.g. `..._001`). That number is the position of that
flag in the final hidden page's URL, not a hint about solve order.

## Final hidden page

Once a team has all five flags, concatenating them in numbered order and
visiting that path reveals a reward page:

    /{flag_001}{flag_002}{flag_003}{flag_004}{flag_005}

(no separators between flags). Any other path, or the flags out of order,
is a plain 404, so the page stays hidden until solved. The list lives in
`FINAL_FLAGS` near the bottom of `app.py` — edit it if you change any flag.

The page itself (`templates/final.html`) is blank except for one image and
one gif. Drop your own files in as:

    deploy/vulnerable-factory-dashboard/static/congrats/congrats.jpg
    deploy/vulnerable-factory-dashboard/static/congrats/congrats.gif

(rename or edit `final.html` if yours use different names/extensions).

----

# NOTICES & ALERTS (organizer only)

Participants see a read-only **Notices & Alerts** page after logging in.
Posts are added from the organizer machine with `post_notice.py`
(keep it outside the deployed project folder):

    python post_notice.py "Furnace 2 overheating" --photo furnace2.png --level Critical
    python post_notice.py "Shift change in 10 minutes"
    python post_notice.py --list
    python post_notice.py --delete 3

Levels: Info, Warning, Critical. New posts show up on open pages within ~8 seconds.
Data lives in `deploy/vulnerable-factory-dashboard/notices/` (images + `notices.json`), no database.
For several instances, set the same `NOTICES_DIR` for every instance and for this script.
