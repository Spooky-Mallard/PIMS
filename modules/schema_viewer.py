"""Schema Viewer Module for PIMS
Displays the ERD, UML Class Diagram, and complete 11-table Data Dictionary.
"""

import os
import streamlit as st
import pandas as pd

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

DATA_DICTIONARY = {
    "User": [
        {"Attribute": "UserID", "Type": "SERIAL (INT)", "Key": "PK", "Nullable": "No", "Description": "Unique staff identifier"},
        {"Attribute": "FullName", "Type": "VARCHAR(100)", "Key": "-", "Nullable": "No", "Description": "Staff member's full legal name"},
        {"Attribute": "Username", "Type": "VARCHAR(50)", "Key": "UNIQUE", "Nullable": "No", "Description": "Unique system login credential"},
        {"Attribute": "PasswordHash", "Type": "VARCHAR(255)", "Key": "-", "Nullable": "No", "Description": "PBKDF2/SHA256 password hash (never plain text)"},
        {"Attribute": "Role", "Type": "VARCHAR(20)", "Key": "CHECK", "Nullable": "Yes", "Description": "Role: Director, OperationsManager, Pharmacist, Cashier, Dispenser"},
        {"Attribute": "Phone", "Type": "VARCHAR(20)", "Key": "-", "Nullable": "Yes", "Description": "Staff telephone contact"},
        {"Attribute": "Status", "Type": "VARCHAR(10)", "Key": "CHECK", "Nullable": "Yes", "Description": "Account status: Active / Inactive (soft deactivation)"},
    ],
    "Supplier": [
        {"Attribute": "SupplierID", "Type": "SERIAL (INT)", "Key": "PK", "Nullable": "No", "Description": "Unique supplier identifier"},
        {"Attribute": "CompanyName", "Type": "VARCHAR(120)", "Key": "-", "Nullable": "No", "Description": "Registered corporate or trading name"},
        {"Attribute": "ContactPerson", "Type": "VARCHAR(100)", "Key": "-", "Nullable": "Yes", "Description": "Supplier sales representative name"},
        {"Attribute": "Phone", "Type": "VARCHAR(20)", "Key": "-", "Nullable": "Yes", "Description": "Supplier phone number"},
        {"Attribute": "Email", "Type": "VARCHAR(100)", "Key": "-", "Nullable": "Yes", "Description": "Supplier contact email"},
        {"Attribute": "Address", "Type": "VARCHAR(200)", "Key": "-", "Nullable": "Yes", "Description": "Physical or postal warehouse address"},
    ],
    "Drug": [
        {"Attribute": "DrugID", "Type": "SERIAL (INT)", "Key": "PK", "Nullable": "No", "Description": "Unique pharmaceutical product identifier"},
        {"Attribute": "DrugName", "Type": "VARCHAR(150)", "Key": "-", "Nullable": "No", "Description": "Generic and brand formulation name"},
        {"Attribute": "Category", "Type": "VARCHAR(60)", "Key": "-", "Nullable": "Yes", "Description": "Pharmacological class (e.g., Analgesic, Antibiotic, Antimalarial)"},
        {"Attribute": "Manufacturer", "Type": "VARCHAR(100)", "Key": "-", "Nullable": "Yes", "Description": "Manufacturing pharmaceutical company"},
        {"Attribute": "NDARegNo", "Type": "VARCHAR(40)", "Key": "-", "Nullable": "Yes", "Description": "National Drug Authority compliance registration code"},
        {"Attribute": "UnitPrice", "Type": "DECIMAL(10,2)", "Key": "-", "Nullable": "No", "Description": "Standard unit retail selling price in UGX"},
        {"Attribute": "ReorderLevel", "Type": "INT", "Key": "-", "Nullable": "No", "Description": "Inventory threshold that triggers a restock alert"},
    ],
    "StockBatch": [
        {"Attribute": "BatchID", "Type": "SERIAL (INT)", "Key": "PK", "Nullable": "No", "Description": "Unique batch/lot delivery identifier"},
        {"Attribute": "DrugID", "Type": "INT", "Key": "FK", "Nullable": "No", "Description": "References Drug(DrugID)"},
        {"Attribute": "SupplierID", "Type": "INT", "Key": "FK", "Nullable": "Yes", "Description": "References Supplier(SupplierID)"},
        {"Attribute": "BatchNumber", "Type": "VARCHAR(40)", "Key": "-", "Nullable": "No", "Description": "Manufacturer lot/batch code"},
        {"Attribute": "QuantityReceived", "Type": "INT", "Key": "-", "Nullable": "No", "Description": "Original quantity delivered into stock"},
        {"Attribute": "QuantityRemaining", "Type": "INT", "Key": "-", "Nullable": "No", "Description": "Running stock balance (decremented on sale)"},
        {"Attribute": "ExpiryDate", "Type": "DATE", "Key": "-", "Nullable": "No", "Description": "Manufacturer expiration date (drives FEFO alerts)"},
        {"Attribute": "DateReceived", "Type": "DATE", "Key": "-", "Nullable": "No", "Description": "Date inventory arrived at Sekarungi pharmacy"},
    ],
    "PurchaseOrder": [
        {"Attribute": "POID", "Type": "SERIAL (INT)", "Key": "PK", "Nullable": "No", "Description": "Unique purchase order identifier"},
        {"Attribute": "SupplierID", "Type": "INT", "Key": "FK", "Nullable": "Yes", "Description": "References Supplier(SupplierID)"},
        {"Attribute": "CreatedByUserID", "Type": "INT", "Key": "FK", "Nullable": "Yes", "Description": "References User(UserID) who raised the order"},
        {"Attribute": "OrderDate", "Type": "DATE", "Key": "-", "Nullable": "No", "Description": "Date order was placed with supplier"},
        {"Attribute": "Status", "Type": "VARCHAR(20)", "Key": "CHECK", "Nullable": "Yes", "Description": "Order status: Pending, Received, Cancelled"},
    ],
    "PurchaseOrderItem": [
        {"Attribute": "POItemID", "Type": "SERIAL (INT)", "Key": "PK", "Nullable": "No", "Description": "Unique line item identifier"},
        {"Attribute": "POID", "Type": "INT", "Key": "FK", "Nullable": "No", "Description": "Identifying reference to owning PurchaseOrder(POID)"},
        {"Attribute": "DrugID", "Type": "INT", "Key": "FK", "Nullable": "No", "Description": "References Drug(DrugID)"},
        {"Attribute": "QuantityOrdered", "Type": "INT", "Key": "-", "Nullable": "No", "Description": "Quantity of units ordered"},
        {"Attribute": "UnitCost", "Type": "DECIMAL(10,2)", "Key": "-", "Nullable": "No", "Description": "Agreed wholesale purchase cost per unit (UGX)"},
    ],
    "Sale": [
        {"Attribute": "SaleID", "Type": "SERIAL (INT)", "Key": "PK", "Nullable": "No", "Description": "Unique receipt transaction identifier"},
        {"Attribute": "CashierUserID", "Type": "INT", "Key": "FK", "Nullable": "Yes", "Description": "References User(UserID) who processed the checkout"},
        {"Attribute": "ReceiptNumber", "Type": "VARCHAR(30)", "Key": "UNIQUE", "Nullable": "No", "Description": "Customer printed receipt number"},
        {"Attribute": "CustomerName", "Type": "VARCHAR(100)", "Key": "-", "Nullable": "Yes", "Description": "Customer full name or 'Walk-in Customer'"},
        {"Attribute": "SaleDate", "Type": "TIMESTAMP", "Key": "-", "Nullable": "No", "Description": "Transaction date and time timestamp"},
        {"Attribute": "SubTotal", "Type": "DECIMAL(10,2)", "Key": "-", "Nullable": "No", "Description": "Sale total before tax in UGX"},
        {"Attribute": "VATAmount", "Type": "DECIMAL(10,2)", "Key": "-", "Nullable": "No", "Description": "18% URA-compliant Value Added Tax"},
        {"Attribute": "TotalAmount", "Type": "DECIMAL(10,2)", "Key": "-", "Nullable": "No", "Description": "Gross total amount paid in UGX"},
        {"Attribute": "PaymentType", "Type": "VARCHAR(20)", "Key": "CHECK", "Nullable": "Yes", "Description": "Method: Cash, MobileMoney, Card"},
    ],
    "SaleItem": [
        {"Attribute": "SaleItemID", "Type": "SERIAL (INT)", "Key": "PK", "Nullable": "No", "Description": "Unique sale line item identifier"},
        {"Attribute": "SaleID", "Type": "INT", "Key": "FK", "Nullable": "No", "Description": "Identifying reference to owning Sale(SaleID)"},
        {"Attribute": "BatchID", "Type": "INT", "Key": "FK", "Nullable": "Yes", "Description": "References specific StockBatch dispensed from"},
        {"Attribute": "Quantity", "Type": "INT", "Key": "-", "Nullable": "No", "Description": "Number of units dispensed"},
        {"Attribute": "UnitPrice", "Type": "DECIMAL(10,2)", "Key": "-", "Nullable": "No", "Description": "Selling price per unit at transaction time"},
        {"Attribute": "LineTotal", "Type": "DECIMAL(10,2)", "Key": "-", "Nullable": "No", "Description": "Computed line sum: Quantity * UnitPrice"},
    ],
    "DispensingRegister": [
        {"Attribute": "RegisterID", "Type": "SERIAL (INT)", "Key": "PK", "Nullable": "No", "Description": "Unique regulatory register entry"},
        {"Attribute": "SaleItemID", "Type": "INT", "Key": "FK, UNIQUE", "Nullable": "No", "Description": "1:1 identifying reference to SaleItem(SaleItemID)"},
        {"Attribute": "DispensedByUserID", "Type": "INT", "Key": "FK", "Nullable": "Yes", "Description": "References User(UserID) licensed Pharmacist/Dispenser"},
        {"Attribute": "DateDispensed", "Type": "TIMESTAMP", "Key": "-", "Nullable": "No", "Description": "Timestamp of physical medication handover"},
        {"Attribute": "PrescriptionRef", "Type": "VARCHAR(100)", "Key": "-", "Nullable": "Yes", "Description": "Doctor's prescription number (NDA audit requirement)"},
    ],
    "Expense": [
        {"Attribute": "ExpenseID", "Type": "SERIAL (INT)", "Key": "PK", "Nullable": "No", "Description": "Unique operating expenditure record"},
        {"Attribute": "RecordedByUserID", "Type": "INT", "Key": "FK", "Nullable": "Yes", "Description": "References User(UserID) who logged the expense"},
        {"Attribute": "Category", "Type": "VARCHAR(100)", "Key": "-", "Nullable": "No", "Description": "Classification: Rent, Utilities, Transport, Security, etc."},
        {"Attribute": "Description", "Type": "TEXT", "Key": "-", "Nullable": "Yes", "Description": "Full narrative description of the expenditure"},
        {"Attribute": "Amount", "Type": "DECIMAL(12,2)", "Key": "-", "Nullable": "No", "Description": "Expenditure amount in UGX"},
        {"Attribute": "ExpenseDate", "Type": "DATE", "Key": "-", "Nullable": "No", "Description": "Date expense was incurred"},
    ],
    "Payroll": [
        {"Attribute": "PayrollID", "Type": "SERIAL (INT)", "Key": "PK", "Nullable": "No", "Description": "Unique staff compensation record"},
        {"Attribute": "StaffUserID", "Type": "INT", "Key": "FK", "Nullable": "No", "Description": "References User(UserID) staff recipient"},
        {"Attribute": "RecordedByUserID", "Type": "INT", "Key": "FK", "Nullable": "Yes", "Description": "References User(UserID) manager who authorized payment"},
        {"Attribute": "Amount", "Type": "DECIMAL(12,2)", "Key": "-", "Nullable": "No", "Description": "Payment value in UGX"},
        {"Attribute": "PaymentDate", "Type": "DATE", "Key": "-", "Nullable": "No", "Description": "Date disbursement was made"},
        {"Attribute": "PaymentType", "Type": "VARCHAR(20)", "Key": "CHECK", "Nullable": "Yes", "Description": "Type: Salary, Advance, Bonus"},
    ],
}


