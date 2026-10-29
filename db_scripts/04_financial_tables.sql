-- 04_financial_tables.sql
-- Sekarungi Pharmaceuticals Ltd
-- Requires: 01_foundational_tables.sql

CREATE TABLE IF NOT EXISTS Expense (
    ExpenseID SERIAL PRIMARY KEY,
    RecordedByUserID INT REFERENCES "User"(UserID),
    Category VARCHAR(100) NOT NULL,
    Description TEXT,
    Amount DECIMAL(12, 2) NOT NULL,
    ExpenseDate DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS Payroll (
    PayrollID SERIAL PRIMARY KEY,
    StaffUserID INT REFERENCES "User"(UserID),
    RecordedByUserID INT REFERENCES "User"(UserID),
    Amount DECIMAL(12, 2) NOT NULL,
    PaymentDate DATE NOT NULL,
    PaymentType VARCHAR(20) CHECK (PaymentType IN ('Salary', 'Advance', 'Bonus'))
);

-- ========================================================
-- DUMMY DATA INSERTS (24 Expenses, 24 Payroll Disbursements)
-- ========================================================

-- 1. Insert 24 Operating Expenses (Categorized & Audited)
INSERT INTO Expense (RecordedByUserID, Category, Description, Amount, ExpenseDate) VALUES 
-- September 2025 Operating Expenses (Total: 4,200,000 UGX)
(4, 'Rent', 'Commercial Pharmacy Premises Rent (September 2025)', 2500000.00, '2025-09-01'),
(4, 'Utilities', 'Umeme Commercial Electricity Power (September)', 380000.00, '2025-09-03'),
(4, 'Generator & Fuel', 'Diesel for Cold-Chain Backup Generator (200 Litres)', 320000.00, '2025-09-06'),
(4, 'Security', 'Securico Guard Patrol Services (September)', 250000.00, '2025-09-08'),
(4, 'Internet & IT', 'MTN High-Speed Fiber Internet & VPN Subscription', 200000.00, '2025-09-10'),
(4, 'Sanitation & Cleaning', 'Clinical Facility Sanitation & PPE Supplies', 150000.00, '2025-09-14'),
(4, 'Medical Waste Disposal', 'Certified Biohazard Pharmaceutical Waste Incineration', 220000.00, '2025-09-20'),
(4, 'Stationery & Printing', 'Prescription Registers, Invoices & Receipt Rolls', 180000.00, '2025-09-25'),

-- October 2025 Operating Expenses (Total: 4,450,000 UGX)
(4, 'Rent', 'Commercial Pharmacy Premises Rent (October 2025)', 2500000.00, '2025-10-01'),
(4, 'Utilities', 'Umeme Commercial Electricity Power (October)', 410000.00, '2025-10-02'),
(4, 'Generator & Fuel', 'Diesel for Backup Generator (Cold-Chain Maintenance)', 340000.00, '2025-10-05'),
(4, 'Regulatory Compliance', 'National Drug Authority (NDA) Annual Licensing Levy', 350000.00, '2025-10-07'),
(4, 'Security', 'Securico Guard Patrol Services (October)', 250000.00, '2025-10-08'),
(4, 'Internet & IT', 'MTN Fiber Internet & Database Cloud Backup Link', 200000.00, '2025-10-10'),
(4, 'Repairs & Maintenance', 'Cold-Room Air Conditioning Servicing & Calibration', 160000.00, '2025-10-14'),
(4, 'Medical Waste Disposal', 'Clinical Biohazard Waste Collection (October)', 240000.00, '2025-10-18'),

-- Additional audited operating entries (November preparation & ad-hoc)
(4, 'Stationery & Printing', 'Pharmacy Stamp, POS Thermal Paper Rolls & Registers', 120000.00, '2025-10-20'),
(4, 'Sanitation & Cleaning', 'Pharmacy Disinfection & Sanitizer Refills', 140000.00, '2025-10-22'),
(4, 'Marketing & Outreach', 'Community Health Screening Camp Flyers & Banner', 250000.00, '2025-09-15'),
(4, 'Transport & Logistics', 'Inter-Branch Stock Relocation Dispatch Van Fuel', 180000.00, '2025-09-18'),
(4, 'Staff Welfare', 'Team Clinical Training Tea & Refreshments', 110000.00, '2025-09-28'),
(4, 'Equipment Calibration', 'Digital Weighing Scale & Temperature Monitor Certification', 190000.00, '2025-10-21'),
(4, 'Repairs & Maintenance', 'Shelving & Lockable Dangerous Drug Safe Hinge Repair', 95000.00, '2025-10-23'),
(4, 'Staff Welfare', 'End-of-Month Staff Refreshments & Water Dispenser Refills', 135000.00, '2025-10-24');

-- 2. Insert 24 Staff Payroll Records (September & October Distributions)
INSERT INTO Payroll (StaffUserID, RecordedByUserID, Amount, PaymentDate, PaymentType) VALUES 
-- September 2025 Payroll (Total: 10,800,000 UGX)
(3, 4, 2500000.00, '2025-09-30', 'Salary'),   -- Alex Okello (Director)
(4, 3, 1800000.00, '2025-09-30', 'Salary'),   -- Grace Akello (Operations Manager)
(1, 4, 1200000.00, '2025-09-30', 'Salary'),   -- Sabano Zubedah (Lead Pharmacist)
(6, 4, 1100000.00, '2025-09-30', 'Salary'),   -- Sarah Namubiru (Pharmacist)
(9, 4, 1100000.00, '2025-09-30', 'Salary'),   -- Peter Kato (Pharmacist)
(2, 4, 750000.00, '2025-09-30', 'Salary'),    -- Mumbere Matthew (Dispenser)
(10, 4, 700000.00, '2025-09-30', 'Salary'),   -- Lillian Achieng (Dispenser)
(14, 4, 700000.00, '2025-09-30', 'Salary'),   -- Mary Atuhaire (Dispenser)
(5, 4, 550000.00, '2025-09-30', 'Salary'),    -- David Mukasa (Head Cashier)
(8, 4, 500000.00, '2025-09-30', 'Salary'),    -- Joan Nsubuga (Cashier)
(1, 4, 150000.00, '2025-09-15', 'Advance'),   -- Mid-month advance
(2, 4, 100000.00, '2025-09-15', 'Advance'),   -- Mid-month advance

-- October 2025 Payroll (Total: 11,200,000 UGX)
(3, 4, 2500000.00, '2025-10-31', 'Salary'),   -- Alex Okello (Director)
(4, 3, 1800000.00, '2025-10-31', 'Salary'),   -- Grace Akello (Operations Manager)
(1, 4, 1200000.00, '2025-10-31', 'Salary'),   -- Sabano Zubedah (Lead Pharmacist)
(6, 4, 1100000.00, '2025-10-31', 'Salary'),   -- Sarah Namubiru (Pharmacist)
(9, 4, 1100000.00, '2025-10-31', 'Salary'),   -- Peter Kato (Pharmacist)
(2, 4, 750000.00, '2025-10-31', 'Salary'),    -- Mumbere Matthew (Dispenser)
(10, 4, 700000.00, '2025-10-31', 'Salary'),   -- Lillian Achieng (Dispenser)
(14, 4, 700000.00, '2025-10-31', 'Salary'),   -- Mary Atuhaire (Dispenser)
(5, 4, 550000.00, '2025-10-31', 'Salary'),    -- David Mukasa (Head Cashier)
(8, 4, 500000.00, '2025-10-31', 'Salary'),    -- Joan Nsubuga (Cashier)
(1, 4, 200000.00, '2025-10-25', 'Bonus'),     -- Clinical audit compliance performance bonus
(2, 4, 100000.00, '2025-10-25', 'Bonus');     -- Inventory reconciliation accuracy bonus
