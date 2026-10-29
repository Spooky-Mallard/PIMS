"""Live Database Tables Browser Module for PIMS
Allows real-time inspection, search, sorting, and CSV export of all 11 database tables from Neon.
"""

import streamlit as st
import pandas as pd
from backend.db import fetch_dataframe

TABLES = [
    "Drug",
    "StockBatch",
    "Sale",
    "SaleItem",
    "DispensingRegister",
    "Supplier",
    "User",
    "PurchaseOrder",
    "PurchaseOrderItem",
    "Expense",
    "Payroll",
]

TABLE_DDL = {
    "Drug": "CREATE TABLE Drug (\n    DrugID SERIAL PRIMARY KEY,\n    DrugName VARCHAR(150) NOT NULL,\n    Category VARCHAR(60),\n    Manufacturer VARCHAR(100),\n    NDARegNo VARCHAR(40),\n    UnitPrice DECIMAL(10, 2) NOT NULL,\n    ReorderLevel INT NOT NULL\n);",
    "StockBatch": "CREATE TABLE StockBatch (\n    BatchID SERIAL PRIMARY KEY,\n    DrugID INT REFERENCES Drug(DrugID),\n    SupplierID INT REFERENCES Supplier(SupplierID),\n    BatchNumber VARCHAR(40) NOT NULL,\n    QuantityReceived INT NOT NULL,\n    QuantityRemaining INT NOT NULL,\n    ExpiryDate DATE NOT NULL,\n    DateReceived DATE NOT NULL\n);",
    "Sale": "CREATE TABLE Sale (\n    SaleID SERIAL PRIMARY KEY,\n    CashierUserID INT REFERENCES \"User\"(UserID),\n    ReceiptNumber VARCHAR(30) UNIQUE NOT NULL,\n    CustomerName VARCHAR(100),\n    SaleDate TIMESTAMP NOT NULL,\n    SubTotal DECIMAL(10, 2) NOT NULL,\n    VATAmount DECIMAL(10, 2) NOT NULL,\n    TotalAmount DECIMAL(10, 2) NOT NULL,\n    PaymentType VARCHAR(20) CHECK (PaymentType IN ('Cash', 'MobileMoney', 'Card'))\n);",
    "SaleItem": "CREATE TABLE SaleItem (\n    SaleItemID SERIAL PRIMARY KEY,\n    SaleID INT REFERENCES Sale(SaleID),\n    BatchID INT REFERENCES StockBatch(BatchID),\n    Quantity INT NOT NULL,\n    UnitPrice DECIMAL(10, 2) NOT NULL,\n    LineTotal DECIMAL(10, 2) NOT NULL\n);",
    "DispensingRegister": "CREATE TABLE DispensingRegister (\n    RegisterID SERIAL PRIMARY KEY,\n    SaleItemID INT UNIQUE REFERENCES SaleItem(SaleItemID),\n    DispensedByUserID INT REFERENCES \"User\"(UserID),\n    DateDispensed TIMESTAMP NOT NULL,\n    PrescriptionRef VARCHAR(100)\n);",
    "Supplier": "CREATE TABLE Supplier (\n    SupplierID SERIAL PRIMARY KEY,\n    CompanyName VARCHAR(120) NOT NULL,\n    ContactPerson VARCHAR(100),\n    Phone VARCHAR(20),\n    Email VARCHAR(100),\n    Address VARCHAR(200)\n);",
    "User": "CREATE TABLE \"User\" (\n    UserID SERIAL PRIMARY KEY,\n    FullName VARCHAR(100) NOT NULL,\n    Username VARCHAR(50) UNIQUE NOT NULL,\n    PasswordHash VARCHAR(255) NOT NULL,\n    Role VARCHAR(20) CHECK (Role IN ('Director', 'OperationsManager', 'Pharmacist', 'Cashier', 'Dispenser')),\n    Phone VARCHAR(20),\n    Status VARCHAR(10) CHECK (Status IN ('Active', 'Inactive'))\n);",
    "PurchaseOrder": "CREATE TABLE PurchaseOrder (\n    POID SERIAL PRIMARY KEY,\n    SupplierID INT REFERENCES Supplier(SupplierID),\n    CreatedByUserID INT REFERENCES \"User\"(UserID),\n    OrderDate DATE NOT NULL,\n    Status VARCHAR(20) CHECK (Status IN ('Pending', 'Received', 'Cancelled'))\n);",
    "PurchaseOrderItem": "CREATE TABLE PurchaseOrderItem (\n    POItemID SERIAL PRIMARY KEY,\n    POID INT REFERENCES PurchaseOrder(POID),\n    DrugID INT REFERENCES Drug(DrugID),\n    QuantityOrdered INT NOT NULL,\n    UnitCost DECIMAL(10, 2) NOT NULL\n);",
    "Expense": "CREATE TABLE Expense (\n    ExpenseID SERIAL PRIMARY KEY,\n    RecordedByUserID INT REFERENCES \"User\"(UserID),\n    Category VARCHAR(100) NOT NULL,\n    Description TEXT,\n    Amount DECIMAL(12, 2) NOT NULL,\n    ExpenseDate DATE NOT NULL\n);",
    "Payroll": "CREATE TABLE Payroll (\n    PayrollID SERIAL PRIMARY KEY,\n    StaffUserID INT REFERENCES \"User\"(UserID),\n    RecordedByUserID INT REFERENCES \"User\"(UserID),\n    Amount DECIMAL(12, 2) NOT NULL,\n    PaymentDate DATE NOT NULL,\n    PaymentType VARCHAR(20) CHECK (PaymentType IN ('Salary', 'Advance', 'Bonus'))\n);",
}


def render_tables_browser():
    st.title("📋 Live Database Tables Browser")
    st.caption("Inspect live relations directly from Neon PostgreSQL.")

    col_select, col_refresh = st.columns([4, 1])
    with col_select:
        table_name = st.selectbox("Select Table to View:", TABLES, index=0)
    with col_refresh:
        st.write("")
        st.write("")
        refresh = st.button("🔄 Refresh Data")

    # Fetch data
    quoted_name = f'"{table_name}"' if table_name == "User" else table_name.lower()
    try:
        df = fetch_dataframe(f"SELECT * FROM {quoted_name} ORDER BY 1 DESC;")
    except Exception as e:
        st.error(f"Error reading table {table_name}: {e}")
        return

    # Metrics
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Total Records", len(df))
    with m2:
        st.metric("Columns", len(df.columns))
    with m3:
        st.metric("Database Source", "Neon PostgreSQL (Live)")

    # Filter / Search
    search_term = st.text_input(f"🔍 Filter {table_name} records (searches all columns):", "")
    if search_term:
        mask = df.astype(str).apply(lambda row: row.str.contains(search_term, case=False).any(), axis=1)
        filtered_df = df[mask]
        st.caption(f"Showing {len(filtered_df)} of {len(df)} matching rows")
    else:
        filtered_df = df

    # Display Table
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    # Actions
    c1, c2 = st.columns([3, 1])
    with c2:
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f"⬇️ Export {table_name}.csv",
            data=csv_data,
            file_name=f"pims_{table_name.lower()}_export.csv",
            mime="text/csv",
            use_container_width=True
        )

    # DDL
    with st.expander(f"🛠️ View Table DDL Schema: {table_name}"):
        st.code(TABLE_DDL.get(table_name, "-- DDL not available"), language="sql")