def render_schema_viewer():
    st.title("🗄️ Database Architecture & Data Dictionary")
    st.markdown("Comprehensive relational model design for **Sekarungi Pharmaceuticals Ltd (PIMS)**.")

    col_header, col_theme = st.columns([3, 2])
    with col_header:
        st.caption("Inspect the conceptual and physical database schema architecture.")
    with col_theme:
        canvas_theme = st.radio(
            "Canvas Theme:",
            ["🌙 Dark Slate (Matches UI)", "☀️ Clean Light Canvas"],
            horizontal=True,
            index=0,
            key="canvas_theme_choice"
        )

    is_dark = (canvas_theme == "🌙 Dark Slate (Matches UI)")
    bg_color = "#0f172a" if is_dark else "#ffffff"
    border_color = "#334155" if is_dark else "#e2e8f0"

    tab_erd, tab_dict, tab_uml = st.tabs(["🖼️ Entity-Relationship Diagram (ERD)", "📖 Data Dictionary", "📐 UML Class Diagram"])

    with tab_erd:
        st.subheader("PIMS Entity-Relationship Diagram (Crow's Foot Notation)")
        st.caption("Visualizing strong and weak entities, 1:M relationships, and associative resolving tables.")
        
        erd_filename = "pims_erd_dark.svg" if is_dark else "pims_erd.svg"
        erd_svg_path = os.path.join(ASSETS_DIR, erd_filename)
        if not os.path.exists(erd_svg_path):
            erd_svg_path = os.path.join(ASSETS_DIR, "pims_erd.svg")

        if os.path.exists(erd_svg_path):
            with open(erd_svg_path, "r", encoding="utf-8") as f:
                svg_content = f.read()
            st.markdown(
                f'<div style="background-color: {bg_color}; padding: 20px; border-radius: 8px; border: 1px solid {border_color}; overflow-x: auto;">'
                f'{svg_content}'
                f'</div>',
                unsafe_allow_html=True
            )
            with open(erd_svg_path, "rb") as file:
                st.download_button(
                    label=f"⬇️ Download Full ERD ({'Dark' if is_dark else 'Light'} SVG)",
                    data=file,
                    file_name=f"PIMS-ERD-{'dark' if is_dark else 'light'}.svg",
                    mime="image/svg+xml"
                )
        else:
            st.warning("ERD diagram asset not found at assets/pims_erd.svg")

    with tab_dict:
        st.subheader("Data Dictionary (11 Entities)")
        st.caption("Formal dictionary of all entities, primary/foreign keys, types, and constraints.")

        col1, col2 = st.columns([2, 3])
        with col1:
            selected_table = st.selectbox("Select Entity to Inspect:", list(DATA_DICTIONARY.keys()))
        with col2:
            search_query = st.text_input("🔍 Search attribute or description across all tables:", "")

        if search_query:
            st.markdown(f"**Search Results matching '{search_query}':**")
            results = []
            for tbl, rows in DATA_DICTIONARY.items():
                for r in rows:
                    if (search_query.lower() in r["Attribute"].lower() or 
                        search_query.lower() in r["Description"].lower() or
                        search_query.lower() in r["Type"].lower()):
                        r_copy = r.copy()
                        r_copy["Entity"] = tbl
                        results.append(r_copy)
            if results:
                st.dataframe(pd.DataFrame(results)[["Entity", "Attribute", "Type", "Key", "Nullable", "Description"]], use_container_width=True)
            else:
                st.info("No matching attributes found.")
        else:
            rows = DATA_DICTIONARY[selected_table]
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.markdown(f"**Total Attributes:** `{len(df)}` | **Entity Type:** `{'Weak Entity' if selected_table in ['SaleItem', 'PurchaseOrderItem', 'DispensingRegister'] else 'Strong Entity'}`")

    with tab_uml:
        st.subheader("PIMS UML Domain Class Diagram")
        st.caption("Domain object model representing entity attributes, data visibility, and associations.")

        uml_filename = "pims_uml_dark.svg" if is_dark else "pims_uml.svg"
        uml_svg_path = os.path.join(ASSETS_DIR, uml_filename)
        if not os.path.exists(uml_svg_path):
            uml_svg_path = os.path.join(ASSETS_DIR, "pims_uml.svg")

        if os.path.exists(uml_svg_path):
            with open(uml_svg_path, "r", encoding="utf-8") as f:
                uml_svg_content = f.read()
            st.markdown(
                f'<div style="background-color: {bg_color}; padding: 20px; border-radius: 8px; border: 1px solid {border_color}; overflow-x: auto;">'
                f'{uml_svg_content}'
                f'</div>',
                unsafe_allow_html=True
            )
            with open(uml_svg_path, "rb") as file:
                st.download_button(
                    label=f"⬇️ Download Full UML ({'Dark' if is_dark else 'Light'} SVG)",
                    data=file,
                    file_name=f"PIMS-UML-{'dark' if is_dark else 'light'}.svg",
                    mime="image/svg+xml"
                )
        else:
            uml_png_path = os.path.join(ASSETS_DIR, "pims_uml.png")
            if os.path.exists(uml_png_path):
                st.image(uml_png_path, caption="PIMS Domain Model UML Class Diagram", use_container_width=True)
            else:
                st.info("UML diagram asset not found.")
