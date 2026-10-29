"""Main Streamlit Application Entrypoint for PIMS
Sekarungi Pharmaceuticals Ltd
Makerere University - BCS 2206 Database Management Systems
"""

import streamlit as st

# Must be the very first Streamlit command
st.set_page_config(
    page_title="Sekarungi PIMS | Pharmacy Management",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Pharmacy Teal/Slate Styling
st.markdown("""
<style>
    /* Global font and subtle styling */
    .main {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Metrics styling */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0f766e;
    }
    
    /* Tab styling */
    button[data-baseweb="tab"] {
        font-weight: 600;
        font-size: 0.95rem;
    }
    
    /* Sidebar branding */
    .sidebar-header {
        background-color: #f0fdfa;
        padding: 14px;
        border-radius: 8px;
        border-left: 4px solid #0d9488;
        margin-bottom: 20px;
    }
    .sidebar-header h2 {
        color: #0f766e;
        margin: 0;
        font-size: 1.25rem;
    }
    .sidebar-header p {
        color: #115e59;
        margin: 4px 0 0 0;
        font-size: 0.85rem;
    }

    /* Table styling */
    div[data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# Core Dashboard & Database Utilities
from modules.dashboard import render_dashboard
from backend.db import test_connection

# Graceful modular imports for teammate deliverables
try:
    from modules.schema_viewer import render_schema_viewer
except ImportError:
    def render_schema_viewer():
        st.subheader("📑 ERD & Data Dictionary")
        st.info("Module under active implementation by **Karen Nakibuuka** (@Kar3n-N) under ticket **PIMS-23 / Issue #27**.")

try:
    from modules.tables_browser import render_tables_browser
except ImportError:
    def render_tables_browser():
        st.subheader("🗃️ Live Database Tables Browser")
        st.info("Module under active implementation by **Karen Nakibuuka** (@Kar3n-N) under ticket **PIMS-23 / Issue #27**.")

try:
    from modules.forms import render_forms
except ImportError:
    def render_forms():
        st.subheader("📝 Data Entry & Point of Sale (POS) Forms")
        st.info("Module under active implementation by **Sabano Zubedah** (@Angel-coder-max) under ticket **PIMS-21 / Issue #26**.")

try:
    from modules.queries_runner import render_queries_runner
except ImportError:
    def render_queries_runner():
        st.subheader("🔍 SQL Query Explorer")
        st.info("Module under active implementation by **Reagan Ankunda** (@reaganankunda4-alt) under ticket **PIMS-25 / Issue #28**.")

try:
    from modules.reports import render_reports
except ImportError:
    def render_reports():
        st.subheader("📊 Graphical Reports & Analytics")
        st.info("Module under active implementation by **Reagan Ankunda** (@reaganankunda4-alt) under ticket **PIMS-25 / Issue #28**.")


def main():
    # Sidebar Header
    st.sidebar.markdown("""
    <div class="sidebar-header">
        <h2>💊 Sekarungi PIMS</h2>
        <p>Pharmaceutical Information Management System</p>
    </div>
    """, unsafe_allow_html=True)

    # Navigation Menu
    nav_choice = st.sidebar.radio(
        "Navigate Application:",
        [
            "🏠 Executive Dashboard",
            "📑 ERD & Data Dictionary",
            "🗃️ Database Tables Browser",
            "📝 Data Entry & POS Forms",
            "🔍 SQL Query Explorer",
            "📊 Graphical Reports & Analytics",
        ],
        index=0
    )

    st.sidebar.markdown("---")

    # System Status in Sidebar
    st.sidebar.markdown("##### 🔌 System Status")
    conn_ok, conn_info = test_connection()
    if conn_ok:
        st.sidebar.success(f"● Neon PostgreSQL (Online)\nDB: `{conn_info.get('database')}`")
    else:
        st.sidebar.error("● Database Offline")

    st.sidebar.markdown("---")
    st.sidebar.caption("""
    **Sekarungi Pharmaceuticals Ltd**  
    Makerere University  
    BCS 2206 Database Systems  
    Pure SQL (No ORM) • Streamlit GUI
    """)

    # Route navigation
    if nav_choice == "🏠 Executive Dashboard":
        render_dashboard()
    elif nav_choice == "📑 ERD & Data Dictionary":
        render_schema_viewer()
    elif nav_choice == "🗃️ Database Tables Browser":
        render_tables_browser()
    elif nav_choice == "📝 Data Entry & POS Forms":
        render_forms()
    elif nav_choice == "🔍 SQL Query Explorer":
        render_queries_runner()
    elif nav_choice == "📊 Graphical Reports & Analytics":
        render_reports()


if __name__ == "__main__":
    main()
