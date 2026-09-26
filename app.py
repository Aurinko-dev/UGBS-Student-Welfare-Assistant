"""
Entry point: streamlit run app.py

This file is now only the ROUTER. It sets up the page, the shared styling and
the sidebar, then hands over to whichever page is selected:

    views/user_interface.py        the student chat
    views/admin_interface.py       the analytics dashboard
    views/live_admin_interface.py  the real-time monitor
    views/settings.py              system status + classifier tester
"""

import streamlit as st

import analytics_db
from logo import logo_html
from ui_theme import inject_css, wide

import re

with open("app.py", "r", encoding="utf-8", errors="replace") as f:
    content = f.read()

content = re.sub(r'page_icon="[^"]*"', r'page_icon="\U0001F393"', content)
content = re.sub(r'title="User Interface", icon="[^"]*"', r'title="User Interface", icon="\U0001F4AC"', content)
content = re.sub(r'title="Admin Interface", icon="[^"]*"', r'title="Admin Interface", icon="\U0001F4CA"', content)
content = re.sub(r'title="Live Admin Interface", icon="[^"]*"', r'title="Live Admin Interface", icon="\U0001F534"', content)
content = re.sub(r'title="Settings", icon="[^"]*"', r'title="Settings", icon="\u2699\uFE0F"', content)

with open("app.py", "w", encoding="utf-8", newline="\n") as f:
    f.write(content)

print("Done")
# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="UGBS Student Welfare AI",
    page_icon="\U0001F393",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# INITIALISE SHARED SERVICES
# ============================================================

analytics_db.init_db()
inject_css()


# ============================================================
# APPLICATION PAGES
# ============================================================
#
# IMPORTANT:
# Do NOT type the actual emoji characters into st.Page().
#
# We use Unicode escape sequences instead. Python converts these
# into the correct emoji at runtime.
#
# This prevents:
#
#     💬
#
# from being incorrectly interpreted as:
#
#     ðŸ’¬
#
# on Windows / during deployment.
# ============================================================

ui_page = st.Page(
    "views/user_interface.py",
    title="User Interface",
    icon="\U0001F4AC",
    default=True,
)

admin_page = st.Page(
    "views/admin_interface.py",
    title="Admin Interface",
    icon="\U0001F4CA",
)

live_page = st.Page(
    "views/live_admin_interface.py",
    title="Live Admin Interface",
    icon="\U0001F534",
)

settings_page = st.Page(
    "views/settings.py",
    title="Settings",
    icon="\u2699\uFE0F",
)


# ============================================================
# MAIN NAVIGATION
# ============================================================

# Pages shown in the main navigation block.
# Settings sits separately below a divider.

main_pages = [
    ui_page,
    admin_page,
    live_page,
]


# Newer Streamlit can hide its automatic menu so we control
# the exact order.
#
# Older versions fall back to the built-in menu with named
# sections.

try:
    nav = st.navigation(
        [
            *main_pages,
            settings_page,
        ],
        position="hidden",
    )

    custom_nav = True

except TypeError:
    nav = st.navigation(
        {
            "Student": [
                ui_page,
            ],
            "Administration": [
                admin_page,
                live_page,
            ],
            "System": [
                settings_page,
            ],
        }
    )

    custom_nav = False


# ============================================================
# CLEAR CHAT
# ============================================================

def _clear_chat() -> None:
    """
    Reset the student chat session.
    """

    st.session_state.messages = []
    st.session_state.nationality = None
    st.session_state.awaiting_nationality = False
    st.session_state.pending_query = None
    st.session_state.awaiting_department = False
    st.session_state.active_topic = None
    st.session_state.show_guidance = False


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # 1. Logo — always first
    # --------------------------------------------------------

    st.markdown(
        '<div class="side-brand">'
        + logo_html(52)
        + '<div>'
        + '<div class="name">UGBS Welfare Hub</div>'
        + '<div class="tag">AI Intake &amp; Triage System</div>'
        + '</div>'
        + '</div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # 2. Navigation
    # --------------------------------------------------------

    if custom_nav:

        for page in main_pages:
            st.page_link(page)

        # Push everything below towards the bottom of the sidebar.

        st.markdown(
            '<div style="height:max(24px, calc(100vh - 480px));"></div>',
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # 3. Chat-only action
    # --------------------------------------------------------

    if nav.title == ui_page.title:

        st.button(
            "Clear chat history",
            key="clear_chat",
            on_click=_clear_chat,
            **wide(st.button),
        )

    # --------------------------------------------------------
    # 4. Settings — last
    # --------------------------------------------------------

    if custom_nav:

        st.divider()

        st.page_link(settings_page)


# ============================================================
# RUN SELECTED PAGE
# ============================================================

nav.run()


# ============================================================
# END OF FILE
# ============================================================