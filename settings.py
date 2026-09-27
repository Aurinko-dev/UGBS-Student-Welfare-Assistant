import os
from datetime import datetime

import streamlit as st

import config
import llm_engine
import neural_classifier
import risk_classifier

st.markdown("## ⚙️ Settings")
st.caption("System status, the indexed knowledge base, and a live classifier test tool — "
           "kept here so the User Interface page stays focused on the conversation.")

# --- Generation & decision tuning -------------------------------------------
# Session-only knobs (see caption below) for exploring how generation
# creativity and the two confidence cutoffs affect behavior, without
# editing code or restarting the app. This is a demo/exploration aid, not a
# way to permanently retune the app -- a real change to, say, the retrieval
# cutoff still belongs in code, backed by evidence the way the current
# default was (see check_retrieval_scores.py and the comment in
# views/user_interface.py explaining why it's 1.0).
#
# The two cutoff defaults below are duplicated from views/user_interface.py
# rather than imported from it, because that file is a Streamlit *page*
# (it has top-level st.* calls that would render on import) -- config.py or
# llm_engine.py would be the place to unify these if they ever need to be
# imported from more than one page.
_DEFAULT_RETRIEVAL_CUTOFF = 1.0   # must match views/user_interface.py
_DEFAULT_CLASSIFIER_CUTOFF = 0.4  # must match views/user_interface.py

st.divider()
st.markdown("#### Generation & decision tuning")
st.caption("Adjust how the AI generates answers and where it draws the line between "
           "'confident enough to answer' and 'should ask for help instead.'")

for _key, _default in (
    ("tune_temperature", llm_engine.DEFAULT_TEMPERATURE),
    ("tune_max_tokens", llm_engine.DEFAULT_MAX_TOKENS),
    ("tune_classifier_cutoff", _DEFAULT_CLASSIFIER_CUTOFF),
    ("tune_retrieval_cutoff", _DEFAULT_RETRIEVAL_CUTOFF),
):
    if _key not in st.session_state:
        st.session_state[_key] = _default

tcol1, tcol2 = st.columns(2)
with tcol1:
    st.session_state.tune_temperature = st.slider(
        "Temperature", 0.0, 1.0, st.session_state.tune_temperature, 0.05,
        help="Higher = more varied/creative wording in generated answers. "
             "Lower = more literal and repeatable.")
    st.session_state.tune_classifier_cutoff = st.slider(
        "Classifier confidence cutoff", 0.0, 1.0, st.session_state.tune_classifier_cutoff, 0.05,
        help="Below this confidence, the neural classifier's prediction is discarded and "
             "the question falls back to the LLM classifier instead.")
with tcol2:
    st.session_state.tune_max_tokens = st.slider(
        "Max response length (tokens)", 100, 1000, st.session_state.tune_max_tokens, 50,
        help="Caps how long a generated answer or action plan can run.")
    st.session_state.tune_retrieval_cutoff = st.slider(
        "Retrieval confidence cutoff (distance)", 0.0, 2.0, st.session_state.tune_retrieval_cutoff, 0.05,
        help="Above this vector-similarity distance, the assistant says it doesn't know "
             "instead of guessing. Default of 1.0 was chosen empirically -- see "
             "check_retrieval_scores.py and the comment in views/user_interface.py.")

if st.button("↺ Reset to defaults"):
    st.session_state.tune_temperature = llm_engine.DEFAULT_TEMPERATURE
    st.session_state.tune_max_tokens = llm_engine.DEFAULT_MAX_TOKENS
    st.session_state.tune_classifier_cutoff = _DEFAULT_CLASSIFIER_CUTOFF
    st.session_state.tune_retrieval_cutoff = _DEFAULT_RETRIEVAL_CUTOFF
    st.rerun()

st.caption("These settings live only in this browser session — they reset to the defaults "
           "above when the app restarts.")

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

st.caption(f"Retrieval confidence threshold: `{st.session_state.tune_retrieval_cutoff:.2f}` "
           f"(adjustable above — above this distance, the assistant says it doesn't know "
           f"rather than guessing)")

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
        net_result = None
        with result_col1:
            st.markdown("**Neural classifier**")
            if neural_classifier.is_available():
                category, severity, confidence, p_high = neural_classifier.classify_full(normalized)
                net_result = (category, severity, confidence, p_high)
                st.write(f"Category: **{category}**")
                st.write(f"Severity: **{severity}**")
                st.write(f"Confidence: **{confidence:.0%}**")
                if p_high is not None:
                    st.write(f"P(High severity): **{p_high:.0%}**")
            else:
                st.caption("Not trained yet — run train_classifier.py")
        with result_col2:
            st.markdown("**Rule-based fallback**")
            triage = risk_classifier.rule_based_classify(normalized)
            st.write(f"Category: **{triage.category}**")
            st.write(f"Severity: **{triage.severity}**")
            st.write(f"Matched rule: `{triage.matched_rule}`")

        # What the live app would actually do: net (or rules) + safety net +
        # urgency floor + escalation policy.
        st.markdown("**Final decision (after safety net, urgency floor and escalation policy)**")
        if net_result is not None:
            base_cat, base_sev, base_conf, base_ph = net_result
        else:
            base_cat, base_sev, base_conf, base_ph = triage.category, triage.severity, None, None
        f_cat, f_sev, f_esc, f_reason, f_note = risk_classifier.finalize_triage(
            normalized, base_cat, base_sev, base_conf, base_ph)
        st.write(f"Category: **{f_cat}**  ·  Severity: **{f_sev}**  ·  "
                 f"Escalated: **{'YES — ' + f_reason if f_esc else 'no'}**")
        if f_note:
            st.caption(f"Adjustments applied: {f_note}")
