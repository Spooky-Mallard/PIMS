"""PIMS Database Initializer & Coordinated Data Seeder
Sekarungi Pharmaceuticals Ltd
Connects to Neon PostgreSQL and sets up all 11 tables, 4 views, and realistic coordinated sample data.
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load env from DBMS-PROJECT/.env
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in .env")
    sys.exit(1)


def init_database():
    print(f"Connecting to Neon PostgreSQL...")
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cur = conn.cursor()

    print("Dropping existing tables and views in reverse dependency order...")
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

    print("Creating 11 core tables...")
    cur.execute("""
    -- 1. USER TABLE
    CREATE TABLE "User" (
        UserID SERIAL PRIMARY KEY,
        FullName VARCHAR(100) NOT NULL,
        Username VARCHAR(50) UNIQUE NOT NULL,
        PasswordHash VARCHAR(255) NOT NULL,
        Role VARCHAR(20) CHECK (Role IN ('Director', 'OperationsManager', 'Pharmacist', 'Cashier', 'Dispenser')),
        Phone VARCHAR(20),
        Status VARCHAR(10) CHECK (Status IN ('Active', 'Inactive'))
    );

    -- 2. SUPPLIER TABLE
    CREATE TABLE Supplier (
        SupplierID SERIAL PRIMARY KEY,
        CompanyName VARCHAR(120) NOT NULL,
        ContactPerson VARCHAR(100),
        Phone VARCHAR(20),
        Email VARCHAR(100),
        Address VARCHAR(200)
    );

    -- 3. DRUG TABLE
    CREATE TABLE Drug (
        DrugID SERIAL PRIMARY KEY,
        DrugName VARCHAR(150) NOT NULL,
        Category VARCHAR(60),
        Manufacturer VARCHAR(100),
        NDARegNo VARCHAR(40),
        UnitPrice DECIMAL(10, 2) NOT NULL,
        ReorderLevel INT NOT NULL
    );

    -- 4. STOCKBATCH TABLE
    CREATE TABLE StockBatch (
        BatchID SERIAL PRIMARY KEY,
        DrugID INT REFERENCES Drug(DrugID) ON DELETE CASCADE,
        SupplierID INT REFERENCES Supplier(SupplierID) ON DELETE SET NULL,
        BatchNumber VARCHAR(40) NOT NULL,
        QuantityReceived INT NOT NULL,
        QuantityRemaining INT NOT NULL,
        ExpiryDate DATE NOT NULL,
        DateReceived DATE NOT NULL
    );

    -- 5. PURCHASEORDER TABLE
    CREATE TABLE PurchaseOrder (
        POID SERIAL PRIMARY KEY,
        SupplierID INT REFERENCES Supplier(SupplierID) ON DELETE SET NULL,
        CreatedByUserID INT REFERENCES "User"(UserID) ON DELETE SET NULL,
        OrderDate DATE NOT NULL,
        Status VARCHAR(20) CHECK (Status IN ('Pending', 'Received', 'Cancelled'))
    );

    -- 6. PURCHASEORDERITEM TABLE
    CREATE TABLE PurchaseOrderItem (
        POItemID SERIAL PRIMARY KEY,
        POID INT REFERENCES PurchaseOrder(POID) ON DELETE CASCADE,
        DrugID INT REFERENCES Drug(DrugID) ON DELETE CASCADE,
        QuantityOrdered INT NOT NULL,
        UnitCost DECIMAL(10, 2) NOT NULL
    );

    -- 7. SALE TABLE
    CREATE TABLE Sale (
        SaleID SERIAL PRIMARY KEY,
        CashierUserID INT REFERENCES "User"(UserID) ON DELETE SET NULL,
        ReceiptNumber VARCHAR(30) UNIQUE NOT NULL,
        CustomerName VARCHAR(100),
        SaleDate TIMESTAMP NOT NULL,
        SubTotal DECIMAL(10, 2) NOT NULL,
        VATAmount DECIMAL(10, 2) NOT NULL,
        TotalAmount DECIMAL(10, 2) NOT NULL,
        PaymentType VARCHAR(20) CHECK (PaymentType IN ('Cash', 'MobileMoney', 'Card'))
    );

    -- 8. SALEITEM TABLE
    CREATE TABLE SaleItem (
        SaleItemID SERIAL PRIMARY KEY,
        SaleID INT REFERENCES Sale(SaleID) ON DELETE CASCADE,
        BatchID INT REFERENCES StockBatch(BatchID) ON DELETE SET NULL,
        Quantity INT NOT NULL,
        UnitPrice DECIMAL(10, 2) NOT NULL,
        LineTotal DECIMAL(10, 2) NOT NULL
    );

    -- 9. DISPENSINGREGISTER TABLE
    CREATE TABLE DispensingRegister (
        RegisterID SERIAL PRIMARY KEY,
        SaleItemID INT UNIQUE REFERENCES SaleItem(SaleItemID) ON DELETE CASCADE,
        DispensedByUserID INT REFERENCES "User"(UserID) ON DELETE SET NULL,
        DateDispensed TIMESTAMP NOT NULL,
        PrescriptionRef VARCHAR(100)
    );

    -- 10. EXPENSE TABLE
    CREATE TABLE Expense (
        ExpenseID SERIAL PRIMARY KEY,
        RecordedByUserID INT REFERENCES "User"(UserID) ON DELETE SET NULL,
        Category VARCHAR(100) NOT NULL,
        Description TEXT,
        Amount DECIMAL(12, 2) NOT NULL,
        ExpenseDate DATE NOT NULL
    );

    -- 11. PAYROLL TABLE
    CREATE TABLE Payroll (
        PayrollID SERIAL PRIMARY KEY,
        StaffUserID INT REFERENCES "User"(UserID) ON DELETE CASCADE,
        RecordedByUserID INT REFERENCES "User"(UserID) ON DELETE SET NULL,
        Amount DECIMAL(12, 2) NOT NULL,
        PaymentDate DATE NOT NULL,
        PaymentType VARCHAR(20) CHECK (PaymentType IN ('Salary', 'Advance', 'Bonus'))
    );
    """)

    print("Seeding coordinated sample data (Users, Suppliers, Drugs)...")
    cur.execute("""
    INSERT INTO "User" (FullName, Username, PasswordHash, Role, Phone, Status) VALUES 
    ('Sabano Zubedah', 'sabanoz', 'pbkdf2:sha256:1000$sec1', 'Pharmacist', '+256700000001', 'Active'),
    ('Mumbere Matthew', 'mumberem', 'pbkdf2:sha256:1000$sec2', 'Dispenser', '+256700000002', 'Active'),
    ('Alex Okello', 'alexo', 'pbkdf2:sha256:1000$sec3', 'Director', '+256700000003', 'Active'),
    ('Grace Akello', 'gracea', 'pbkdf2:sha256:1000$sec4', 'OperationsManager', '+256700000004', 'Active'),
    ('David Mukasa', 'davidm', 'pbkdf2:sha256:1000$sec5', 'Cashier', '+256700000005', 'Active'),
    ('Sarah Namubiru', 'sarahn', 'pbkdf2:sha256:1000$sec6', 'Pharmacist', '+256700000006', 'Active'),
    ('Brian Kintu', 'briank', 'pbkdf2:sha256:1000$sec7', 'Dispenser', '+256700000007', 'Inactive'),
    ('Joan Nsubuga', 'joann', 'pbkdf2:sha256:1000$sec8', 'Cashier', '+256700000008', 'Active'),
    ('Peter Kato', 'peterk', 'pbkdf2:sha256:1000$sec9', 'Pharmacist', '+256700000009', 'Active'),
    ('Lillian Achieng', 'lilliana', 'pbkdf2:sha256:1000$sec10', 'Dispenser', '+256700000010', 'Active');

    INSERT INTO Supplier (CompanyName, ContactPerson, Phone, Email, Address) VALUES 
    ('Pharma Supplies Ltd', 'John Doe', '+256701111111', 'contact@pharmasupplies.com', 'Kampala, Uganda'),
    ('Kigali Meds', 'Jane Smith', '+256702222222', 'sales@kigalimeds.rw', 'Kigali, Rwanda'),
    ('Abacus Pharma', 'Sanjay Patel', '+256703333333', 'info@abacuspharma.com', 'Kampala, Uganda'),
    ('Renal Remedies', 'David Ochieng', '+256704444444', 'orders@renalremedies.com', 'Entebbe, Uganda'),
    ('Quality Chemicals', 'Florence Babirye', '+256705555555', 'support@qcil.co.ug', 'Luzira, Uganda'),
    ('East Africa Pharmaceuticals', 'Michael Kironde', '+256706666666', 'sales@eapharma.com', 'Jinja, Uganda'),
    ('Universal Corporation', 'Anita Sharma', '+254707777777', 'contact@universalcorp.ke', 'Nairobi, Kenya'),
    ('Medreich Africa', 'Robert Kibuuka', '+256708888888', 'info@medreich.co.ug', 'Kampala, Uganda'),
    ('Laborex Uganda', 'Esther Nantongo', '+256709999999', 'orders@laborex.ug', 'Kampala, Uganda'),
    ('Cipla Quality Chemical', 'Emmanuel Kato', '+256710000008', 'sales@ciplaqcil.co.ug', 'Kampala, Uganda');

    INSERT INTO Drug (DrugName, Category, Manufacturer, NDARegNo, UnitPrice, ReorderLevel) VALUES 
    ('Paracetamol 500mg', 'Analgesic', 'Cipla', 'NDA/101', 500.00, 100),
    ('Amoxicillin 250mg', 'Antibiotic', 'GSK', 'NDA/102', 1200.00, 50),
    ('Ibuprofen 400mg', 'Anti-inflammatory', 'Abacus', 'NDA/103', 800.00, 80),
    ('Metformin 500mg', 'Antidiabetic', 'Sun Pharma', 'NDA/104', 1500.00, 60),
    ('Ciprofloxacin 500mg', 'Antibiotic', 'Laborex', 'NDA/105', 2500.00, 40),
    ('Omeprazole 20mg', 'Antacid', 'QCIL', 'NDA/106', 1800.00, 70),
    ('Cetirizine 10mg', 'Antihistamine', 'Medreich', 'NDA/107', 600.00, 120),
    ('Azithromycin 500mg', 'Antibiotic', 'Pfizer', 'NDA/108', 4500.00, 30),
    ('Amlodipine 5mg', 'Antihypertensive', 'Novartis', 'NDA/109', 2000.00, 50),
    ('Artemether/Lumefantrine', 'Antimalarial', 'QCIL', 'NDA/111', 5000.00, 150),
    ('Metronidazole 400mg', 'Antibiotic', 'Universal', 'NDA/112', 1000.00, 90),
    ('Salbutamol Inhaler', 'Bronchodilator', 'GSK', 'NDA/113', 12000.00, 20),
    ('Diclofenac Gel 1%', 'Analgesic', 'Novartis', 'NDA/118', 6500.00, 25),
    ('Vitamin C 500mg', 'Supplement', 'Abacus', 'NDA/120', 300.00, 300);
    """)

    print("Seeding Stock Batches & Purchase Orders...")
    cur.execute("""
    INSERT INTO StockBatch (DrugID, SupplierID, BatchNumber, QuantityReceived, QuantityRemaining, ExpiryDate, DateReceived) VALUES 
    (1, 1, 'BATCH-PCM-001', 1000, 850, '2028-05-30', '2025-08-15'),
    (1, 1, 'BATCH-PCM-002', 500, 40, '2026-11-20', '2025-05-10'), -- Expiring soon / low stock!
    (2, 2, 'BATCH-AMX-001', 400, 310, '2027-12-15', '2025-09-01'),
    (2, 2, 'BATCH-AMX-002', 200, 25, '2026-11-10', '2025-06-12'), -- Near expiry!
    (3, 3, 'BATCH-IBU-001', 600, 520, '2028-01-20', '2025-09-10'),
    (4, 4, 'BATCH-MET-001', 300, 240, '2027-08-15', '2025-07-22'),
    (5, 5, 'BATCH-CIP-001', 250, 190, '2027-04-30', '2025-08-01'),
    (6, 5, 'BATCH-OMP-001', 500, 380, '2028-03-10', '2025-08-18'),
    (7, 8, 'BATCH-CET-001', 800, 650, '2028-09-01', '2025-09-05'),
    (8, 9, 'BATCH-AZI-001', 150, 85, '2027-06-15', '2025-08-25'),
    (9, 10, 'BATCH-AML-001', 350, 290, '2027-11-01', '2025-07-15'),
    (10, 5, 'BATCH-ALU-001', 600, 110, '2027-03-25', '2025-08-30'), -- Below reorder level!
    (11, 7, 'BATCH-MTZ-001', 450, 360, '2027-10-10', '2025-09-12'),
    (12, 2, 'BATCH-SAL-001', 80, 45, '2027-01-15', '2025-06-20'),
    (13, 10, 'BATCH-DIC-001', 100, 75, '2027-07-20', '2025-08-10'),
    (14, 3, 'BATCH-VTC-001', 1200, 950, '2028-12-31', '2025-09-15');

    INSERT INTO PurchaseOrder (SupplierID, CreatedByUserID, OrderDate, Status) VALUES 
    (1, 1, '2025-08-01', 'Received'),
    (2, 4, '2025-08-10', 'Received'),
    (3, 1, '2025-08-20', 'Received'),
    (5, 4, '2025-09-05', 'Received'),
    (8, 1, '2025-09-15', 'Received'),
    (1, 4, '2025-10-01', 'Pending'),
    (5, 1, '2025-10-10', 'Pending'),
    (2, 4, '2025-10-12', 'Cancelled');

    INSERT INTO PurchaseOrderItem (POID, DrugID, QuantityOrdered, UnitCost) VALUES 
    (1, 1, 1000, 300.00),
    (1, 3, 600, 500.00),
    (2, 2, 400, 800.00),
    (2, 12, 80, 8500.00),
    (3, 4, 300, 950.00),
    (3, 14, 1200, 180.00),
    (4, 5, 250, 1600.00),
    (4, 6, 500, 1100.00),
    (5, 7, 800, 350.00),
    (6, 1, 500, 320.00),
    (7, 10, 400, 3200.00);
    """)

    print("Seeding Sales, SaleItems, and Dispensing Register...")
    cur.execute("""
    INSERT INTO Sale (CashierUserID, ReceiptNumber, CustomerName, SaleDate, SubTotal, VATAmount, TotalAmount, PaymentType) VALUES 
    (5, 'RCPT-1001', 'Walk-in Customer', '2025-09-01 10:15:00', 10000.00, 1800.00, 11800.00, 'Cash'),
    (8, 'RCPT-1002', 'Alice Mukasa',     '2025-09-02 11:30:00', 24000.00, 4320.00, 28320.00, 'MobileMoney'),
    (5, 'RCPT-1003', 'John Ssali',       '2025-09-03 14:00:00', 8000.00,  1440.00, 9440.00,  'Cash'),
    (8, 'RCPT-1004', 'Grace Nansubuga',  '2025-09-05 09:45:00', 15000.00, 2700.00, 17700.00, 'Card'),
    (5, 'RCPT-1005', 'Peter Owino',      '2025-09-08 12:20:00', 35000.00, 6300.00, 41300.00, 'MobileMoney'),
    (8, 'RCPT-1006', 'Walk-in Customer', '2025-09-10 15:10:00', 5000.00,  900.00,  5900.00,  'Cash'),
    (5, 'RCPT-1007', 'Mary Achieng',     '2025-09-12 16:30:00', 12000.00, 2160.00, 14160.00, 'Cash'),
    (8, 'RCPT-1008', 'Robert Tumwine',   '2025-09-15 10:05:00', 18000.00, 3240.00, 21240.00, 'Card'),
    (5, 'RCPT-1009', 'Sarah Nabirye',    '2025-09-18 11:50:00', 22000.00, 3960.00, 25960.00, 'MobileMoney'),
    (8, 'RCPT-1010', 'Michael Odongo',   '2025-09-22 13:40:00', 9500.00,  1710.00, 11210.00, 'Cash'),
    (5, 'RCPT-1011', 'Esther Nakimuli',  '2025-10-01 09:20:00', 14000.00, 2520.00, 16520.00, 'Cash'),
    (8, 'RCPT-1012', 'Walk-in Customer', '2025-10-02 10:45:00', 6000.00,  1080.00, 7080.00,  'Cash'),
    (5, 'RCPT-1013', 'David Kiwanuka',   '2025-10-04 11:15:00', 25000.00, 4500.00, 29500.00, 'MobileMoney'),
    (8, 'RCPT-1014', 'Florence Among',   '2025-10-06 14:30:00', 36000.00, 6480.00, 42480.00, 'Card'),
    (5, 'RCPT-1015', 'James Okello',     '2025-10-08 15:50:00', 16500.00, 2970.00, 19470.00, 'Cash'),
    (8, 'RCPT-1016', 'Walk-in Customer', '2025-10-10 10:10:00', 7200.00,  1296.00, 8496.00,  'MobileMoney'),
    (5, 'RCPT-1017', 'Ruth Nambi',       '2025-10-12 12:00:00', 28000.00, 5040.00, 33040.00, 'Card'),
    (8, 'RCPT-1018', 'Samuel Mugisha',   '2025-10-15 14:15:00', 19000.00, 3420.00, 22420.00, 'Cash'),
    (5, 'RCPT-1019', 'Walk-in Customer', '2025-10-18 16:40:00', 4500.00,  810.00,  5310.00,  'MobileMoney'),
    (8, 'RCPT-1020', 'Grace Nansubuga',  '2025-10-20 17:00:00', 30000.00, 5400.00, 35400.00, 'Card');

    INSERT INTO SaleItem (SaleID, BatchID, Quantity, UnitPrice, LineTotal) VALUES 
    (1, 1, 20, 500.00, 10000.00),
    (2, 3, 20, 1200.00, 24000.00),
    (3, 5, 10, 800.00, 8000.00),
    (4, 4, 10, 1500.00, 15000.00),
    (5, 10, 7, 5000.00, 35000.00),
    (6, 1, 10, 500.00, 5000.00),
    (7, 3, 10, 1200.00, 12000.00),
    (8, 7, 30, 600.00, 18000.00),
    (9, 6, 12, 1800.00, 21600.00),
    (10, 11, 8, 1000.00, 8000.00),
    (11, 1, 28, 500.00, 14000.00),
    (12, 7, 10, 600.00, 6000.00),
    (13, 8, 5, 4500.00, 22500.00),
    (14, 12, 3, 12000.00, 36000.00),
    (15, 3, 10, 1200.00, 12000.00),
    (16, 5, 9, 800.00, 7200.00),
    (17, 10, 5, 5000.00, 25000.00),
    (18, 9, 8, 2000.00, 16000.00),
    (19, 14, 15, 300.00, 4500.00),
    (20, 13, 4, 6500.00, 26000.00);

    INSERT INTO DispensingRegister (SaleItemID, DispensedByUserID, DateDispensed, PrescriptionRef) VALUES 
    (1, 1, '2025-09-01 10:20:00', NULL),
    (2, 2, '2025-09-02 11:35:00', 'RX-2025-0891'),
    (3, 1, '2025-09-03 14:05:00', NULL),
    (4, 6, '2025-09-05 09:50:00', 'RX-2025-0895'),
    (5, 2, '2025-09-08 12:25:00', 'RX-2025-0902'),
    (6, 1, '2025-09-10 15:15:00', NULL),
    (7, 6, '2025-09-12 16:35:00', 'RX-2025-0914'),
    (8, 2, '2025-09-15 10:10:00', NULL),
    (9, 1, '2025-09-18 11:55:00', 'RX-2025-0925'),
    (10, 6, '2025-09-22 13:45:00', 'RX-2025-0931'),
    (11, 1, '2025-10-01 09:25:00', NULL),
    (12, 2, '2025-10-02 10:50:00', NULL),
    (13, 6, '2025-10-04 11:20:00', 'RX-2025-0955'),
    (14, 2, '2025-10-06 14:35:00', 'RX-2025-0962'),
    (15, 1, '2025-10-08 15:55:00', 'RX-2025-0970'),
    (16, 6, '2025-10-10 10:15:00', NULL),
    (17, 2, '2025-10-12 12:05:00', 'RX-2025-0985'),
    (18, 1, '2025-10-15 14:20:00', 'RX-2025-0992'),
    (19, 6, '2025-10-18 16:45:00', NULL),
    (20, 2, '2025-10-20 17:05:00', 'RX-2025-1008');
    """)

    print("Seeding Expenses and Payroll...")
    cur.execute("""
    INSERT INTO Expense (RecordedByUserID, Category, Description, Amount, ExpenseDate) VALUES 
    (4, 'Rent', 'Pharmacy building rent for September', 1800000.00, '2025-09-01'),
    (4, 'Utilities', 'Umeme electricity bill for September', 280000.00, '2025-09-05'),
    (4, 'Utilities', 'NWSC water bill for September', 85000.00, '2025-09-06'),
    (4, 'Transport', 'Drug delivery from Luzira QCIL', 120000.00, '2025-09-10'),
    (4, 'Security', 'Securiko guard services September', 350000.00, '2025-09-15'),
    (4, 'Internet', 'MTN fiber internet subscription', 150000.00, '2025-09-20'),
    (4, 'Rent', 'Pharmacy building rent for October', 1800000.00, '2025-10-01'),
    (4, 'Utilities', 'Umeme electricity bill for October', 310000.00, '2025-10-05'),
    (4, 'Maintenance', 'Air conditioning servicing in drug store', 250000.00, '2025-10-08'),
    (4, 'Packaging', 'Branded medicine dispensing bags & labels', 180000.00, '2025-10-12'),
    (4, 'Security', 'Securiko guard services October', 350000.00, '2025-10-15');

    INSERT INTO Payroll (StaffUserID, RecordedByUserID, Amount, PaymentDate, PaymentType) VALUES 
    (1, 4, 1800000.00, '2025-09-30', 'Salary'), -- Pharmacist Sabano
    (2, 4, 1200000.00, '2025-09-30', 'Salary'), -- Dispenser Matthew
    (3, 4, 3000000.00, '2025-09-30', 'Salary'), -- Director Alex
    (4, 4, 2200000.00, '2025-09-30', 'Salary'), -- Operations Mgr Grace
    (5, 4, 850000.00,  '2025-09-30', 'Salary'), -- Cashier David
    (6, 4, 1800000.00, '2025-09-30', 'Salary'), -- Pharmacist Sarah
    (8, 4, 850000.00,  '2025-09-30', 'Salary'), -- Cashier Joan
    (1, 4, 1800000.00, '2025-10-31', 'Salary'),
    (2, 4, 1200000.00, '2025-10-31', 'Salary'),
    (3, 4, 3000000.00, '2025-10-31', 'Salary'),
    (4, 4, 2200000.00, '2025-10-31', 'Salary'),
    (5, 4, 850000.00,  '2025-10-31', 'Salary'),
    (2, 4, 200000.00,  '2025-10-15', 'Advance'), -- Advance for Matthew
    (6, 4, 1800000.00, '2025-10-31', 'Salary');
    """)

    print("Creating 4 analytical views for reporting...")
    cur.execute("""
    -- 1. Current stock view
    CREATE OR REPLACE VIEW vw_current_stock AS
    SELECT d.DrugID, d.DrugName, d.Category, d.ReorderLevel,
           COALESCE(SUM(sb.QuantityRemaining), 0) AS TotalStock,
           CASE 
               WHEN COALESCE(SUM(sb.QuantityRemaining), 0) = 0 THEN 'Out of Stock'
               WHEN COALESCE(SUM(sb.QuantityRemaining), 0) <= d.ReorderLevel THEN 'Low Stock'
               ELSE 'Adequate'
           END AS StockStatus
    FROM Drug d
    LEFT JOIN StockBatch sb ON sb.DrugID = d.DrugID
    GROUP BY d.DrugID, d.DrugName, d.Category, d.ReorderLevel;

    -- 2. Purchase order summary view
    CREATE OR REPLACE VIEW vw_purchase_order_summary AS
    SELECT po.POID, po.OrderDate, po.Status, s.CompanyName AS Supplier,
           u.FullName AS CreatedBy,
           COALESCE(SUM(poi.QuantityOrdered * poi.UnitCost), 0) AS OrderTotal
    FROM PurchaseOrder po
    JOIN Supplier s ON s.SupplierID = po.SupplierID
    JOIN "User" u   ON u.UserID = po.CreatedByUserID
    LEFT JOIN PurchaseOrderItem poi ON poi.POID = po.POID
    GROUP BY po.POID, po.OrderDate, po.Status, s.CompanyName, u.FullName;

    -- 3. Sales detail view
    CREATE OR REPLACE VIEW vw_sales_detail AS
    SELECT s.SaleID, s.ReceiptNumber, s.SaleDate, s.PaymentType, s.CustomerName,
           u.FullName AS Cashier, d.DrugName, d.Category, si.Quantity, si.UnitPrice, si.LineTotal,
           sb.BatchNumber, dr.PrescriptionRef, dr.DateDispensed
    FROM Sale s
    JOIN SaleItem si ON si.SaleID = s.SaleID
    JOIN StockBatch sb ON sb.BatchID = si.BatchID
    JOIN Drug d ON d.DrugID = sb.DrugID
    JOIN "User" u ON u.UserID = s.CashierUserID
    LEFT JOIN DispensingRegister dr ON dr.SaleItemID = si.SaleItemID;

    -- 4. Monthly financial summary view
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
    """)

    print("\nVerifying row counts in Neon:")
    for t in ['"User"', 'supplier', 'drug', 'stockbatch', 'purchaseorder', 'purchaseorderitem', 'sale', 'saleitem', 'dispensingregister', 'expense', 'payroll']:
        cur.execute(f'SELECT COUNT(*) FROM {t};')
        cnt = cur.fetchone()[0]
        name = t.replace('"', '')
        print(f"  * {name}: {cnt} rows")

    cur.close()
    conn.close()
    print("\nPIMS Database successfully initialized and seeded on Neon PostgreSQL!")


if __name__ == "__main__":
    init_database()
