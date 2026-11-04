"""PIMS Database Initializer & Canonical Script Executor
Sekarungi Pharmaceuticals Ltd
Makerere University - BCS 2206 Database Management Systems

Directly reads and executes canonical SQL files from db_scripts/ (Single Source of Truth).
Ensures all 11 tables, 4 reporting views, and 20-50 realistic coordinated records are built.
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Locate and load .env from DBMS-PROJECT/.env
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
env_path = os.path.join(project_root, ".env")
load_dotenv(env_path)

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL not found in .env")
    sys.exit(1)

SCRIPTS_DIR = os.path.join(project_root, "db_scripts")


def execute_sql_file(cur, filepath):
    """Read a raw SQL script file and execute its contents."""
    filename = os.path.basename(filepath)
    print(f"  -> Executing: {filename} ...")
    with open(filepath, "r", encoding="utf-8") as f:
        sql_content = f.read()
    cur.execute(sql_content)


def init_database():
    print("=" * 70)
    print("  SEKARUNGI PHARMACEUTICALS LTD — DATABASE INITIALIZATION")
    print("=" * 70)
    print(f"Connecting to Neon PostgreSQL...")

    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cur = conn.cursor()

    print("\n1. Dropping existing views and tables in reverse dependency order...")
    cur.execute("""
        DROP VIEW IF EXISTS vw_monthly_financial_summary CASCADE;
        DROP VIEW IF EXISTS vw_sales_detail CASCADE;
        DROP VIEW IF EXISTS vw_purchase_order_summary CASCADE;
        DROP VIEW IF EXISTS vw_current_stock CASCADE;

        DROP TABLE IF EXISTS DispensingRegister CASCADE;
        DROP TABLE IF EXISTS SaleItem CASCADE;
        DROP TABLE IF EXISTS Sale CASCADE;
        DROP TABLE IF EXISTS PurchaseOrderItem CASCADE;
        DROP TABLE IF EXISTS PurchaseOrder CASCADE;
        DROP TABLE IF EXISTS StockBatch CASCADE;
        DROP TABLE IF EXISTS Payroll CASCADE;
        DROP TABLE IF EXISTS Expense CASCADE;
        DROP TABLE IF EXISTS Drug CASCADE;
        DROP TABLE IF EXISTS Supplier CASCADE;
        DROP TABLE IF EXISTS "User" CASCADE;
    """)
    print("  -> Clean slate prepared.")

    print("\n2. Executing canonical database scripts from db_scripts/ ...")
    canonical_files = [
        "01_foundational_tables.sql",
        "02_inventory_purchasing_tables.sql",
        "03_sales_dispensing_tables.sql",
        "04_financial_tables.sql",
    ]

    for fname in canonical_files:
        fpath = os.path.join(SCRIPTS_DIR, fname)
        if not os.path.exists(fpath):
            raise FileNotFoundError(f"Missing canonical script: {fpath}")
        execute_sql_file(cur, fpath)

    print("\n3. Creating analytical and reporting views...")
    views_ddl = """
    -- 1. Current Stock View
    CREATE OR REPLACE VIEW vw_current_stock AS
    SELECT d.DrugID, d.DrugName, d.Category, d.ReorderLevel,
           COALESCE(SUM(sb.QuantityRemaining), 0) AS TotalStock
    FROM Drug d
    LEFT JOIN StockBatch sb ON sb.DrugID = d.DrugID
    GROUP BY d.DrugID, d.DrugName, d.Category, d.ReorderLevel;

    -- 2. Purchase Order Summary View
    CREATE OR REPLACE VIEW vw_purchase_order_summary AS
    SELECT po.POID, po.OrderDate, po.Status, s.CompanyName AS Supplier,
           u.FullName AS CreatedBy,
           COALESCE(SUM(poi.QuantityOrdered * poi.UnitCost), 0) AS OrderTotal
    FROM PurchaseOrder po
    JOIN Supplier s ON s.SupplierID = po.SupplierID
    JOIN "User" u   ON u.UserID = po.CreatedByUserID
    LEFT JOIN PurchaseOrderItem poi ON poi.POID = po.POID
    GROUP BY po.POID, po.OrderDate, po.Status, s.CompanyName, u.FullName;

    -- 3. Sales Detail View
    CREATE OR REPLACE VIEW vw_sales_detail AS
    SELECT s.SaleID, s.ReceiptNumber, s.SaleDate, s.PaymentType,
           u.FullName AS Cashier, d.DrugName, si.Quantity, si.UnitPrice, si.LineTotal
    FROM Sale s
    JOIN SaleItem si   ON si.SaleID = s.SaleID
    JOIN StockBatch sb ON sb.BatchID = si.BatchID
    JOIN Drug d        ON d.DrugID = sb.DrugID
    JOIN "User" u      ON u.UserID = s.CashierUserID;

    -- 4. Monthly Financial Summary View
    CREATE OR REPLACE VIEW vw_monthly_financial_summary AS
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
    FULL OUTER JOIN payroll p  ON p.Month = COALESCE(r.Month, e.Month);
    """
    cur.execute(views_ddl)
    print("  -> 4 reporting views created successfully.")

    print("\n4. Verifying Table Row Counts (Lecturer 20-50 Requirement):")
    tables = [
        ('"User"', 1),
        ("Supplier", 2),
        ("Drug", 3),
        ("StockBatch", 4),
        ("PurchaseOrder", 5),
        ("PurchaseOrderItem", 6),
        ("Sale", 7),
        ("SaleItem", 8),
        ("DispensingRegister", 9),
        ("Expense", 10),
        ("Payroll", 11),
    ]

    for tbl_name, idx in tables:
        cur.execute(f"SELECT COUNT(*) FROM {tbl_name};")
        count = cur.fetchone()[0]
        status_icon = "✅" if count >= 20 else "⚠️"
        print(f"  {status_icon} Table {idx:2d}: {tbl_name:<22} -> {count:3d} records")

    # Financial Profit & Loss Verification
    cur.execute("SELECT * FROM vw_monthly_financial_summary ORDER BY Month ASC;")
    pnl_rows = cur.fetchall()
    print("\n5. Monthly Profit & Loss Statement (P&L):")
    print(f"  {'Month':<12} | {'Revenue (UGX)':<16} | {'Expenses (UGX)':<16} | {'Payroll (UGX)':<16} | {'Net Profit (UGX)':<16}")
    print("  " + "-" * 88)
    for row in pnl_rows:
        m_str = row[0].strftime("%b %Y") if hasattr(row[0], "strftime") else str(row[0])[:7]
        print(f"  {m_str:<12} | UGX {float(row[1]):>12,.2f} | UGX {float(row[2]):>12,.2f} | UGX {float(row[3]):>12,.2f} | UGX {float(row[4]):>12,.2f}")

    cur.close()
    conn.close()
    print("\n✅ Database setup & seeding complete!")


if __name__ == "__main__":
    init_database()
