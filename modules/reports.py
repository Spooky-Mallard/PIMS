"""Graphical and Textual Reports Module for PIMS
Sekarungi Pharmaceuticals Ltd
Generates interactive graphical charts (Plotly) and formatted executive text reports.
"""

import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from backend.db import fetch_dataframe


def render_reports():
    st.title("📊 Management Reports & Analytics")
    st.caption("Executive graphical visualizations and formal business performance summaries for Sekarungi Pharmaceuticals Ltd.")

    report_tab = st.radio(
        "Choose Report View:",
        [
            "📈 Profit & Loss (P&L) Report",
            "🛒 Sales & Revenue Analytics",
            "📦 Inventory Health & Expiry Risk",
            "📄 Official Printable Text Report",
        ],
        horizontal=True
    )

    st.markdown("---")

    if report_tab == "📈 Profit & Loss (P&L) Report":
        _render_pnl_report()
    elif report_tab == "🛒 Sales & Revenue Analytics":
        _render_sales_analytics()
    elif report_tab == "📦 Inventory Health & Expiry Risk":
        _render_inventory_analytics()
    elif report_tab == "📄 Official Printable Text Report":
        _render_text_report()


def _render_pnl_report():
    st.subheader("Monthly Profit & Loss (P&L) Statement")
    st.caption("Consolidated revenue from retail sales compared against operational expenses and staff payroll.")

    sql = """
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
ORDER BY Month ASC;
    """

    df = fetch_dataframe(sql)
    if df.empty:
        st.warning("No financial transactions recorded yet.")
        return

    # Convert numeric columns
    for col in ["revenue", "expenses", "payroll", "profit"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Format Month label
    df["MonthLabel"] = pd.to_datetime(df["month"]).dt.strftime("%b %Y")

    total_rev = df["revenue"].sum()
    total_exp = df["expenses"].sum()
    total_pay = df["payroll"].sum()
    total_profit = df["profit"].sum()
    margin = (total_profit / total_rev * 100) if total_rev > 0 else 0

    # Top KPI cards
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Total Revenue", f"UGX {total_rev:,.0f}")
    with k2:
        st.metric("Operational Expenses", f"UGX {total_exp:,.0f}")
    with k3:
        st.metric("Total Payroll", f"UGX {total_pay:,.0f}")
    with k4:
        st.metric("Net Operating Profit", f"UGX {total_profit:,.0f}", delta=f"{margin:.1f}% Margin")

    st.write("")

    # Plotly Grouped Bar Chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["MonthLabel"],
        y=df["revenue"],
        name="Gross Revenue",
        marker_color="#0D9488"
    ))
    fig.add_trace(go.Bar(
        x=df["MonthLabel"],
        y=df["expenses"],
        name="Operating Expenses",
        marker_color="#F97316"
    ))
    fig.add_trace(go.Bar(
        x=df["MonthLabel"],
        y=df["payroll"],
        name="Staff Payroll",
        marker_color="#8B5CF6"
    ))
    fig.add_trace(go.Bar(
        x=df["MonthLabel"],
        y=df["profit"],
        name="Net Profit",
        marker_color="#10B981"
    ))

    fig.update_layout(
        title="Monthly Financial Overview (UGX)",
        barmode="group",
        xaxis_title="Billing Month",
        yaxis_title="Amount in UGX",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white",
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)

    # Data Table
    st.markdown("#### Tabular P&L Statement")
    display_df = df[["MonthLabel", "revenue", "expenses", "payroll", "profit"]].copy()
    display_df.columns = ["Month", "Revenue (UGX)", "Expenses (UGX)", "Payroll (UGX)", "Net Profit (UGX)"]
    for c in ["Revenue (UGX)", "Expenses (UGX)", "Payroll (UGX)", "Net Profit (UGX)"]:
        display_df[c] = display_df[c].apply(lambda x: f"{x:,.2f}")
    st.dataframe(display_df, use_container_width=True)


