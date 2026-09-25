"""
Checks #6 and #7 in one run.  From the project root:  python check_6_and_7.py

#6 -- Typo-corrector sanity check. Runs normalize_query() on a mix of:
   (a) ordinary, correctly-spelled sentences that should come back UNCHANGED
   (b) real typos in domain words that SHOULD get corrected
   Flags anything in (a) that got changed -- that's a false-positive
   "correction" mangling a normal word.

#7 -- Vector-store freshness. Compares the newest knowledge-base .md file's
   modified time against ugbs_welfare_db/chroma.sqlite3's modified time.
   If a .md file was edited more recently than the store was built, the new
   content (e.g. the STS FAQ merge) is NOT actually indexed yet, no matter
   what's in the .md files on disk.
"""
import os
from pathlib import Path
from datetime import datetime

import config
from risk_classifier import normalize_query

# --- #6: typo-corrector sanity check --------------------------------------
print("=" * 70)
print("#6 -- TYPO-CORRECTOR SANITY CHECK")
print("=" * 70)

# (a) Ordinary sentences that should NOT be touched at all.
SHOULD_STAY_UNCHANGED = [
    "I am walking to class right now",
    "My roommate is talking too loud at night",
    "I have a meeting with my friend later today",
    "I am feeling really tired after studying all night",
    "Can you help me plan my week better",
    "I want to join a new club or society this semester",
    "The weather has been really nice this week",
    "I need advice on making new friends",
    "My phone battery keeps dying so fast",
    "I am thinking about changing my daily routine",
]

# (b) Genuine typos in domain-relevant words -- SHOULD get corrected.
SHOULD_GET_CORRECTED = [
    "I need help with my schlarship application",
    "I want to defere my programme this semester",
    "How do I register for my curses next semester",
    "I was harrased by another student",
    "My hstel roommate keeps taking my things",
]

print("\n--- (a) Ordinary sentences -- expect NO changes ---\n")
false_positives = 0
for s in SHOULD_STAY_UNCHANGED:
    out = normalize_query(s)
    changed = (out != s)
    flag = "  !! CHANGED (false positive)" if changed else ""
    print(f"  IN:  {s}")
    if changed:
        print(f"  OUT: {out}{flag}")
        false_positives += 1
    print()

print("--- (b) Real typos in domain words -- expect corrections ---\n")
missed = 0
for s in SHOULD_GET_CORRECTED:
    out = normalize_query(s)
    changed = (out != s)
    flag = "" if changed else "  !! NOT corrected (missed)"
    print(f"  IN:  {s}")
    print(f"  OUT: {out}{flag}")
    if not changed:
        missed += 1
    print()

print("-" * 70)
if false_positives == 0:
    print(f"#6 RESULT: OK -- no ordinary sentence was incorrectly changed.")
else:
    print(f"#6 RESULT: !! {false_positives} ordinary sentence(s) were incorrectly "
          f"'corrected'. The 0.85 cutoff may still be too loose for those "
          f"specific words -- see which ones above and consider raising it "
          f"further or excluding those words.")
if missed > 0:
    print(f"           (Also: {missed} real typo(s) were NOT corrected -- less "
          f"urgent than false positives, but worth a look if it's a common word.)")

# --- #7: vector-store freshness -------------------------------------------
print()
print("=" * 70)
print("#7 -- VECTOR STORE FRESHNESS")
print("=" * 70)

root = Path(".").resolve()
db_sqlite = root / "ugbs_welfare_db" / "chroma.sqlite3"

if not db_sqlite.exists():
    print("!! ugbs_welfare_db/chroma.sqlite3 not found -- the vector store "
          "hasn't been built at all yet. Run: python build_vectorstore.py")
else:
    db_time = datetime.fromtimestamp(db_sqlite.stat().st_mtime)
    kb_files = [root / f for f in config.MARKDOWN_FILES if (root / f).exists()]
    newest_kb = max(kb_files, key=lambda p: p.stat().st_mtime)
    kb_time = datetime.fromtimestamp(newest_kb.stat().st_mtime)

    print(f"Vector store last built:     {db_time:%Y-%m-%d %H:%M}")
    print(f"Newest knowledge-base file:  {kb_time:%Y-%m-%d %H:%M}  ({newest_kb.name})")

    if kb_time > db_time:
        print("\n!! STALE: at least one .md file (including possibly your STS FAQ "
              "merge into ug_academic_affairs_qna.md / sfao_financial_aid.md) was "
              "edited AFTER the vector store was last built. That new content is "
              "NOT actually searchable yet.")
        print("   Fix: run `python build_vectorstore.py` now.")
    else:
        print("\nOK: vector store is newer than all knowledge-base files -- "
              "your STS FAQ merge (and anything else) is already indexed.")