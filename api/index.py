"""Sekarungi Pharmaceuticals Ltd - PIMS Vercel Serverless Application Entrypoint
Flask-based Web Application and REST API designed for Vercel Serverless Functions.
Connects directly to Neon PostgreSQL using raw SQL via psycopg2 (No ORM).
"""

import sys
import os
import json
import time
import datetime
from decimal import Decimal

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, jsonify, request, render_template_string
from backend.db import get_db_connection, test_connection, fetch_dataframe, execute_statement

app = Flask(__name__)

# JSON encoder for Decimal, Date, and Timestamp
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return super().default(obj)

app.json_encoder = CustomJSONEncoder


# Pre-defined project queries
PREDEFINED_QUERIES = {
    "q1_1": {
        "title": "Q1.1: Every Batch with Drug & Supplier Info",
        "category": "Inventory",
        "sql": """SELECT sb.BatchID, sb.BatchNumber, d.DrugName, d.Category, s.CompanyName AS Supplier,
       sb.QuantityRemaining, sb.ExpiryDate, sb.DateReceived
FROM StockBatch sb
JOIN Drug d ON sb.DrugID = d.DrugID
JOIN Supplier s ON sb.SupplierID = s.SupplierID
ORDER BY sb.ExpiryDate ASC LIMIT 30;"""
    },
    "q1_3": {
        "title": "Q1.3: Batches Expiring Within 90 Days",
        "category": "Inventory",
        "sql": """SELECT sb.BatchNumber, d.DrugName, sb.ExpiryDate,
       sb.ExpiryDate - CURRENT_DATE AS DaysUntilExpiry, sb.QuantityRemaining
FROM StockBatch sb
JOIN Drug d ON sb.DrugID = d.DrugID
WHERE sb.ExpiryDate BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '90 days'
  AND sb.QuantityRemaining > 0
ORDER BY sb.ExpiryDate ASC;"""
    },
    "q1_4": {
        "title": "Q1.4: Expired Batches Still Holding Stock (Urgent)",
        "category": "Inventory",
        "sql": """SELECT sb.BatchNumber, d.DrugName, s.CompanyName AS Supplier,
       sb.ExpiryDate, CURRENT_DATE - sb.ExpiryDate AS DaysExpired, sb.QuantityRemaining
FROM StockBatch sb
JOIN Drug d ON sb.DrugID = d.DrugID
JOIN Supplier s ON sb.SupplierID = s.SupplierID
WHERE sb.ExpiryDate < CURRENT_DATE AND sb.QuantityRemaining > 0
ORDER BY sb.ExpiryDate ASC;"""
    },
    "q1_5": {
        "title": "Q1.5: Total Stock Valuation by Drug",
        "category": "Inventory",
        "sql": """SELECT d.DrugID, d.DrugName, d.Category,
       SUM(sb.QuantityRemaining) AS TotalUnitsRemaining,
       d.UnitPrice,
       SUM(sb.QuantityRemaining * d.UnitPrice) AS TotalStockValue
FROM Drug d
LEFT JOIN StockBatch sb ON d.DrugID = sb.DrugID
GROUP BY d.DrugID, d.DrugName, d.Category, d.UnitPrice
ORDER BY TotalStockValue DESC;"""
    },
    "q2_3": {
        "title": "Q2.3: Top Suppliers by Total Purchase Order Value",
        "category": "Purchasing",
        "sql": """SELECT s.SupplierID, s.CompanyName, s.ContactPerson,
       COUNT(po.POID) AS TotalOrdersPlaced,
       COALESCE(SUM(po.TotalCost), 0) AS TotalSpendUGX
FROM Supplier s
JOIN PurchaseOrder po ON s.SupplierID = po.SupplierID
GROUP BY s.SupplierID, s.CompanyName, s.ContactPerson
ORDER BY TotalSpendUGX DESC;"""
    },
    "q3_1": {
        "title": "Q3.1: Daily Sales Revenue Trend",
        "category": "Sales",
        "sql": """SELECT DATE(SaleDate) AS SaleDay,
       COUNT(SaleID) AS TotalTransactions,
       SUM(SubTotal) AS GrossRevenue,
       SUM(VATAmount) AS TotalVAT,
       SUM(TotalAmount) AS NetCustomerSpend
FROM Sale
GROUP BY DATE(SaleDate)
ORDER BY SaleDay DESC LIMIT 15;"""
    },
    "q3_2": {
        "title": "Q3.2: Top 10 Best-Selling Drugs by Revenue",
        "category": "Sales",
        "sql": """SELECT d.DrugName, d.Category,
       SUM(si.Quantity) AS UnitsSold,
       SUM(si.LineTotal) AS TotalRevenueUGX
FROM SaleItem si
JOIN StockBatch sb ON si.BatchID = sb.BatchID
JOIN Drug d ON sb.DrugID = d.DrugID
GROUP BY d.DrugName, d.Category
ORDER BY TotalRevenueUGX DESC LIMIT 10;"""
    },
    "q4_1": {
        "title": "Q4.1: Operating Expenses by Category",
        "category": "Finance",
        "sql": """SELECT Category,
       COUNT(ExpenseID) AS ExpenseCount,
       SUM(Amount) AS TotalSpentUGX,
       ROUND((SUM(Amount) * 100.0 / (SELECT SUM(Amount) FROM Expense)), 2) AS PctOfTotal
FROM Expense
GROUP BY Category
ORDER BY TotalSpentUGX DESC;"""
    },
    "q4_6": {
        "title": "Q4.6: Monthly Net Operating Profit Summary",
        "category": "Finance",
        "sql": """SELECT 
    m.MonthName,
    m.GrossRevenue,
    m.OperationalExpenses,
    m.StaffPayroll,
    m.NetOperatingProfit,
    ROUND((m.NetOperatingProfit * 100.0 / NULLIF(m.GrossRevenue, 0)), 2) AS ProfitMarginPct
FROM (
    SELECT 
        TO_CHAR(s.SaleMonth, 'Month YYYY') AS MonthName,
        s.GrossRevenue,
        COALESCE(e.TotalExpenses, 0) AS OperationalExpenses,
        COALESCE(p.TotalPayroll, 0) AS StaffPayroll,
        (s.GrossRevenue - COALESCE(e.TotalExpenses, 0) - COALESCE(p.TotalPayroll, 0)) AS NetOperatingProfit
    FROM (
        SELECT DATE_TRUNC('month', SaleDate) AS SaleMonth, SUM(TotalAmount) AS GrossRevenue
        FROM Sale GROUP BY DATE_TRUNC('month', SaleDate)
    ) s
    LEFT JOIN (
        SELECT DATE_TRUNC('month', ExpenseDate) AS ExpMonth, SUM(Amount) AS TotalExpenses
        FROM Expense GROUP BY DATE_TRUNC('month', ExpenseDate)
    ) e ON s.SaleMonth = e.ExpMonth
    LEFT JOIN (
        SELECT DATE_TRUNC('month', PayDate) AS PayMonth, SUM(Amount) AS TotalPayroll
        FROM Payroll GROUP BY DATE_TRUNC('month', PayDate)
    ) p ON s.SaleMonth = p.PayMonth
) m
ORDER BY m.GrossRevenue DESC;"""
    }
}


