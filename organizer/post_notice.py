"""
Post, list or delete notices on the factory dashboard (organizer use only).
Keep this file OUTSIDE the deployed project folder.

  python post_notice.py "Furnace 2 overheating" --photo furnace2.png --level Critical
  python post_notice.py "Shift change in 10 minutes"
  python post_notice.py --list
  python post_notice.py --delete 3

Notices folder: $NOTICES_DIR if set, otherwise
../deploy/vulnerable-factory-dashboard/notices relative to this file.
"""
import argparse, json, os, shutil, tempfile, uuid
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
NOTICES_DIR = os.environ.get(
    "NOTICES_DIR",
    os.path.join(HERE, "..", "deploy", "vulnerable-factory-dashboard", "notices"),
)
INDEX = os.path.join(NOTICES_DIR, "notices.json")
LEVELS = ("Info", "Warning", "Critical")


def image_ext(path):
    with open(path, "rb") as f:
        head = f.read(16)
    if head.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if head[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "webp"
    return None


def load():
    try:
        with open(INDEX, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return []


def save(items):
    os.makedirs(NOTICES_DIR, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=NOTICES_DIR, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)
    os.replace(tmp, INDEX)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("comment", nargs="?", default="")
    ap.add_argument("--photo", help="path to a jpg/png/gif/webp file")
    ap.add_argument("--level", default="Info", choices=LEVELS)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--delete", type=int, metavar="ID")
    a = ap.parse_args()
    items = load()

    if a.list:
        for n in sorted(items, key=lambda n: n["id"], reverse=True):
            print("#{id} [{level}] {posted_at}  photo={photo}  {comment}".format(**n))
        return

    if a.delete is not None:
        gone = [n for n in items if n["id"] == a.delete]
        if not gone:
            raise SystemExit("No notice with id {}".format(a.delete))
        if gone[0].get("photo"):
            try:
                os.remove(os.path.join(NOTICES_DIR, gone[0]["photo"]))
            except OSError:
                pass
        save([n for n in items if n["id"] != a.delete])
        print("Deleted #{}".format(a.delete))
        return

    photo = None
    if a.photo:
        ext = image_ext(a.photo)
        if ext is None:
            raise SystemExit("That file is not a supported image.")
        photo = "{}.{}".format(uuid.uuid4().hex, ext)
        os.makedirs(NOTICES_DIR, exist_ok=True)
        shutil.copyfile(a.photo, os.path.join(NOTICES_DIR, photo))
    if not photo and not a.comment.strip():
        raise SystemExit("Give a comment and/or --photo.")

    nid = max([n["id"] for n in items], default=0) + 1
    items.append({
        "id": nid,
        "level": a.level,
        "comment": a.comment.strip(),
        "photo": photo,
        "posted_at": datetime.now().strftime("%d %b %Y, %H:%M:%S"),
    })
    save(items)
    print("Posted #{} ({})".format(nid, a.level))


if __name__ == "__main__":
    main()
