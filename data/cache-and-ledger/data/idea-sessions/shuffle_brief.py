"""Reorder the measured facts and the excluded ideas of the brief with a seeded shuffle."""
import random
import re
import sys
from pathlib import Path

brief, seed, out = Path(sys.argv[1]).read_text(encoding="utf-8"), int(sys.argv[2]), Path(sys.argv[3])
rng = random.Random(seed)
head, rest = brief.split("Summary of the facts:\n\n", 1)
facts_text, rest = rest.split("\n## Already on the table", 1)
facts = [re.sub(r"^\d+\.\s", "", f.strip(), count=1) for f in re.split(r"\n(?=\d+\. )", facts_text.strip())]
order = list(range(len(facts)))
rng.shuffle(order)
facts_out = "\n".join(f"{i}. {facts[j]}" for i, j in enumerate(order, 1))
intro, rest = rest.split("\n\n", 1)
banned_text, tail = rest.split("\n\nCombinations", 1)
banned = banned_text.strip().split("\n")
rng.shuffle(banned)
out.write_text(head + "Summary of the facts:\n\n" + facts_out + "\n\n## Already on the table" + intro
               + "\n\n" + "\n".join(banned) + "\n\nCombinations" + tail, encoding="utf-8")
print(seed, "fact order:", [j + 1 for j in order])
