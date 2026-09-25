"""
Standalone test for the combined answer+action-plan LLM call.
Run from the project root:   python test_combined_call.py

Does NOT touch Streamlit or the chat UI -- it calls llm_engine directly with
a real retrieved chunk from your actual vector store, so this is a true test
of your actual Ollama model's behavior with the new combined prompt.

Prints:
  1. Whether the OLD two-call approach and the NEW combined call both work
  2. How long each took (wall-clock seconds)
  3. The actual answer + plan text from the new combined call, so you can
     see with your own eyes whether the delimiter parsing worked cleanly
     (no stray "===ACTION_PLAN===" text, no empty plan, etc.)
"""
import time
import sys

import config
import llm_engine

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

TEST_QUERY = "I can't pay my fees this semester, what can I do?"
TEST_CATEGORY = "Financial Distress"

print(f"LLM_PROVIDER = {config.LLM_PROVIDER}")
print(f"llm_is_configured() = {config.llm_is_configured()}")
print()

if not config.llm_is_configured():
    print("!! No LLM configured -- this test would only exercise the template")
    print("   fallback paths, not a real model. Set up Ollama/Gemini/Anthropic")
    print("   in .env first, then re-run this.")
    sys.exit(1)

print("Loading vector store and running a real retrieval for the test query...")
embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL_NAME)
vectorstore = Chroma(persist_directory=config.DB_DIR, embedding_function=embeddings)
results = vectorstore.similarity_search_with_score(TEST_QUERY, k=3)

if not results:
    print("!! No retrieval results at all -- is ugbs_welfare_db/ built? "
          "Run build_vectorstore.py first.")
    sys.exit(1)

print(f"Top match: {results[0][0].metadata.get('source', '?')} "
      f"(distance {results[0][1]:.4f})")
print()

# --- OLD approach: two sequential calls -------------------------------
print("=" * 70)
print("OLD approach: generate_grounded_answer() + generate_action_plan()")
print("=" * 70)
t0 = time.time()
old_answer = llm_engine.generate_grounded_answer(TEST_QUERY, results, category=TEST_CATEGORY)
t1 = time.time()
old_plan = llm_engine.generate_action_plan(TEST_QUERY, TEST_CATEGORY, results)
t2 = time.time()

print(f"\n--- Answer (took {t1 - t0:.1f}s) ---")
print(old_answer)
print(f"\n--- Action plan (took {t2 - t1:.1f}s) ---")
print(old_plan)
print(f"\nTOTAL old approach: {t2 - t0:.1f}s")

# --- NEW approach: one combined call -----------------------------------
print()
print("=" * 70)
print("NEW approach: generate_answer_and_plan() -- single call")
print("=" * 70)
t3 = time.time()
new_answer, new_plan = llm_engine.generate_answer_and_plan(TEST_QUERY, results, category=TEST_CATEGORY)
t4 = time.time()

print(f"\n--- Answer (took {t4 - t3:.1f}s total for BOTH answer + plan) ---")
print(new_answer)
print(f"\n--- Action plan ---")
print(new_plan)
print(f"\nTOTAL new approach: {t4 - t3:.1f}s")

# --- Sanity checks -------------------------------------------------------
print()
print("=" * 70)
print("SANITY CHECKS")
print("=" * 70)
problems = []
if "===ACTION_PLAN===" in new_answer:
    problems.append("!! The delimiter leaked into the visible answer text.")
if not new_plan.strip():
    problems.append("!! The plan came back empty.")
if new_answer.strip() == new_plan.strip():
    problems.append("!! Answer and plan are identical -- parsing likely failed.")

speedup = (t2 - t0) - (t4 - t3)
print(f"Old total: {t2 - t0:.1f}s   New total: {t4 - t3:.1f}s   "
      f"Saved: {speedup:.1f}s ({100 * speedup / (t2 - t0):.0f}% faster)"
      if (t2 - t0) > 0 else "")

if problems:
    print("\nISSUES FOUND:")
    for p in problems:
        print(" ", p)
else:
    print("\nNo issues found -- combined call parsed cleanly.")