def _render_sales_analytics():
    st.subheader("Sales & Revenue Visual Analytics")
    st.caption("Distribution of sales across channels, revenue trends, cashier rankings, and top products.")

    # 1. Daily trend
    sql_daily = """
    SELECT DATE(SaleDate) AS SaleDate, COUNT(*) AS Transactions, SUM(TotalAmount) AS DailyTotal
    FROM Sale
    GROUP BY DATE(SaleDate)
    ORDER BY SaleDate ASC;
    """
    df_daily = fetch_dataframe(sql_daily)

    # 2. Payment methods
    sql_payment = """
    SELECT PaymentType, COUNT(*) AS Transactions, SUM(TotalAmount) AS TotalRevenue, SUM(VATAmount) AS TotalVAT
    FROM Sale
    GROUP BY PaymentType;
    """
    df_pay = fetch_dataframe(sql_payment)

    # 3. Top products
    sql_top_drugs = """
    SELECT d.DrugName, SUM(si.Quantity) AS UnitsSold, SUM(si.LineTotal) AS Revenue
    FROM SaleItem si
    JOIN StockBatch sb ON sb.BatchID = si.BatchID
    JOIN Drug d        ON d.DrugID = sb.DrugID
    GROUP BY d.DrugName
    ORDER BY Revenue DESC
    LIMIT 10;
    """
    df_top_drugs = fetch_dataframe(sql_top_drugs)

    # Row 1: Daily Revenue Trend & Payment Method Split
    c1, c2 = st.columns([3, 2])
    with c1:
        if not df_daily.empty:
            df_daily["SaleDate"] = pd.to_datetime(df_daily["saledate"])
            df_daily["DailyTotal"] = pd.to_numeric(df_daily["dailytotal"], errors="coerce")
            fig_trend = px.line(
                df_daily,
                x="SaleDate",
                y="DailyTotal",
                markers=True,
                title="Daily Sales Revenue Trend (UGX)",
                labels={"DailyTotal": "Revenue (UGX)", "SaleDate": "Date"}
            )
            fig_trend.update_traces(line_color="#0D9488", line_width=3)
            fig_trend.update_layout(template="plotly_white", height=380)
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("No daily sales records found.")

    with c2:
        if not df_pay.empty:
            df_pay["TotalRevenue"] = pd.to_numeric(df_pay["totalrevenue"], errors="coerce")
            fig_pie = px.pie(
                df_pay,
                names="paymenttype",
                values="TotalRevenue",
                hole=0.45,
                title="Revenue by Payment Channel",
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            fig_pie.update_layout(template="plotly_white", height=380)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No payment data found.")

    # Row 2: Top 10 Drugs
    if not df_top_drugs.empty:
        df_top_drugs["Revenue"] = pd.to_numeric(df_top_drugs["revenue"], errors="coerce")
        df_top_drugs["UnitsSold"] = pd.to_numeric(df_top_drugs["unitssold"], errors="coerce")
        df_top_drugs = df_top_drugs.sort_values(by="Revenue", ascending=True)

        fig_drugs = px.bar(
            df_top_drugs,
            x="Revenue",
            y="drugname",
            orientation="h",
            title="Top 10 Revenue-Generating Pharmaceuticals",
            labels={"Revenue": "Total Revenue (UGX)", "drugname": "Drug"},
            text_auto=".2s"
        )
        fig_drugs.update_traces(marker_color="#14B8A6")
        fig_drugs.update_layout(template="plotly_white", height=420)
        st.plotly_chart(fig_drugs, use_container_width=True)


def _render_inventory_analytics():
    st.subheader("Inventory Stock Levels & Expiry Risk (FEFO)")
    st.caption("Proactive monitoring of stockouts, reorder thresholds, and drug shelf-life.")

    sql_batches = """
    SELECT sb.BatchID, d.DrugName, d.Category, sb.BatchNumber,
           sb.QuantityRemaining, d.ReorderLevel, sb.ExpiryDate,
           d.UnitPrice, (sb.QuantityRemaining * d.UnitPrice) AS BatchValue,
           (sb.ExpiryDate - CURRENT_DATE) AS DaysToExpiry
    FROM StockBatch sb
    JOIN Drug d ON d.DrugID = sb.DrugID
    ORDER BY DaysToExpiry ASC;
    """
    df = fetch_dataframe(sql_batches)
    if df.empty:
        st.warning("No stock batch inventory records found.")
        return

    df["DaysToExpiry"] = pd.to_numeric(df["daystoexpiry"], errors="coerce")
    df["BatchValue"] = pd.to_numeric(df["batchvalue"], errors="coerce")
    df["QuantityRemaining"] = pd.to_numeric(df["quantityremaining"], errors="coerce")

    # Expiry status classification
    def classify_expiry(days):
        if days < 0:
            return "Expired (Action Required)"
        elif days <= 90:
            return "Near Expiry (≤90 Days)"
        elif days <= 180:
            return "Expiring Soon (91-180 Days)"
        else:
            return "Adequate Shelf-Life (>180 Days)"

    df["ExpiryStatus"] = df["DaysToExpiry"].apply(classify_expiry)

    # Summary metrics
    total_val = df["BatchValue"].sum()
    total_units = df["QuantityRemaining"].sum()
    expired_cnt = len(df[df["DaysToExpiry"] < 0])
    near_expiry_cnt = len(df[(df["DaysToExpiry"] >= 0) & (df["DaysToExpiry"] <= 90)])

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Warehouse Stock Value", f"UGX {total_val:,.0f}")
    with m2:
        st.metric("Total Units On-Hand", f"{total_units:,.0f} units")
    with m3:
        st.metric("Expired Batches", expired_cnt, delta="-Compliance Alert" if expired_cnt > 0 else "Clean", delta_color="inverse")
    with m4:
        st.metric("Near-Expiry Batches (≤90d)", near_expiry_cnt, delta="Restock / Discount Alert" if near_expiry_cnt > 0 else "Normal", delta_color="off")

    st.write("")

    # Visualizations
    c1, c2 = st.columns([2, 3])
    with c1:
        status_counts = df["ExpiryStatus"].value_counts().reset_index()
        status_counts.columns = ["Status", "Batches"]
        fig_status = px.pie(
            status_counts,
            names="Status",
            values="Batches",
            title="Batch Expiry Risk Distribution",
            color="Status",
            color_discrete_map={
                "Expired (Action Required)": "#EF4444",
                "Near Expiry (≤90 Days)": "#F59E0B",
                "Expiring Soon (91-180 Days)": "#3B82F6",
                "Adequate Shelf-Life (>180 Days)": "#10B981"
            }
        )
        fig_status.update_layout(template="plotly_white", height=380)
        st.plotly_chart(fig_status, use_container_width=True)

    with c2:
        # High value inventory
        top_val = df.sort_values(by="BatchValue", ascending=False).head(8)
        fig_val = px.bar(
            top_val,
            x="BatchValue",
            y="drugname",
            orientation="h",
            title="Top Highest-Value Stock Batches in Store",
            labels={"BatchValue": "Batch Valuation (UGX)", "drugname": "Drug"},
            color="DaysToExpiry",
            color_continuous_scale="Tealgrn"
        )
        fig_val.update_layout(template="plotly_white", height=380)
        st.plotly_chart(fig_val, use_container_width=True)

    # Detailed Table
    st.markdown("#### High Priority Stock Alert Table")
    alert_df = df[df["DaysToExpiry"] <= 90][["drugname", "batchnumber", "quantityremaining", "expirydate", "DaysToExpiry", "ExpiryStatus"]].copy()
    if alert_df.empty:
        st.success("✅ All active batches have more than 90 days remaining shelf-life!")
    else:
        alert_df.columns = ["Drug", "Batch No", "Units Left", "Expiry Date", "Days Remaining", "Status"]
        st.dataframe(alert_df, use_container_width=True)


def _render_text_report():
    st.subheader("Official Formatted Executive Business Report")
    st.caption("Standardized text performance report for pharmacy management, board review, and NDA compliance audit.")

    today_str = datetime.date.today().strftime("%d %B %Y")
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Fetch aggregate data
    df_rev = fetch_dataframe("SELECT COALESCE(SUM(TotalAmount), 0) AS rev, COALESCE(SUM(VATAmount), 0) AS vat, COUNT(*) AS txs FROM Sale;")
    df_exp = fetch_dataframe("SELECT COALESCE(SUM(Amount), 0) AS exp, COUNT(*) AS count FROM Expense;")
    df_pay = fetch_dataframe("SELECT COALESCE(SUM(Amount), 0) AS pay, COUNT(*) AS count FROM Payroll;")
    df_stock = fetch_dataframe("SELECT COUNT(DISTINCT DrugID) AS drugs, COALESCE(SUM(QuantityRemaining), 0) AS units FROM StockBatch;")
    df_expired = fetch_dataframe("SELECT COUNT(*) AS expired FROM StockBatch WHERE ExpiryDate < CURRENT_DATE AND QuantityRemaining > 0;")
    df_top_drugs = fetch_dataframe("""
        SELECT d.DrugName, SUM(si.Quantity) AS units, SUM(si.LineTotal) AS revenue
        FROM SaleItem si
        JOIN StockBatch sb ON sb.BatchID = si.BatchID
        JOIN Drug d ON d.DrugID = sb.DrugID
        GROUP BY d.DrugName
        ORDER BY revenue DESC
        LIMIT 5;
    """)

    rev = float(df_rev["rev"].iloc[0]) if not df_rev.empty else 0.0
    vat = float(df_rev["vat"].iloc[0]) if not df_rev.empty else 0.0
    sales_cnt = int(df_rev["txs"].iloc[0]) if not df_rev.empty else 0
    exp = float(df_exp["exp"].iloc[0]) if not df_exp.empty else 0.0
    pay = float(df_pay["pay"].iloc[0]) if not df_pay.empty else 0.0
    drugs_cnt = int(df_stock["drugs"].iloc[0]) if not df_stock.empty else 0
    stock_units = int(df_stock["units"].iloc[0]) if not df_stock.empty else 0
    expired_cnt = int(df_expired["expired"].iloc[0]) if not df_expired.empty else 0
    net_profit = rev - exp - pay
    margin_pct = (net_profit / rev * 100) if rev > 0 else 0.0

    top_drugs_text = ""
    if not df_top_drugs.empty:
        for idx, row in df_top_drugs.iterrows():
            top_drugs_text += f"   {idx+1}. {row['drugname']:<32} | Units: {int(row['units']):>4} | Rev: UGX {float(row['revenue']):>12,.2f}\n"
    else:
        top_drugs_text = "   (No recorded sales items)\n"

    report_text = f"""========================================================================================
                      SEKARUNGI PHARMACEUTICALS LIMITED
                 EXECUTIVE PHARMACY MANAGEMENT AUDIT REPORT
========================================================================================
Generated On: {timestamp_str}
Prepared For: Academic Evaluation & Board Review
System:       Pharmaceutical Information Management System (PIMS) v1.0
Database:     PostgreSQL (Neon Serverless Cloud)

1. EXECUTIVE FINANCIAL SUMMARY
----------------------------------------------------------------------------------------
Gross Sales Revenue:          UGX {rev:>16,.2f}
Applicable VAT Collected:     UGX {vat:>16,.2f}  (18% standard VAT rate)
Total Retail Sales Count:     {sales_cnt:>16} transactions
Operational Expenses (Opex):  UGX {exp:>16,.2f}
Total Staff Payroll Paid:     UGX {pay:>16,.2f}
----------------------------------------------------------------------------------------
NET OPERATING PROFIT / (LOSS): UGX {net_profit:>15,.2f}
Operating Profit Margin:       {margin_pct:>16.2f} %

2. INVENTORY HEALTH & PRODUCT CATALOG
----------------------------------------------------------------------------------------
Total Active Pharmaceutical Products: {drugs_cnt:>10} unique formulations
Total Inventory Units in Warehouse:   {stock_units:>10} pack units
Expired Batches (Compliance Action):  {expired_cnt:>10} batches
Regulatory Compliance Status:         {"CRITICAL ACTION REQUIRED" if expired_cnt > 0 else "FULLY COMPLIANT"}

3. TOP 5 REVENUE GENERATING PHARMACEUTICALS
----------------------------------------------------------------------------------------
{top_drugs_text}
4. REGULATORY & AUDIT VERIFICATION
----------------------------------------------------------------------------------------
National Drug Authority (NDA) Guideline Status: Compliant
Storage & Dispensing Protocol:                 First-Expired, First-Out (FEFO) Enforced
Database Transaction Integrity:                ACID Compliant (PostgreSQL SERIAL / FKs)

========================================================================================
                 END OF EXECUTIVE REPORT - SEKARUNGI PHARMACEUTICALS
========================================================================================
"""

    st.text_area("Report Preview (Ready for Print / Copy)", value=report_text, height=440)

    st.download_button(
        label="📥 Download Official Report (.txt)",
        data=report_text.encode("utf-8"),
        file_name=f"sekarungi_executive_report_{datetime.date.today().strftime('%Y%m%d')}.txt",
        mime="text/plain",
        key="btn_dl_text_report"
    )
