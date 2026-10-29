"""SQL Queries Runner Module for PIMS
Sekarungi Pharmaceuticals Ltd
Interactive execution of course queries (PIMS-6, PIMS-7, PIMS-8, PIMS-9) and custom SQL console.
"""

import time
import streamlit as st
import pandas as pd
from backend.db import fetch_dataframe, get_db_connection


def render_queries_runner():
    st.title("🔍 SQL Query Explorer & Runner")
    st.caption("Execute predefined relational queries across all pharmacy operational areas, or run custom SQL statements.")

    tabs = st.tabs([
        "📦 1. Inventory & Stock (PIMS-6)",
        "🚚 2. Purchasing & Orders (PIMS-7)",
        "💰 3. Sales & Dispensing (PIMS-8)",
        "📊 4. Financial & Payroll (PIMS-9)",
        "💻 5. Custom SQL Console",
    ])

    # -------------------------------------------------------------
    # TAB 1: INVENTORY & STOCK
    # -------------------------------------------------------------
    with tabs[0]:
        st.subheader("Inventory Management Queries")
        st.caption("Tracks stock balances, suppliers, reorder thresholds, expiry dates, and valuations.")

        q1_choice = st.selectbox(
            "Select Inventory Query to Run:",
            [
                "Q1.1: Every Batch with Drug & Supplier Info",
                "Q1.2: Drugs Below Reorder Level (Urgent Restock Needed)",
                "Q1.3: Batches Expiring Soon (FEFO Monitoring)",
                "Q1.4: Expired Batches Still in Stock (Compliance Alert)",
                "Q1.5: Inventory Valuation per Drug Product",
                "Q1.6: Current Stock View (vw_current_stock)",
            ],
            key="q1_choice"
        )

        sql_to_run = ""
        params = None

        if q1_choice.startswith("Q1.1"):
            sql_to_run = """
SELECT sb.BatchID, d.DrugName, s.CompanyName AS Supplier,
       sb.BatchNumber, sb.QuantityRemaining, sb.ExpiryDate
FROM StockBatch sb
JOIN Drug d     ON d.DrugID = sb.DrugID
JOIN Supplier s ON s.SupplierID = sb.SupplierID
ORDER BY sb.ExpiryDate;
            """
        elif q1_choice.startswith("Q1.2"):
            sql_to_run = """
SELECT d.DrugID, d.DrugName, d.ReorderLevel,
       COALESCE(SUM(sb.QuantityRemaining), 0) AS TotalStock
FROM Drug d
LEFT JOIN StockBatch sb ON sb.DrugID = d.DrugID
GROUP BY d.DrugID, d.DrugName, d.ReorderLevel
HAVING COALESCE(SUM(sb.QuantityRemaining), 0) < d.ReorderLevel
ORDER BY TotalStock ASC;
            """
        elif q1_choice.startswith("Q1.3"):
            c1, c2 = st.columns([2, 1])
            with c1:
                days = st.slider("Expiry Window (Days from today):", min_value=15, max_value=365, value=90, step=15)
            sql_to_run = f"""
SELECT d.DrugName, sb.BatchNumber, sb.QuantityRemaining, sb.ExpiryDate,
       (sb.ExpiryDate - CURRENT_DATE) AS DaysLeft
FROM StockBatch sb
JOIN Drug d ON d.DrugID = sb.DrugID
WHERE sb.QuantityRemaining > 0
  AND sb.ExpiryDate BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '{days} days'
ORDER BY sb.ExpiryDate;
            """
        elif q1_choice.startswith("Q1.4"):
            sql_to_run = """
SELECT d.DrugName, sb.BatchNumber, sb.QuantityRemaining, sb.ExpiryDate
FROM StockBatch sb
JOIN Drug d ON d.DrugID = sb.DrugID
WHERE sb.ExpiryDate < CURRENT_DATE AND sb.QuantityRemaining > 0;
            """
        elif q1_choice.startswith("Q1.5"):
            sql_to_run = """
SELECT d.DrugName,
       SUM(sb.QuantityRemaining) AS UnitsInStock,
       SUM(sb.QuantityRemaining * d.UnitPrice) AS StockValue
FROM Drug d
JOIN StockBatch sb ON sb.DrugID = d.DrugID
GROUP BY d.DrugID, d.DrugName
ORDER BY StockValue DESC;
            """
        elif q1_choice.startswith("Q1.6"):
            sql_to_run = "SELECT * FROM vw_current_stock ORDER BY TotalStock ASC;"

        _execute_and_display(sql_to_run, key_prefix="inv")

    # -------------------------------------------------------------
    # TAB 2: PURCHASING & ORDERS
    # -------------------------------------------------------------
    with tabs[1]:
        st.subheader("Purchasing & Supplier Queries")
        st.caption("Monitors purchase orders, costs, vendor spend, and uncataloged supplier items.")

        q2_choice = st.selectbox(
            "Select Purchasing Query to Run:",
            [
                "Q2.1: Pending Purchase Orders with Supplier & Requester",
                "Q2.2: Total Cost per Purchase Order (with Status Filter)",
                "Q2.3: Top Suppliers by Total Spend (Received Orders)",
                "Q2.4: Catalog Drugs Never Ordered",
                "Q2.5: Average and Peak Unit Purchase Cost per Drug",
                "Q2.6: Purchase Order Summary View (vw_purchase_order_summary)",
            ],
            key="q2_choice"
        )

        sql_to_run = ""

        if q2_choice.startswith("Q2.1"):
            sql_to_run = """
SELECT po.POID, s.CompanyName AS Supplier, u.FullName AS CreatedBy, po.OrderDate
FROM PurchaseOrder po
JOIN Supplier s ON s.SupplierID = po.SupplierID
JOIN "User" u   ON u.UserID = po.CreatedByUserID
WHERE po.Status = 'Pending'
ORDER BY po.OrderDate;
            """
        elif q2_choice.startswith("Q2.2"):
            status_filter = st.selectbox("Filter PO Status:", ["All", "Pending", "Received", "Cancelled"], index=0)
            where_clause = "" if status_filter == "All" else f"WHERE po.Status = '{status_filter}'"
            sql_to_run = f"""
SELECT po.POID, s.CompanyName AS Supplier, po.Status,
       COALESCE(SUM(poi.QuantityOrdered * poi.UnitCost), 0) AS OrderTotal
FROM PurchaseOrder po
JOIN Supplier s          ON s.SupplierID = po.SupplierID
LEFT JOIN PurchaseOrderItem poi ON poi.POID = po.POID
{where_clause}
GROUP BY po.POID, s.CompanyName, po.Status
ORDER BY OrderTotal DESC;
            """
        elif q2_choice.startswith("Q2.3"):
            limit_n = st.slider("Number of Top Suppliers to Show:", min_value=3, max_value=10, value=5)
            sql_to_run = f"""
SELECT s.SupplierID, s.CompanyName,
       COUNT(DISTINCT po.POID) AS OrdersCount,
       COALESCE(SUM(poi.QuantityOrdered * poi.UnitCost), 0) AS TotalSpent
FROM Supplier s
JOIN PurchaseOrder po      ON po.SupplierID = s.SupplierID
JOIN PurchaseOrderItem poi ON poi.POID = po.POID
WHERE po.Status = 'Received'
GROUP BY s.SupplierID, s.CompanyName
ORDER BY TotalSpent DESC
LIMIT {limit_n};
            """
        elif q2_choice.startswith("Q2.4"):
            sql_to_run = """
SELECT d.DrugID, d.DrugName
FROM Drug d
LEFT JOIN PurchaseOrderItem poi ON poi.DrugID = d.DrugID
WHERE poi.POItemID IS NULL;
            """
        elif q2_choice.startswith("Q2.5"):
            sql_to_run = """
SELECT d.DrugID, d.DrugName,
       ROUND(AVG(poi.UnitCost), 2) AS AvgUnitCost,
       MAX(poi.UnitCost) AS HighestUnitCost
FROM Drug d
JOIN PurchaseOrderItem poi ON poi.DrugID = d.DrugID
GROUP BY d.DrugID, d.DrugName
ORDER BY AvgUnitCost DESC;
            """
        elif q2_choice.startswith("Q2.6"):
            sql_to_run = "SELECT * FROM vw_purchase_order_summary ORDER BY OrderDate DESC;"

        _execute_and_display(sql_to_run, key_prefix="pur")

    # -------------------------------------------------------------
    # TAB 3: SALES & DISPENSING
    # -------------------------------------------------------------
    with tabs[2]:
        st.subheader("Sales & Dispensing Queries")
        st.caption("Analyzes sales revenue, payment channels, cashier activity, and prescription dispensing compliance.")

        q3_choice = st.selectbox(
            "Select Sales/Dispensing Query to Run:",
            [
                "Q3.1: Daily Revenue & Sales Volume",
                "Q3.2: Best-Selling Drugs by Units Sold",
                "Q3.3: Cashier Sales Performance",
                "Q3.4: Payment Type Revenue & 18% VAT Breakdown",
                "Q3.5: Regulatory Compliance: Sold Items Not Yet Dispensed",
                "Q3.6: Dispensing Register Audit Log",
                "Q3.7: Sales Detail View (vw_sales_detail)",
            ],
            key="q3_choice"
        )

        sql_to_run = ""

        if q3_choice.startswith("Q3.1"):
            sql_to_run = """
SELECT DATE(SaleDate) AS SaleDay,
       COUNT(*) AS NumberOfSales,
       SUM(TotalAmount) AS Revenue
FROM Sale
GROUP BY DATE(SaleDate)
ORDER BY SaleDay DESC;
            """
        elif q3_choice.startswith("Q3.2"):
            top_drugs = st.slider("Show Top N Drugs:", min_value=3, max_value=20, value=10)
            sql_to_run = f"""
SELECT d.DrugName,
       SUM(si.Quantity) AS UnitsSold,
       SUM(si.LineTotal) AS Revenue
FROM SaleItem si
JOIN StockBatch sb ON sb.BatchID = si.BatchID
JOIN Drug d        ON d.DrugID = sb.DrugID
GROUP BY d.DrugID, d.DrugName
ORDER BY UnitsSold DESC
LIMIT {top_drugs};
            """
        elif q3_choice.startswith("Q3.3"):
            sql_to_run = """
SELECT u.FullName AS Cashier,
       COUNT(s.SaleID) AS Sales,
       SUM(s.TotalAmount) AS TotalSold
FROM "User" u
JOIN Sale s ON s.CashierUserID = u.UserID
GROUP BY u.UserID, u.FullName
ORDER BY TotalSold DESC;
            """
        elif q3_choice.startswith("Q3.4"):
            sql_to_run = """
SELECT PaymentType,
       COUNT(*) AS Transactions,
       SUM(VATAmount) AS TotalVAT,
       SUM(TotalAmount) AS TotalRevenue
FROM Sale
GROUP BY PaymentType;
            """
        elif q3_choice.startswith("Q3.5"):
            sql_to_run = """
SELECT s.ReceiptNumber, d.DrugName, si.Quantity
FROM SaleItem si
JOIN Sale s        ON s.SaleID = si.SaleID
JOIN StockBatch sb ON sb.BatchID = si.BatchID
JOIN Drug d        ON d.DrugID = sb.DrugID
LEFT JOIN DispensingRegister dr ON dr.SaleItemID = si.SaleItemID
WHERE dr.RegisterID IS NULL;
            """
        elif q3_choice.startswith("Q3.6"):
            sql_to_run = """
SELECT dr.DateDispensed, d.DrugName, si.Quantity,
       u.FullName AS DispensedBy, dr.PrescriptionRef
FROM DispensingRegister dr
JOIN SaleItem si   ON si.SaleItemID = dr.SaleItemID
JOIN StockBatch sb ON sb.BatchID = si.BatchID
JOIN Drug d        ON d.DrugID = sb.DrugID
JOIN "User" u      ON u.UserID = dr.DispensedByUserID
ORDER BY dr.DateDispensed DESC;
            """
        elif q3_choice.startswith("Q3.7"):
            sql_to_run = "SELECT * FROM vw_sales_detail ORDER BY SaleDate DESC;"

        _execute_and_display(sql_to_run, key_prefix="sales")

    # -------------------------------------------------------------
    # TAB 4: FINANCIAL & PAYROLL
    # -------------------------------------------------------------
    with tabs[3]:
        st.subheader("Financial & Payroll Queries")
        st.caption("P&L statements, operational expenses, staff payroll disbursements, and audit logs.")

        q4_choice = st.selectbox(
            "Select Financial Query to Run:",
            [
                "Q4.1: Monthly Operational Expenses by Category",
                "Q4.2: Staff Payroll Summary by Payment Type",
                "Q4.3: High-Cost Expense Categories (Threshold Filter)",
                "Q4.4: Finance Audit: Entries Recorded per Staff Member",
                "Q4.5: Monthly Profit & Loss Statement (Revenue - Expenses - Payroll)",
                "Q4.6: Monthly Financial Summary View (vw_monthly_financial_summary)",
            ],
            key="q4_choice"
        )

        sql_to_run = ""

        if q4_choice.startswith("Q4.1"):
            sql_to_run = """
SELECT DATE_TRUNC('month', ExpenseDate) AS Month,
       Category,
       SUM(Amount) AS TotalExpense
FROM Expense
GROUP BY DATE_TRUNC('month', ExpenseDate), Category
ORDER BY Month DESC, TotalExpense DESC;
            """
        elif q4_choice.startswith("Q4.2"):
            sql_to_run = """
SELECT u.FullName, p.PaymentType, SUM(p.Amount) AS TotalPaid
FROM Payroll p
JOIN "User" u ON u.UserID = p.StaffUserID
GROUP BY u.UserID, u.FullName, p.PaymentType
ORDER BY u.FullName, p.PaymentType;
            """
        elif q4_choice.startswith("Q4.3"):
            min_expense = st.number_input("Minimum Category Spend (UGX):", min_value=100000, max_value=5000000, value=500000, step=100000)
            sql_to_run = f"""
SELECT Category, SUM(Amount) AS TotalExpense
FROM Expense
GROUP BY Category
HAVING SUM(Amount) > {min_expense}
ORDER BY TotalExpense DESC;
            """
        elif q4_choice.startswith("Q4.4"):
            sql_to_run = """
SELECT u.FullName,
       (SELECT COUNT(*) FROM Expense e WHERE e.RecordedByUserID = u.UserID) AS ExpensesRecorded,
       (SELECT COUNT(*) FROM Payroll p WHERE p.RecordedByUserID = u.UserID) AS PayrollRecorded
FROM "User" u
ORDER BY ExpensesRecorded + PayrollRecorded DESC;
            """
        elif q4_choice.startswith("Q4.5"):
            sql_to_run = """
WITH revenue AS (
    SELECT DATE_TRUNC('month', SaleDate) AS Month, SUM(TotalAmount) AS Revenue
    FROM Sale GROUP BY 1
), expenses AS (
    SELECT DATE_TRUNC('month', ExpenseDate) AS Month, SUM(Amount) AS Expenses
    FROM Expense GROUP BY 1
), payroll AS (
    SELECT DATE_TRUNC('month', PaymentDate) AS Month, SUM(Amount) AS Payroll
    FROM Payroll GROUP BY 1
)
SELECT COALESCE(r.Month, e.Month, p.Month) AS Month,
       COALESCE(r.Revenue, 0)  AS Revenue,
       COALESCE(e.Expenses, 0) AS Expenses,
       COALESCE(p.Payroll, 0)  AS Payroll,
       COALESCE(r.Revenue, 0) - COALESCE(e.Expenses, 0) - COALESCE(p.Payroll, 0) AS Profit
FROM revenue r
FULL OUTER JOIN expenses e ON e.Month = r.Month
FULL OUTER JOIN payroll p  ON p.Month = COALESCE(r.Month, e.Month)
ORDER BY Month DESC;
            """
        elif q4_choice.startswith("Q4.6"):
            sql_to_run = "SELECT * FROM vw_monthly_financial_summary ORDER BY Month DESC;"

        _execute_and_display(sql_to_run, key_prefix="fin")

    # -------------------------------------------------------------
    # TAB 5: CUSTOM SQL CONSOLE
    # -------------------------------------------------------------
    with tabs[4]:
        st.subheader("Interactive Custom SQL Console")
        st.caption("Write and execute custom SELECT queries against the Neon database.")

        sample_sql = "SELECT d.DrugName, d.Category, d.UnitPrice, sb.BatchNumber, sb.QuantityRemaining, sb.ExpiryDate\nFROM Drug d\nJOIN StockBatch sb ON sb.DrugID = d.DrugID\nWHERE sb.QuantityRemaining > 0\nORDER BY sb.ExpiryDate ASC\nLIMIT 15;"

        user_sql = st.text_area("SQL Query to Execute:", value=sample_sql, height=140)

        col_run, col_clear = st.columns([1, 4])
        with col_run:
            run_custom = st.button("▶️ Execute SQL", type="primary")

        if run_custom:
            if not user_sql.strip():
                st.warning("Please enter a SQL query.")
            else:
                _execute_and_display(user_sql, key_prefix="custom")


def _execute_and_display(sql_statement: str, key_prefix: str = "query"):
    """Helper to run SQL, measure latency, display results, show SQL code and download CSV."""
    sql_clean = sql_statement.strip()
    
    with st.expander("📄 View Raw SQL Query", expanded=False):
        st.code(sql_clean, language="sql")

    start_time = time.time()
    try:
        df = fetch_dataframe(sql_clean)
        elapsed = (time.time() - start_time) * 1000

        col_count, col_time = st.columns([1, 1])
        with col_count:
            st.metric("Rows Returned", len(df))
        with col_time:
            st.metric("Execution Latency", f"{elapsed:.1f} ms")

        if df.empty:
            st.info("Query executed successfully, but returned 0 rows.")
        else:
            # Format currency / numerical columns if appropriate
            st.dataframe(df, use_container_width=True)

            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Result as CSV",
                data=csv_data,
                file_name=f"{key_prefix}_result.csv",
                mime="text/csv",
                key=f"dl_{key_prefix}_{hash(sql_statement)}"
            )

    except Exception as e:
        st.error(f"❌ SQL Execution Error: {e}")
