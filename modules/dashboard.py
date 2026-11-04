"""Executive Dashboard Module for PIMS
Sekarungi Pharmaceuticals Ltd
High-level operational overview, live KPI metrics, active alerts, and recent transaction feeds.
"""

import streamlit as st
import pandas as pd
from backend.db import fetch_dataframe, test_connection


def render_dashboard():
    # Header Banner
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0f766e 0%, #134e4a 100%); padding: 24px; border-radius: 12px; color: white; margin-bottom: 25px;">
        <h1 style="margin: 0; color: #ffffff; font-size: 2.2rem;">💊 Sekarungi Pharmaceuticals Ltd</h1>
        <p style="margin: 8px 0 0 0; color: #ccfbf1; font-size: 1.05rem;">
            Pharmacy Information Management System (PIMS) — Centralized Operations, Inventory, POS & Regulatory Auditing
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Database connectivity verification
    conn_ok, conn_info = test_connection()
    c_status, c_db, c_user, c_time = st.columns(4)
    with c_status:
        if conn_ok:
            st.success("🟢 Neon PostgreSQL Connected")
        else:
            st.error("🔴 DB Offline")
    with c_db:
        st.info(f"Database: **{conn_info.get('database', 'unknown')}**")
    with c_user:
        st.info(f"User: **{conn_info.get('user', 'unknown')}**")
    with c_time:
        st.info(f"Engine: **{conn_info.get('version', 'PostgreSQL')}**")

    st.write("")

    # Top KPI Metrics Cards
    try:
        df_drugs = fetch_dataframe("SELECT COUNT(*) AS count FROM Drug;")
        df_stock = fetch_dataframe("SELECT COALESCE(SUM(QuantityRemaining), 0) AS units, COUNT(*) AS batches FROM StockBatch;")
        df_sales = fetch_dataframe("SELECT COALESCE(SUM(TotalAmount), 0) AS rev, COUNT(*) AS count FROM Sale;")
        df_expired = fetch_dataframe("SELECT COUNT(*) AS cnt FROM StockBatch WHERE ExpiryDate < CURRENT_DATE AND QuantityRemaining > 0;")
        df_reorder = fetch_dataframe("""
            SELECT COUNT(*) AS cnt FROM Drug d
            LEFT JOIN StockBatch sb ON sb.DrugID = d.DrugID
            GROUP BY d.DrugID, d.ReorderLevel
            HAVING COALESCE(SUM(sb.QuantityRemaining), 0) < d.ReorderLevel;
        """)

        num_drugs = int(df_drugs["count"].iloc[0]) if not df_drugs.empty else 0
        stock_units = int(df_stock["units"].iloc[0]) if not df_stock.empty else 0
        total_rev = float(df_sales["rev"].iloc[0]) if not df_sales.empty else 0.0
        total_sales_tx = int(df_sales["count"].iloc[0]) if not df_sales.empty else 0
        expired_batches = int(df_expired["cnt"].iloc[0]) if not df_expired.empty else 0
        reorder_drugs = len(df_reorder) if not df_reorder.empty else 0

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric("Catalog Pharmaceuticals", f"{num_drugs} Items", "Active Products")
        with k2:
            st.metric("Total Warehouse Stock", f"{stock_units:,} Units", f"{df_stock['batches'].iloc[0]} Batches")
        with k3:
            st.metric("Cumulative Retail Revenue", f"UGX {total_rev:,.0f}", f"{total_sales_tx} Transactions")
        with k4:
            st.metric("Compliance Alerts", f"{expired_batches} Expired", f"{reorder_drugs} Low Stock Items", delta_color="inverse")

    except Exception as e:
        st.warning(f"Could not load KPI aggregates: {e}")

    # Actionable Warning Banners
    if expired_batches > 0:
        st.error(f"⚠️ **Urgent Compliance Warning**: {expired_batches} stock batch(es) have expired and still hold inventory. Open the **SQL Query Explorer** or **Reports** to inspect batches for quarantine.")
    if reorder_drugs > 0:
        st.warning(f"🔔 **Stock Warning**: {reorder_drugs} drug(s) have fallen below their minimum reorder thresholds. Restocking purchase orders recommended.")

    st.markdown("---")

    # Feeds: Recent Sales & Dispensing
    col_sales, col_disp = st.columns(2)

    with col_sales:
        st.subheader("🛒 Recent Sales Activity")
        try:
            sql_recent_sales = """
            SELECT s.ReceiptNumber, s.CustomerName, s.PaymentType, s.TotalAmount, s.SaleDate, u.FullName AS Cashier
            FROM Sale s
            JOIN "User" u ON u.UserID = s.CashierUserID
            ORDER BY s.SaleDate DESC
            LIMIT 5;
            """
            df_rec_sales = fetch_dataframe(sql_recent_sales)
            if not df_rec_sales.empty:
                df_rec_sales["totalamount"] = df_rec_sales["totalamount"].apply(lambda x: f"UGX {float(x):,.0f}")
                df_rec_sales.columns = ["Receipt #", "Customer", "Payment", "Amount", "Timestamp", "Cashier"]
                st.dataframe(df_rec_sales, use_container_width=True)
            else:
                st.info("No sales transactions recorded yet.")
        except Exception as e:
            st.error(f"Error fetching recent sales: {e}")

    with col_disp:
        st.subheader("📋 Recent Dispensing Activity")
        try:
            sql_recent_disp = """
            SELECT s.ReceiptNumber, d.DrugName, si.Quantity, dr.DateDispensed, u.FullName AS Dispenser
            FROM DispensingRegister dr
            JOIN SaleItem si ON si.SaleItemID = dr.SaleItemID
            JOIN Sale s ON s.SaleID = si.SaleID
            JOIN StockBatch sb ON sb.BatchID = si.BatchID
            JOIN Drug d ON d.DrugID = sb.DrugID
            JOIN "User" u ON u.UserID = dr.DispensedByUserID
            ORDER BY dr.DateDispensed DESC
            LIMIT 5;
            """
            df_rec_disp = fetch_dataframe(sql_recent_disp)
            if not df_rec_disp.empty:
                df_rec_disp.columns = ["Receipt #", "Drug Dispensed", "Quantity", "Date Dispensed", "Dispenser"]
                st.dataframe(df_rec_disp, use_container_width=True)
            else:
                st.info("No dispensing events recorded yet.")
        except Exception as e:
            st.error(f"Error fetching dispensing events: {e}")

    st.markdown("---")

    # Recent Purchase Orders & System Architecture
    col_po, col_arch = st.columns([3, 2])

    with col_po:
        st.subheader("📦 Latest Purchase Orders")
        try:
            sql_recent_po = """
            SELECT po.POID, s.CompanyName AS Supplier, po.OrderDate, po.Status,
                   COALESCE(SUM(poi.QuantityOrdered * poi.UnitCost), 0) AS OrderCost
            FROM PurchaseOrder po
            JOIN Supplier s ON s.SupplierID = po.SupplierID
            LEFT JOIN PurchaseOrderItem poi ON poi.POID = po.POID
            GROUP BY po.POID, s.CompanyName, po.OrderDate, po.Status
            ORDER BY po.OrderDate DESC
            LIMIT 5;
            """
            df_rec_po = fetch_dataframe(sql_recent_po)
            if not df_rec_po.empty:
                df_rec_po["ordercost"] = df_rec_po["ordercost"].apply(lambda x: f"UGX {float(x):,.0f}")
                df_rec_po.columns = ["PO ID", "Supplier", "Order Date", "Status", "Total Cost"]
                st.dataframe(df_rec_po, use_container_width=True)
            else:
                st.info("No purchase orders found.")
        except Exception as e:
            st.error(f"Error fetching purchase orders: {e}")

    with col_arch:
        st.subheader("🏛️ Architecture & Course Info")
        st.markdown("""
        - **Institution**: Makerere University
        - **Course**: BCS 2206 Database Management Systems
        - **Case Study**: Sekarungi Pharmaceuticals Ltd
        - **Database**: PostgreSQL 16 (Neon Serverless Cloud)
        - **Driver**: Raw SQL via `psycopg2` (*Strictly No ORM*)
        - **Frontend**: Streamlit + Plotly Visualizations
        - **Relational Integrity**: 11 Normalized Tables (3NF), Foreign Keys, Check Constraints, Views
        """)