@app.route("/api/health")
def api_health():
    """Health check endpoint for Vercel, uptime pingers, and monitoring."""
    db_ok, db_info = test_connection()
    status_code = 200 if db_ok else 503
    return jsonify({
        "status": "healthy" if db_ok else "degraded",
        "service": "Sekarungi PIMS (Vercel)",
        "database": {
            "connected": db_ok,
            "engine": db_info.get("database", "neondb") if db_ok else "disconnected",
            "host": db_info.get("host", "neon.tech") if db_ok else "unknown",
            "version": db_info.get("version", "PostgreSQL") if db_ok else None
        },
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }), status_code


@app.route("/api/stats")
def api_stats():
    """Fetch Executive Dashboard KPIs."""
    try:
        catalog_count = fetch_dataframe("SELECT COUNT(*) FROM Drug;").iloc[0, 0]
        stock_sum = fetch_dataframe("SELECT COALESCE(SUM(QuantityRemaining), 0) FROM StockBatch;").iloc[0, 0]
        batches_count = fetch_dataframe("SELECT COUNT(*) FROM StockBatch;").iloc[0, 0]
        sales_rev = fetch_dataframe("SELECT COALESCE(SUM(TotalAmount), 0) FROM Sale;").iloc[0, 0]
        sales_count = fetch_dataframe("SELECT COUNT(*) FROM Sale;").iloc[0, 0]
        expired_count = fetch_dataframe("SELECT COUNT(*) FROM StockBatch WHERE ExpiryDate < CURRENT_DATE AND QuantityRemaining > 0;").iloc[0, 0]
        
        recent_sales = fetch_dataframe("""
            SELECT s.ReceiptNumber, s.CustomerName, s.PaymentType, s.TotalAmount, s.SaleDate, u.Username AS Cashier
            FROM Sale s
            LEFT JOIN "User" u ON s.CashierUserID = u.UserID
            ORDER BY s.SaleDate DESC LIMIT 5;
        """).to_dict(orient="records")

        return jsonify({
            "success": True,
            "catalog_count": int(catalog_count),
            "stock_sum": int(stock_sum),
            "batches_count": int(batches_count),
            "sales_rev": float(sales_rev),
            "sales_count": int(sales_count),
            "expired_count": int(expired_count),
            "recent_sales": recent_sales
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/tables/<table_name>")
def api_table_data(table_name):
    """Fetch records from any of the 11 tables with limit."""
    allowed_tables = [
        "User", "Supplier", "Drug", "StockBatch", "PurchaseOrder",
        "PurchaseOrderItem", "Sale", "SaleItem", "DispensingRegister",
        "Expense", "Payroll"
    ]
    if table_name not in allowed_tables:
        return jsonify({"error": "Table not found or access denied"}), 404

    try:
        quoted_name = f'"{table_name}"' if table_name == "User" else table_name
        total_count = fetch_dataframe(f"SELECT COUNT(*) FROM {quoted_name};").iloc[0, 0]
        df = fetch_dataframe(f"SELECT * FROM {quoted_name} LIMIT 50;")
        return jsonify({
            "table": table_name,
            "total_count": int(total_count),
            "columns": list(df.columns),
            "rows": df.to_dict(orient="records")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/query", methods=["POST"])
def api_run_query():
    """Execute a pre-defined or custom SELECT query."""
    data = request.get_json() or {}
    query_key = data.get("query_key")
    custom_sql = data.get("custom_sql", "").strip()

    if query_key and query_key in PREDEFINED_QUERIES:
        sql = PREDEFINED_QUERIES[query_key]["sql"]
    elif custom_sql:
        if not custom_sql.upper().startswith("SELECT"):
            return jsonify({"error": "Only SELECT queries are permitted in the explorer."}), 400
        sql = custom_sql
    else:
        return jsonify({"error": "No query specified."}), 400

    try:
        start_t = time.time()
        df = fetch_dataframe(sql)
        elapsed_ms = round((time.time() - start_t) * 1000, 1)
        return jsonify({
            "success": True,
            "latency_ms": elapsed_ms,
            "columns": list(df.columns),
            "rows": df.to_dict(orient="records")
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/forms/drug", methods=["POST"])
def api_add_drug():
    """Insert a new drug catalog item."""
    data = request.get_json() or {}
    drug_name = data.get("drug_name")
    category = data.get("category", "Other")
    manufacturer = data.get("manufacturer", "")
    unit_price = data.get("unit_price")
    reorder_level = data.get("reorder_level", 50)

    if not drug_name or not unit_price:
        return jsonify({"error": "Drug name and unit price are required."}), 400

    try:
        sql = """INSERT INTO Drug (DrugName, Category, Manufacturer, UnitPrice, ReorderLevel)
                 VALUES (%s, %s, %s, %s, %s) RETURNING DrugID;"""
        execute_statement(sql, (drug_name, category, manufacturer, unit_price, reorder_level))
        return jsonify({"success": True, "message": f"Successfully registered drug: {drug_name}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/reports/pnl")
def api_reports_pnl():
    """Fetch financial summary for charts."""
    try:
        df = fetch_dataframe("""
            SELECT 
                TO_CHAR(s.SaleMonth, 'Mon YYYY') AS month_label,
                s.GrossRevenue AS revenue,
                COALESCE(e.TotalExpenses, 0) AS expenses,
                COALESCE(p.TotalPayroll, 0) AS payroll,
                (s.GrossRevenue - COALESCE(e.TotalExpenses, 0) - COALESCE(p.TotalPayroll, 0)) AS profit
            FROM (
                SELECT DATE_TRUNC('month', SaleDate) AS SaleMonth, SUM(TotalAmount) AS GrossRevenue
                FROM Sale GROUP BY DATE_TRUNC('month', SaleDate)
            ) s
            LEFT JOIN (
                SELECT DATE_TRUNC('month', ExpenseDate) AS ExpMonth, SUM(Amount) AS TotalExpenses
                FROM Expense GROUP BY DATE_TRUNC('month', ExpenseDate)
            ) e ON s.SaleMonth = e.ExpMonth
            LEFT JOIN (
                SELECT DATE_TRUNC('month', PayDate) AS PayMonth, SUM(Amount) AS TotalPayroll
                FROM Payroll GROUP BY DATE_TRUNC('month', PayDate)
            ) p ON s.SaleMonth = p.PayMonth
            ORDER BY s.SaleMonth ASC;
        """)
        return jsonify({
            "months": df["month_label"].tolist(),
            "revenue": [float(x) for x in df["revenue"].tolist()],
            "expenses": [float(x) for x in df["expenses"].tolist()],
            "payroll": [float(x) for x in df["payroll"].tolist()],
            "profit": [float(x) for x in df["profit"].tolist()]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Full HTML Template for Single-Page Application on Vercel
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sekarungi PIMS | Pharmacy Management</title>
  <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>💊</text></svg>">
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    .sidebar-active { background-color: #0f766e; color: #ffffff; }
  </style>
</head>
<body class="bg-slate-50 text-slate-800 font-sans antialiased">
  <div class="flex h-screen overflow-hidden">
    <!-- Sidebar -->
    <aside class="w-64 bg-slate-900 text-slate-300 flex flex-col justify-between shadow-xl">
      <div>
        <div class="p-5 border-b border-slate-800 bg-slate-950">
          <div class="flex items-center space-x-3">
            <span class="text-3xl">💊</span>
            <div>
              <h1 class="text-lg font-bold text-teal-400">Sekarungi PIMS</h1>
              <p class="text-xs text-slate-400">Pharmacy System</p>
            </div>
          </div>
        </div>
        
        <nav class="mt-4 px-3 space-y-1">
          <button onclick="switchTab('dashboard')" id="btn-dashboard" class="sidebar-btn w-full flex items-center space-x-3 px-4 py-2.5 rounded-lg text-sm font-medium transition hover:bg-slate-800 sidebar-active">
            <i class="fa-solid fa-gauge w-5"></i>
            <span>Executive Dashboard</span>
          </button>
          <button onclick="switchTab('tables')" id="btn-tables" class="sidebar-btn w-full flex items-center space-x-3 px-4 py-2.5 rounded-lg text-sm font-medium transition hover:bg-slate-800">
            <i class="fa-solid fa-table w-5"></i>
            <span>Database Tables</span>
          </button>
          <button onclick="switchTab('queries')" id="btn-queries" class="sidebar-btn w-full flex items-center space-x-3 px-4 py-2.5 rounded-lg text-sm font-medium transition hover:bg-slate-800">
            <i class="fa-solid fa-magnifying-glass w-5"></i>
            <span>SQL Query Explorer</span>
          </button>
          <button onclick="switchTab('reports')" id="btn-reports" class="sidebar-btn w-full flex items-center space-x-3 px-4 py-2.5 rounded-lg text-sm font-medium transition hover:bg-slate-800">
            <i class="fa-solid fa-chart-column w-5"></i>
            <span>Financial & Reports</span>
          </button>
          <button onclick="switchTab('forms')" id="btn-forms" class="sidebar-btn w-full flex items-center space-x-3 px-4 py-2.5 rounded-lg text-sm font-medium transition hover:bg-slate-800">
            <i class="fa-solid fa-cash-register w-5"></i>
            <span>Data Entry Forms</span>
          </button>
        </nav>
      </div>

      <!-- System Status Banner -->
      <div class="p-4 border-t border-slate-800 bg-slate-950 text-xs">
        <div class="flex items-center space-x-2 text-emerald-400 font-semibold mb-1">
          <span class="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Neon PostgreSQL Online</span>
        </div>
        <p class="text-slate-500">DB: <code class="text-teal-300">neondb</code> (Pure SQL / No ORM)</p>
        <p class="text-slate-500 mt-2 text-[10px]">Makerere Univ • BCS 2206 DBMS</p>
      </div>
    </aside>

    <!-- Main Content Area -->
    <main class="flex-1 overflow-y-auto p-8">
      <!-- Top Header -->
      <header class="flex justify-between items-center pb-6 border-b border-slate-200 mb-6">
        <div>
          <h2 id="page-title" class="text-2xl font-bold text-slate-800">Executive Dashboard</h2>
          <p id="page-subtitle" class="text-sm text-slate-500">Real-time inventory valuation, revenue, and compliance audit.</p>
        </div>
        <div class="flex items-center space-x-3">
          <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-teal-100 text-teal-800">
            <i class="fa-solid fa-cloud mr-1.5"></i> Vercel Serverless
          </span>
          <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
            <i class="fa-solid fa-database mr-1.5"></i> PostgreSQL 18.7
          </span>
        </div>
      </header>

      <!-- TAB 1: DASHBOARD -->
      <section id="tab-dashboard" class="space-y-6">
        <!-- KPI Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-5">
          <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center space-x-4">
            <div class="p-3 bg-teal-50 rounded-lg text-teal-600 text-2xl"><i class="fa-solid fa-pills"></i></div>
            <div>
              <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Catalog Items</p>
              <h3 id="stat-catalog" class="text-2xl font-bold text-slate-800">25 Products</h3>
              <p class="text-xs text-emerald-600 font-medium mt-0.5">Active catalog formulations</p>
            </div>
          </div>
          <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center space-x-4">
            <div class="p-3 bg-blue-50 rounded-lg text-blue-600 text-2xl"><i class="fa-solid fa-boxes-stacked"></i></div>
            <div>
              <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Warehouse Stock</p>
              <h3 id="stat-stock" class="text-2xl font-bold text-slate-800">6,287 Units</h3>
              <p class="text-xs text-blue-600 font-medium mt-0.5">Across 30 active batches</p>
            </div>
          </div>
          <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center space-x-4">
            <div class="p-3 bg-emerald-50 rounded-lg text-emerald-600 text-2xl"><i class="fa-solid fa-money-bill-wave"></i></div>
            <div>
              <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Retail Revenue</p>
              <h3 id="stat-revenue" class="text-2xl font-bold text-slate-800">UGX 48.6M</h3>
              <p class="text-xs text-emerald-600 font-medium mt-0.5">From 45 sales transactions</p>
            </div>
          </div>
          <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center space-x-4">
            <div class="p-3 bg-rose-50 rounded-lg text-rose-600 text-2xl"><i class="fa-solid fa-triangle-exclamation"></i></div>
            <div>
              <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Compliance Alert</p>
              <h3 id="stat-expired" class="text-2xl font-bold text-rose-600">2 Expired</h3>
              <p class="text-xs text-rose-500 font-medium mt-0.5">Batches quarantined (FEFO)</p>
            </div>
          </div>
        </div>

        <!-- Compliance Warning Banner -->
        <div class="bg-amber-50 border-l-4 border-amber-500 p-4 rounded-r-lg shadow-sm flex items-start space-x-3">
          <i class="fa-solid fa-triangle-exclamation text-amber-600 text-lg mt-0.5"></i>
          <div>
            <h4 class="text-sm font-semibold text-amber-800">Regulatory FEFO Compliance Warning</h4>
            <p class="text-xs text-amber-700 mt-1">2 batch(es) have surpassed their expiration dates (<code class="bg-amber-100 px-1 py-0.5 rounded text-amber-900">BN-PARA-OLD1</code> and <code class="bg-amber-100 px-1 py-0.5 rounded text-amber-900">BN-AMOX-OLD1</code>) and remain restricted from dispensing.</p>
          </div>
        </div>

        <!-- Recent Activity Feed -->
        <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h3 class="text-base font-bold text-slate-800 mb-4 flex items-center">
            <i class="fa-solid fa-clock-rotate-left mr-2 text-teal-600"></i> Recent Sales Transactions
          </h3>
          <div class="overflow-x-auto">
            <table class="w-full text-left text-sm text-slate-600">
              <thead class="bg-slate-50 text-xs uppercase font-semibold text-slate-500 border-b border-slate-200">
                <tr>
                  <th class="py-3 px-4">Receipt #</th>
                  <th class="py-3 px-4">Customer</th>
                  <th class="py-3 px-4">Payment</th>
                  <th class="py-3 px-4">Total Amount (UGX)</th>
                  <th class="py-3 px-4">Date & Time</th>
                </tr>
              </thead>
              <tbody id="table-recent-sales" class="divide-y divide-slate-100">
                <tr><td colspan="5" class="text-center py-4 text-slate-400">Loading recent transactions...</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- TAB 2: DATABASE TABLES BROWSER -->
      <section id="tab-tables" class="hidden space-y-6">
        <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div class="flex justify-between items-center mb-4">
            <div>
              <h3 class="text-lg font-bold text-slate-800">Select Database Table:</h3>
              <p class="text-xs text-slate-500">Directly inspect all 11 normalized PostgreSQL tables.</p>
            </div>
            <div class="flex items-center space-x-2">
              <select id="select-table" onchange="loadTableData()" class="bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-sm font-medium focus:ring-teal-500 focus:border-teal-500">
                <option value="User">1. User (20 rows)</option>
                <option value="Supplier">2. Supplier (20 rows)</option>
                <option value="Drug" selected>3. Drug (25 rows)</option>
                <option value="StockBatch">4. StockBatch (30 rows)</option>
                <option value="PurchaseOrder">5. PurchaseOrder (20 rows)</option>
                <option value="PurchaseOrderItem">6. PurchaseOrderItem (35 rows)</option>
                <option value="Sale">7. Sale (45 rows)</option>
                <option value="SaleItem">8. SaleItem (70 rows)</option>
                <option value="DispensingRegister">9. DispensingRegister (35 rows)</option>
                <option value="Expense">10. Expense (24 rows)</option>
                <option value="Payroll">11. Payroll (24 rows)</option>
              </select>
              <button onclick="loadTableData()" class="px-3 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-lg text-sm font-medium transition">
                <i class="fa-solid fa-arrows-rotate mr-1"></i> Refresh
              </button>
            </div>
          </div>

          <div id="table-container" class="overflow-x-auto border border-slate-200 rounded-lg max-h-[550px]">
            <table class="w-full text-left text-xs text-slate-600">
              <thead id="tbl-browser-head" class="bg-slate-100 text-slate-700 uppercase font-semibold sticky top-0"></thead>
              <tbody id="tbl-browser-body" class="divide-y divide-slate-100 bg-white"></tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- TAB 3: SQL QUERY EXPLORER -->
      <section id="tab-queries" class="hidden space-y-6">
        <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div class="flex justify-between items-center">
            <div>
              <h3 class="text-lg font-bold text-slate-800">Pre-built Query Suite:</h3>
              <p class="text-xs text-slate-500">Select any project query across Inventory, Purchasing, Sales, or Finance.</p>
            </div>
            <select id="select-query" onchange="runPredefinedQuery()" class="bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-sm font-medium w-96">
              <option value="q1_1">Q1.1: Every Batch with Drug & Supplier Info</option>
              <option value="q1_3">Q1.3: Batches Expiring Within 90 Days</option>
              <option value="q1_4">Q1.4: Expired Batches Still Holding Stock</option>
              <option value="q1_5">Q1.5: Total Stock Valuation by Drug</option>
              <option value="q2_3">Q2.3: Top Suppliers by Total Purchase Spend</option>
              <option value="q3_1">Q3.1: Daily Sales Revenue Trend</option>
              <option value="q3_2">Q3.2: Top 10 Best-Selling Drugs by Revenue</option>
              <option value="q4_1">Q4.1: Operating Expenses by Category</option>
              <option value="q4_6" selected>Q4.6: Monthly Net Operating Profit Summary</option>
            </select>
          </div>

          <div class="bg-slate-900 text-slate-100 p-4 rounded-lg font-mono text-xs overflow-x-auto">
            <span class="text-slate-500 block mb-1">-- Raw SQL Statement</span>
            <code id="sql-display">Loading SQL...</code>
          </div>

          <div class="flex items-center space-x-3">
            <button onclick="runPredefinedQuery()" class="px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-lg text-sm font-medium transition flex items-center">
              <i class="fa-solid fa-play mr-2"></i> Execute Query
            </button>
            <span id="query-latency" class="text-xs text-slate-500 font-mono"></span>
          </div>

          <div id="query-results-container" class="overflow-x-auto border border-slate-200 rounded-lg max-h-[450px]">
            <table class="w-full text-left text-xs text-slate-600">
              <thead id="query-head" class="bg-slate-100 text-slate-700 uppercase font-semibold sticky top-0"></thead>
              <tbody id="query-body" class="divide-y divide-slate-100 bg-white"></tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- TAB 4: FINANCIAL REPORTS -->
      <section id="tab-reports" class="hidden space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <h3 class="text-base font-bold text-slate-800 mb-2">Monthly Profit & Loss Breakdown (UGX)</h3>
            <p class="text-xs text-slate-500 mb-4">Comparing Gross Sales Revenue vs Expenses vs Payroll.</p>
            <div class="h-64">
              <canvas id="chart-pnl"></canvas>
            </div>
          </div>
          <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
            <div>
              <h3 class="text-base font-bold text-slate-800 mb-2">Official Financial Audit Statement</h3>
              <p class="text-xs text-slate-500 mb-4">Synthesized via <code class="bg-slate-100 px-1 py-0.5 rounded text-teal-800">vw_monthly_financial_summary</code>.</p>
              <div class="space-y-3 text-sm">
                <div class="flex justify-between py-2 border-b border-slate-100">
                  <span class="text-slate-600">Gross Sales Revenue:</span>
                  <span class="font-bold text-emerald-600">UGX 48,633,700</span>
                </div>
                <div class="flex justify-between py-2 border-b border-slate-100">
                  <span class="text-slate-600">Operating Expenses:</span>
                  <span class="font-bold text-rose-500">- UGX 9,870,000</span>
                </div>
                <div class="flex justify-between py-2 border-b border-slate-100">
                  <span class="text-slate-600">Staff Payroll Disbursements:</span>
                  <span class="font-bold text-amber-600">- UGX 22,350,000</span>
                </div>
                <div class="flex justify-between py-3 border-t-2 border-slate-800 text-base font-bold">
                  <span class="text-slate-900">Net Operating Profit:</span>
                  <span class="text-teal-600">UGX 16,413,700</span>
                </div>
              </div>
            </div>
            <div class="mt-4 p-3 bg-teal-50 rounded-lg text-xs text-teal-800 font-medium">
              <i class="fa-solid fa-circle-check mr-1 text-teal-600"></i> Net Commercial Profit Margin: <strong>33.75%</strong>
            </div>
          </div>
        </div>
      </section>

      <!-- TAB 5: DATA ENTRY FORMS -->
      <section id="tab-forms" class="hidden space-y-6">
        <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm max-w-2xl mx-auto">
          <h3 class="text-lg font-bold text-slate-800 mb-1 flex items-center">
            <i class="fa-solid fa-prescription-bottle-medical mr-2 text-teal-600"></i> Register New Drug in Catalog
          </h3>
          <p class="text-xs text-slate-500 mb-6">Executes a raw parameterized SQL INSERT statement into the <code class="bg-slate-100 px-1 rounded text-teal-700">Drug</code> table.</p>

          <form onsubmit="submitDrugForm(event)" class="space-y-4">
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Drug Brand & Generic Name *</label>
              <input type="text" id="form-drug-name" required placeholder="e.g. Cefixime 200mg" class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-teal-500 focus:border-teal-500">
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-semibold text-slate-700 mb-1">Category *</label>
                <select id="form-category" class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg">
                  <option>Antibiotic</option>
                  <option>Analgesic</option>
                  <option>Antimalarial</option>
                  <option>Antihypertensive</option>
                  <option>Antacid</option>
                  <option>Supplement</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-semibold text-slate-700 mb-1">Manufacturer *</label>
                <input type="text" id="form-mfr" required placeholder="e.g. Cipla Quality Chemicals" class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg">
              </div>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-semibold text-slate-700 mb-1">Unit Selling Price (UGX) *</label>
                <input type="number" id="form-price" required step="100" placeholder="e.g. 15000" class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg">
              </div>
              <div>
                <label class="block text-xs font-semibold text-slate-700 mb-1">Reorder Threshold Level *</label>
                <input type="number" id="form-reorder" required value="50" class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg">
              </div>
            </div>

            <div id="form-status-msg" class="text-xs font-medium py-1"></div>

            <button type="submit" class="w-full py-2.5 bg-teal-600 hover:bg-teal-700 text-white rounded-lg text-sm font-semibold transition">
              <i class="fa-solid fa-plus mr-1.5"></i> Insert Drug into Neon PostgreSQL
            </button>
          </form>
        </div>
      </section>
    </main>
  </div>

  <script>
    // Tab switching logic
    function switchTab(tabId) {
      document.querySelectorAll('main > section').forEach(sec => sec.classList.add('hidden'));
      document.querySelectorAll('.sidebar-btn').forEach(btn => btn.classList.remove('sidebar-active'));
      
      document.getElementById('tab-' + tabId).classList.remove('hidden');
      document.getElementById('btn-' + tabId).classList.add('sidebar-active');

      const titles = {
        dashboard: ["Executive Dashboard", "Real-time inventory valuation, revenue, and compliance audit."],
        tables: ["Database Tables Browser", "Directly inspect records across all 11 normalized tables."],
        queries: ["SQL Query Explorer", "Run pre-built business queries or arbitrary SELECT statements."],
        reports: ["Financial & Management Reports", "Monthly Profit & Loss and sales revenue analytics."],
        forms: ["Data Entry & POS Forms", "Insert transactions and records with raw SQL execution."]
      };
      document.getElementById('page-title').innerText = titles[tabId][0];
      document.getElementById('page-subtitle').innerText = titles[tabId][1];

      if (tabId === 'tables') loadTableData();
      if (tabId === 'queries') runPredefinedQuery();
      if (tabId === 'reports') loadPnlChart();
    }

    // Load Dashboard Stats
    async function loadStats() {
      try {
        const res = await fetch('/api/stats');
        const data = await res.json();
        if (data.success) {
          document.getElementById('stat-catalog').innerText = data.catalog_count + ' Products';
          document.getElementById('stat-stock').innerText = data.stock_sum.toLocaleString() + ' Units';
          document.getElementById('stat-revenue').innerText = 'UGX ' + (data.sales_rev / 1000000).toFixed(1) + 'M';
          document.getElementById('stat-expired').innerText = data.expired_count + ' Expired';

          const tbody = document.getElementById('table-recent-sales');
          tbody.innerHTML = data.recent_sales.map(s => `
            <tr class="hover:bg-slate-50">
              <td class="py-2.5 px-4 font-mono font-semibold text-teal-700">${s.receiptnumber}</td>
              <td class="py-2.5 px-4">${s.customername || 'Walk-in Customer'}</td>
              <td class="py-2.5 px-4"><span class="px-2 py-0.5 rounded text-xs bg-slate-100 text-slate-700 font-medium">${s.paymenttype}</span></td>
              <td class="py-2.5 px-4 font-semibold text-slate-800">UGX ${Number(s.totalamount).toLocaleString()}</td>
              <td class="py-2.5 px-4 text-xs text-slate-400">${s.saledate ? s.saledate.slice(0, 16).replace('T', ' ') : ''}</td>
            </tr>
          `).join('');
        }
      } catch (err) {
        console.error(err);
      }
    }

    // Load Database Table Browser
    async function loadTableData() {
      const tableName = document.getElementById('select-table').value;
      const head = document.getElementById('tbl-browser-head');
      const body = document.getElementById('tbl-browser-body');
      body.innerHTML = '<tr><td class="p-4 text-slate-400">Loading table records...</td></tr>';
      
      try {
        const res = await fetch('/api/tables/' + tableName);
        const data = await res.json();
        head.innerHTML = '<tr>' + data.columns.map(c => `<th class="py-2 px-3 border-b">${c}</th>`).join('') + '</tr>';
        body.innerHTML = data.rows.map(row => `
          <tr class="hover:bg-slate-50 border-b border-slate-50">
            ${data.columns.map(c => `<td class="py-2 px-3 whitespace-nowrap">${row[c] !== null ? row[c] : '<span class="text-slate-300">NULL</span>'}</td>`).join('')}
          </tr>
        `).join('');
      } catch (err) {
        body.innerHTML = `<tr><td class="p-4 text-rose-500">Error loading table: ${err}</td></tr>`;
      }
    }

    // Run Pre-defined Queries
    const queries = """ + json.dumps({k: v["sql"] for k, v in PREDEFINED_QUERIES.items()}) + """;
    async function runPredefinedQuery() {
      const key = document.getElementById('select-query').value;
      document.getElementById('sql-display').innerText = queries[key] || '';
      
      const head = document.getElementById('query-head');
      const body = document.getElementById('query-body');
      const latency = document.getElementById('query-latency');
      body.innerHTML = '<tr><td class="p-4 text-slate-400">Executing query on Neon PostgreSQL...</td></tr>';
      
      try {
        const res = await fetch('/api/query', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({query_key: key})
        });
        const data = await res.json();
        if (data.success) {
          latency.innerText = `Latency: ${data.latency_ms} ms (${data.rows.length} rows returned)`;
          head.innerHTML = '<tr>' + data.columns.map(c => `<th class="py-2 px-3 border-b">${c}</th>`).join('') + '</tr>';
          body.innerHTML = data.rows.map(row => `
            <tr class="hover:bg-slate-50 border-b border-slate-50">
              ${data.columns.map(c => `<td class="py-2 px-3 whitespace-nowrap">${row[c] !== null ? row[c] : '<span class="text-slate-300">NULL</span>'}</td>`).join('')}
            </tr>
          `).join('');
        } else {
          body.innerHTML = `<tr><td class="p-4 text-rose-500">Query error: ${data.error}</td></tr>`;
        }
      } catch (err) {
        body.innerHTML = `<tr><td class="p-4 text-rose-500">Error: ${err}</td></tr>`;
      }
    }

    // Chart.js P&L Chart
    let pnlChart = null;
    async function loadPnlChart() {
      if (pnlChart) return;
      try {
        const res = await fetch('/api/reports/pnl');
        const data = await res.json();
        const ctx = document.getElementById('chart-pnl').getContext('2d');
        pnlChart = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: data.months,
            datasets: [
              { label: 'Revenue', data: data.revenue, backgroundColor: '#0d9488' },
              { label: 'Expenses', data: data.expenses, backgroundColor: '#f43f5e' },
              { label: 'Payroll', data: data.payroll, backgroundColor: '#f59e0b' },
              { label: 'Net Profit', data: data.profit, backgroundColor: '#10b981' }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: { y: { ticks: { callback: v => (v / 1000000) + 'M' } } }
          }
        });
      } catch (err) {
        console.error(err);
      }
    }

    // Submit New Drug Form
    async function submitDrugForm(e) {
      e.preventDefault();
      const msg = document.getElementById('form-status-msg');
      msg.innerText = 'Submitting to database...';
      msg.className = 'text-xs text-slate-500 py-1';
      
      const payload = {
        drug_name: document.getElementById('form-drug-name').value,
        category: document.getElementById('form-category').value,
        manufacturer: document.getElementById('form-mfr').value,
        unit_price: parseFloat(document.getElementById('form-price').value),
        reorder_level: parseInt(document.getElementById('form-reorder').value)
      };

      try {
        const res = await fetch('/api/forms/drug', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
          msg.innerText = '✅ ' + data.message;
          msg.className = 'text-xs text-emerald-600 font-semibold py-1';
          e.target.reset();
        } else {
          msg.innerText = '❌ Error: ' + data.error;
          msg.className = 'text-xs text-rose-600 font-semibold py-1';
        }
      } catch (err) {
        msg.innerText = '❌ Connection error: ' + err;
        msg.className = 'text-xs text-rose-600 font-semibold py-1';
      }
    }

    // Initial load
    loadStats();
  </script>
</body>
</html>
"""

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    """Serve the Single-Page Application on Vercel."""
    if path.startswith("api/"):
        return jsonify({"error": "Endpoint not found"}), 404
    return render_template_string(HTML_TEMPLATE)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)
