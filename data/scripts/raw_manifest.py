"""Size and sha256 of every file under data/raw, as JSON and as a Markdown table.

Usage:
  python3 -I data/scripts/raw_manifest.py data/raw data/raw_manifest.json
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import sha256_of, write_json  # noqa: E402


def main(argv):
    raw_dir, out_path = argv[1], argv[2]
    rows = []
    for folder, _, files in sorted(os.walk(raw_dir)):
        for name in sorted(files):
            if name == ".DS_Store":
                continue
            path = os.path.join(folder, name)
            rows.append({
                "path": os.path.relpath(path, raw_dir),
                "bytes": os.path.getsize(path),
                "sha256": sha256_of(path),
            })
    write_json(out_path, {"files": rows, "total_bytes": sum(r["bytes"] for r in rows)})
    print("| File | Bytes | sha256 |")
    print("|---|---:|---|")
    for row in rows:
        print(f"| `{row['path']}` | {row['bytes']} | `{row['sha256']}` |")
    print("total", len(rows), "files", sum(r["bytes"] for r in rows), "bytes")


if __name__ == "__main__":
    main(sys.argv)
