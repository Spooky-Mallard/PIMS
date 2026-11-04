"""Data Entry Forms Module for PIMS
Sectioned, user-friendly forms for inserting records into Neon PostgreSQL.
"""

import datetime
import streamlit as st
import pandas as pd
from backend.db import fetch_dataframe, execute_statement, get_db_connection


def render_forms():
    st.title("📝 Data Entry & Transaction Forms")
    st.caption("Clean, sectioned inputs for adding new entities and recording transactions.")

    form_type = st.radio(
        "Choose Form to Complete:",
        [
            "💊 Add New Drug",
            "📦 Receive Stock Batch",
            "🛒 Point of Sale & Dispense (POS)",
            "💸 Record Operating Expense",
            "👤 Register Staff Member",
        ],
        horizontal=True
    )

    st.markdown("---")

    # -------------------------------------------------------------
    # 1. ADD NEW DRUG
    # -------------------------------------------------------------
    if form_type == "💊 Add New Drug":
        st.subheader("New Drug Registration")
        st.caption("Step-by-step product catalog entry.")

        with st.form("form_add_drug", clear_on_submit=True):
            st.markdown("#### 1. Identification & Classification")
            c1, c2 = st.columns(2)
            with c1:
                drug_name = st.text_input("Drug Brand & Generic Name *", placeholder="e.g. Cefixime 200mg")
            with c2:
                category = st.selectbox(
                    "Pharmacological Category",
                    ["Antibiotic", "Analgesic", "Antimalarial", "Anti-inflammatory", "Antidiabetic", "Antihypertensive", "Antacid", "Antihistamine", "Supplement", "Other"]
                )

            st.markdown("#### 2. Regulatory & Manufacturer Information")
            c3, c4 = st.columns(2)
            with c3:
                manufacturer = st.text_input("Manufacturer *", placeholder="e.g. Cipla Quality Chemical")
            with c4:
                nda_reg_no = st.text_input("NDA Registration Number *", placeholder="e.g. NDA/UG/2026/045")

            st.markdown("#### 3. Commercial & Inventory Thresholds")
            c5, c6 = st.columns(2)
            with c5:
                unit_price = st.number_input("Standard Selling Price (UGX) *", min_value=100.0, step=500.0, value=2500.0)
            with c6:
                reorder_level = st.number_input("Low Stock Reorder Threshold (Units) *", min_value=5, step=10, value=50)

            submitted = st.form_submit_button("💾 Save New Drug to Database", use_container_width=True)
            if submitted:
                if not drug_name or not manufacturer or not nda_reg_no:
                    st.error("Please fill in all required fields (Drug Name, Manufacturer, and NDA Number).")
                else:
                    sql = """
                    INSERT INTO Drug (DrugName, Category, Manufacturer, NDARegNo, UnitPrice, ReorderLevel)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    ok, msg, new_id = execute_statement(sql, (drug_name, category, manufacturer, nda_reg_no, unit_price, reorder_level), return_id_column="DrugID")
                    if ok:
                        st.success(f"✅ Successfully registered drug **{drug_name}** with **DrugID #{new_id}**!")
                    else:
                        st.error(f"Failed to insert record: {msg}")

    # -------------------------------------------------------------
    # 2. RECEIVE STOCK BATCH
    # -------------------------------------------------------------
    elif form_type == "📦 Receive Stock Batch":
        st.subheader("Receive Inventory Batch")
        st.caption("Record new incoming medicine deliveries into pharmacy stock.")

        # Fetch drugs and suppliers for dropdowns
        try:
            drugs_df = fetch_dataframe("SELECT DrugID, DrugName, Category FROM Drug ORDER BY DrugName;")
            suppliers_df = fetch_dataframe("SELECT SupplierID, CompanyName FROM Supplier ORDER BY CompanyName;")
        except Exception as e:
            st.error(f"Error loading dependencies: {e}")
            return

        if drugs_df.empty or suppliers_df.empty:
            st.warning("Please ensure there is at least one Drug and one Supplier before recording batches.")
            return

        with st.form("form_add_batch", clear_on_submit=True):
            st.markdown("#### 1. Product & Supplier Selection")
            c1, c2 = st.columns(2)
            with c1:
                drug_options = {f"{r['drugname']} (ID: {r['drugid']})": r['drugid'] for _, r in drugs_df.iterrows()}
                selected_drug_label = st.selectbox("Select Drug Product *", list(drug_options.keys()))
                drug_id = drug_options[selected_drug_label]
            with c2:
                supplier_options = {f"{r['companyname']} (ID: {r['supplierid']})": r['supplierid'] for _, r in suppliers_df.iterrows()}
                selected_supplier_label = st.selectbox("Delivering Supplier *", list(supplier_options.keys()))
                supplier_id = supplier_options[selected_supplier_label]

            st.markdown("#### 2. Batch Number & Quantities")
            c3, c4 = st.columns(2)
            with c3:
                batch_number = st.text_input("Manufacturer Batch / Lot Number *", placeholder="e.g. BATCH-2026-X8")
            with c4:
                qty_received = st.number_input("Quantity Received (Packs/Units) *", min_value=1, step=50, value=200)

            st.markdown("#### 3. Dates & Quality Control")
            c5, c6 = st.columns(2)
            with c5:
                date_received = st.date_input("Date Received", value=datetime.date.today())
            with c6:
                expiry_date = st.date_input("Expiry Date *", value=datetime.date.today() + datetime.timedelta(days=730))

            submitted = st.form_submit_button("📦 Commit Batch to Inventory", use_container_width=True)
            if submitted:
                if not batch_number:
                    st.error("Batch Number is mandatory.")
                elif expiry_date <= date_received:
                    st.error("Expiry Date must be in the future relative to delivery date.")
                else:
                    sql = """
                    INSERT INTO StockBatch (DrugID, SupplierID, BatchNumber, QuantityReceived, QuantityRemaining, ExpiryDate, DateReceived)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    ok, msg, new_id = execute_statement(sql, (drug_id, supplier_id, batch_number, qty_received, qty_received, expiry_date, date_received), return_id_column="BatchID")
                    if ok:
                        st.success(f"✅ Stock Batch **{batch_number}** recorded successfully (BatchID #{new_id})!")
                    else:
                        st.error(f"Error saving batch: {msg}")

    # -------------------------------------------------------------
    # 3. POINT OF SALE & DISPENSE (POS)
    # -------------------------------------------------------------
    elif form_type == "🛒 Point of Sale & Dispense (POS)":
        st.subheader("Point of Sale & Medication Dispensing")
        st.caption("Dispense medicine to customer, compute VAT, and record regulatory register.")

        try:
            users_df = fetch_dataframe('SELECT UserID, FullName, Role FROM "User" WHERE Status = \'Active\' ORDER BY FullName;')
            batches_df = fetch_dataframe("""
                SELECT sb.BatchID, sb.BatchNumber, sb.QuantityRemaining, sb.ExpiryDate,
                       d.DrugName, d.UnitPrice, d.Category
                FROM StockBatch sb
                JOIN Drug d ON d.DrugID = sb.DrugID
                WHERE sb.QuantityRemaining > 0 AND sb.ExpiryDate > CURRENT_DATE
                ORDER BY sb.ExpiryDate ASC;
            """)
        except Exception as e:
            st.error(f"Database error: {e}")
            return

        if batches_df.empty:
            st.warning("No active stock available in the pharmacy. Please receive a batch first.")
            return

        # Interactive selection outside form for dynamic pricing calculation
        st.markdown("#### 1. Sale Information")
        c1, c2, c3 = st.columns(3)
        with c1:
            cashier_options = {f"{r['fullname']} ({r['role']})": r['userid'] for _, r in users_df.iterrows()}
            selected_cashier = st.selectbox("Cashier On Duty *", list(cashier_options.keys()))
            cashier_id = cashier_options[selected_cashier]
        with c2:
            customer_name = st.text_input("Customer Name", value="Walk-in Customer")
        with c3:
            payment_type = st.selectbox("Payment Method", ["Cash", "MobileMoney", "Card"])

        st.markdown("#### 2. Select Medication & Quantity")
        c4, c5 = st.columns([3, 1])
        with c4:
            batch_dict = {}
            for _, b in batches_df.iterrows():
                label = f"{b['drugname']} | Lot: {b['batchnumber']} (Avail: {b['quantityremaining']} | Exp: {b['expirydate']}) — UGX {float(b['unitprice']):,.0f}"
                batch_dict[label] = b
            selected_batch_label = st.selectbox("Select Medication Batch (FEFO Sorted) *", list(batch_dict.keys()))
            chosen_batch = batch_dict[selected_batch_label]
        with c5:
            max_qty = int(chosen_batch['quantityremaining'])
            quantity = st.number_input("Quantity to Buy *", min_value=1, max_value=max_qty, value=min(5, max_qty))

        # Dynamic Pricing Calculation
        unit_price = float(chosen_batch['unitprice'])
        subtotal = round(unit_price * quantity, 2)
        vat_amount = round(subtotal * 0.18, 2)  # 18% standard VAT
        total_amount = round(subtotal + vat_amount, 2)

        st.info(f"💰 **SubTotal:** UGX {subtotal:,.2f} | **VAT (18%):** UGX {vat_amount:,.2f} | **Total Amount Payable:** **UGX {total_amount:,.2f}**")

        st.markdown("#### 3. Clinical Dispensing & Regulatory Compliance")
        c6, c7 = st.columns(2)
        with c6:
            dispensers = users_df[users_df['role'].isin(['Pharmacist', 'Dispenser'])]
            dispenser_options = {f"{r['fullname']} ({r['role']})": r['userid'] for _, r in (dispensers if not dispensers.empty else users_df).iterrows()}
            selected_dispenser = st.selectbox("Dispensing Officer *", list(dispenser_options.keys()))
            dispenser_id = dispenser_options[selected_dispenser]
        with c7:
            prescription_ref = st.text_input("Doctor Prescription Reference (Optional)", placeholder="e.g. RX-2026-0412")

        if st.button("💳 Process Transaction & Dispense Medication", use_container_width=True, type="primary"):
            conn = get_db_connection()
            try:
                cur = conn.cursor()
                receipt_no = f"RCPT-{int(datetime.datetime.now().timestamp())}"
                
                # 1. Insert Sale
                cur.execute("""
                    INSERT INTO Sale (CashierUserID, ReceiptNumber, CustomerName, SaleDate, SubTotal, VATAmount, TotalAmount, PaymentType)
                    VALUES (%s, %s, %s, NOW(), %s, %s, %s, %s)
                    RETURNING SaleID;
                """, (cashier_id, receipt_no, customer_name, subtotal, vat_amount, total_amount, payment_type))
                new_sale_id = cur.fetchone()[0]

                # 2. Insert SaleItem
                cur.execute("""
                    INSERT INTO SaleItem (SaleID, BatchID, Quantity, UnitPrice, LineTotal)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING SaleItemID;
                """, (new_sale_id, int(chosen_batch['batchid']), quantity, unit_price, subtotal))
                new_sale_item_id = cur.fetchone()[0]

                # 3. Insert DispensingRegister
                cur.execute("""
                    INSERT INTO DispensingRegister (SaleItemID, DispensedByUserID, DateDispensed, PrescriptionRef)
                    VALUES (%s, %s, NOW(), %s);
                """, (new_sale_item_id, dispenser_id, prescription_ref if prescription_ref else None))

                # 4. Decrement Stock Remaining
                cur.execute("""
                    UPDATE StockBatch 
                    SET QuantityRemaining = QuantityRemaining - %s
                    WHERE BatchID = %s;
                """, (quantity, int(chosen_batch['batchid'])))

                conn.commit()
                cur.close()
                st.success(f"🎉 Sale recorded successfully! Receipt: **{receipt_no}** | Amount: **UGX {total_amount:,.2f}** | Stock balance updated.")
            except Exception as e:
                conn.rollback()
                st.error(f"Transaction failed and was rolled back: {e}")
            finally:
                conn.close()

    # -------------------------------------------------------------
    # 4. RECORD OPERATING EXPENSE
    # -------------------------------------------------------------
    elif form_type == "💸 Record Operating Expense":
        st.subheader("Record Operating Expenditure")
        st.caption("Capture pharmacy operating expenses (Rent, Utilities, Transport, etc.).")

        try:
            users_df = fetch_dataframe('SELECT UserID, FullName FROM "User" WHERE Status = \'Active\' ORDER BY FullName;')
        except Exception as e:
            st.error(f"Database error: {e}")
            return

        with st.form("form_add_expense", clear_on_submit=True):
            st.markdown("#### 1. Categorization & Staff")
            c1, c2 = st.columns(2)
            with c1:
                category = st.selectbox("Expense Category *", ["Rent", "Utilities", "Transport", "Security", "Internet", "Maintenance", "Packaging", "Supplies", "Other"])
            with c2:
                user_options = {r['fullname']: r['userid'] for _, r in users_df.iterrows()}
                recorded_user = st.selectbox("Staff Logging Expense *", list(user_options.keys()))
                user_id = user_options[recorded_user]

            st.markdown("#### 2. Amount & Timeline")
            c3, c4 = st.columns(2)
            with c3:
                amount = st.number_input("Amount (UGX) *", min_value=1000.0, step=50000.0, value=150000.0)
            with c4:
                expense_date = st.date_input("Date Incurred *", value=datetime.date.today())

            st.markdown("#### 3. Expense Description & Voucher")
            description = st.text_area("Detailed Description *", placeholder="e.g. October monthly electricity payment to Umeme")

            submitted = st.form_submit_button("💸 Save Expense Record", use_container_width=True)
            if submitted:
                if not description:
                    st.error("Please provide a description for audit purposes.")
                else:
                    sql = """
                    INSERT INTO Expense (RecordedByUserID, Category, Description, Amount, ExpenseDate)
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    ok, msg, new_id = execute_statement(sql, (user_id, category, description, amount, expense_date), return_id_column="ExpenseID")
                    if ok:
                        st.success(f"✅ Expense of **UGX {amount:,.2f}** under **{category}** recorded (ExpenseID #{new_id})!")
                    else:
                        st.error(f"Error saving expense: {msg}")

    # -------------------------------------------------------------
    # 5. REGISTER STAFF MEMBER
    # -------------------------------------------------------------
    elif form_type == "👤 Register Staff Member":
        st.subheader("Staff Member Onboarding")
        st.caption("Create a new employee profile with role and system access.")

        with st.form("form_add_user", clear_on_submit=True):
            st.markdown("#### 1. Personal Identifiers")
            c1, c2 = st.columns(2)
            with c1:
                full_name = st.text_input("Staff Full Name *", placeholder="e.g. Dr. Kigozi Ronald")
            with c2:
                phone = st.text_input("Phone Number *", placeholder="e.g. +256701234567")

            st.markdown("#### 2. System Credentials")
            c3, c4 = st.columns(2)
            with c3:
                username = st.text_input("Unique Username *", placeholder="e.g. rkigozi")
            with c4:
                temp_password = st.text_input("Temporary Password *", type="password", placeholder="Minimum 6 characters")

            st.markdown("#### 3. Departmental Role & Access")
            c5, c6 = st.columns(2)
            with c5:
                role = st.selectbox("System Role *", ["Pharmacist", "Dispenser", "Cashier", "OperationsManager", "Director"])
            with c6:
                status = st.selectbox("Account Status", ["Active", "Inactive"])

            submitted = st.form_submit_button("👤 Register Staff Member", use_container_width=True)
            if submitted:
                if not full_name or not username or not temp_password:
                    st.error("Full Name, Username, and Password are mandatory.")
                else:
                    # In a production system we use passlib/hashlib
                    pwd_hash = f"pbkdf2:sha256:1000${username}_hash"
                    sql = """
                    INSERT INTO "User" (FullName, Username, PasswordHash, Role, Phone, Status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    ok, msg, new_id = execute_statement(sql, (full_name, username, pwd_hash, role, phone, status), return_id_column="UserID")
                    if ok:
                        st.success(f"✅ Staff member **{full_name}** registered successfully as **{role}** (UserID #{new_id})!")
                    else:
                        st.error(f"Error registering user: {msg}")
