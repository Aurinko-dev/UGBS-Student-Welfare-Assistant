import os
from datetime import datetime

import streamlit as st

import config
import neural_classifier
import risk_classifier

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

st.markdown("## ⚙️ Settings")
st.caption("System status, the indexed knowledge base, and a live classifier test tool — "
           "moved here so the main chat page stays focused on the conversation.")

# --- System status -------------------------------------------------------
st.divider()
st.markdown("#### System status")

llm_ok = config.llm_is_configured()
clf_ok = neural_classifier.is_available()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("LLM provider", config.LLM_PROVIDER)
    if config.LLM_PROVIDER == "ollama":
        st.caption(f"Model: `{config.OLLAMA_MODEL}` @ {config.OLLAMA_HOST}")
    st.caption("Connected" if llm_ok else "Template mode — no API key/local server configured")
with col2:
    st.metric("Classifier", "Trained" if clf_ok else "Fallback")
    if clf_ok and os.path.exists(config.CLASSIFIER_MODEL_PATH):
        trained_at = datetime.fromtimestamp(os.path.getmtime(config.CLASSIFIER_MODEL_PATH))
        st.caption(f"Neural network — last trained {trained_at:%Y-%m-%d %H:%M}")
    else:
        st.caption("Rule-based keywords — run train_classifier.py")
with col3:
    st.metric("Retrieval", "Local")
    st.caption(f"Embedding model: `{config.EMBEDDING_MODEL_NAME}` — no external API calls")

st.caption(f"Retrieval confidence threshold: `0.9` (set in `app.py` — below this, the assistant "
           f"says it doesn't know rather than guessing)")

# --- Privacy notice --------------------------------------------------------
st.warning("⚠️ **Prototype only — not production access control.** No authentication in front of "
           "this app or the Admin Interface. Crisis-flagged messages are redacted at the point of "
           "logging, but other query text is stored in plaintext with no retention policy. See "
           "`report_support_material.md` for the full write-up.")

# --- Knowledge base --------------------------------------------------------
st.divider()
st.markdown("#### Indexed knowledge base")
st.caption(f"{len(config.MARKDOWN_FILES)} source documents currently indexed. Sizes and "
           f"last-modified dates below help spot a source that looks stale or didn't index.")
for f in config.MARKDOWN_FILES:
    if os.path.exists(f):
        size_kb = os.path.getsize(f) / 1024
        modified = datetime.fromtimestamp(os.path.getmtime(f))
        st.markdown(f"- `{f}` — {size_kb:.1f} KB, updated {modified:%Y-%m-%d}")
    else:
        st.markdown(f"- `{f}` — ⚠️ **file not found**")

st.divider()
st.markdown("#### Categories the system routes to")
for c in config.CATEGORIES:
    st.markdown(f"- {c}")

# --- Live classifier test tool ---------------------------------------------
st.divider()
st.markdown("#### Test the classifier")
st.caption("Type a sample question to see exactly how it would be categorized — without going "
           "through the full chat flow. Useful for checking the classifier's behavior directly.")

test_query = st.text_input("Sample question", placeholder="e.g. I can't afford my hostel fees this semester")
if test_query:
    normalized = risk_classifier.normalize_query(test_query)
    if normalized != test_query:
        st.caption(f"Typo-corrected to: *{normalized}*")

    is_crisis = risk_classifier.check_crisis(normalized)
    is_smalltalk = risk_classifier.is_chitchat(normalized)

    if is_crisis:
        st.error("🚨 Would be flagged as a **crisis message** — routed straight to emergency "
                 "referral, bypassing classification and the LLM entirely.")
    elif is_smalltalk:
        st.info("💬 Would be treated as **chit-chat/greeting** — gets a natural reply, not "
                "forced through classification.")
    else:
        result_col1, result_col2 = st.columns(2)
        with result_col1:
            st.markdown("**Neural classifier**")
            if neural_classifier.is_available():
                category, severity, confidence = neural_classifier.classify(normalized)
                st.write(f"Category: **{category}**")
                st.write(f"Severity: **{severity}**")
                st.write(f"Confidence: **{confidence:.0%}**")
            else:
                st.caption("Not trained yet — run train_classifier.py")
        with result_col2:
            st.markdown("**Rule-based fallback**")
            triage = risk_classifier.rule_based_classify(normalized)
            st.write(f"Category: **{triage.category}**")
            st.write(f"Severity: **{triage.severity}**")
            st.write(f"Matched rule: `{triage.matched_rule}`")