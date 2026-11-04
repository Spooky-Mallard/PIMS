-- 02_inventory_purchasing_tables.sql
-- Sekarungi Pharmaceuticals Ltd
-- Requires: 01_foundational_tables.sql

CREATE TABLE IF NOT EXISTS StockBatch (
    BatchID SERIAL PRIMARY KEY,
    DrugID INT REFERENCES Drug(DrugID),
    SupplierID INT REFERENCES Supplier(SupplierID),
    BatchNumber VARCHAR(40) NOT NULL,
    QuantityReceived INT NOT NULL,
    QuantityRemaining INT NOT NULL,
    ExpiryDate DATE NOT NULL,
    DateReceived DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS PurchaseOrder (
    POID SERIAL PRIMARY KEY,
    SupplierID INT REFERENCES Supplier(SupplierID),
    CreatedByUserID INT REFERENCES "User"(UserID),
    OrderDate DATE NOT NULL,
    Status VARCHAR(20) CHECK (Status IN ('Pending', 'Received', 'Cancelled'))
);

CREATE TABLE IF NOT EXISTS PurchaseOrderItem (
    POItemID SERIAL PRIMARY KEY,
    POID INT REFERENCES PurchaseOrder(POID),
    DrugID INT REFERENCES Drug(DrugID),
    QuantityOrdered INT NOT NULL,
    UnitCost DECIMAL(10, 2) NOT NULL
);

-- ========================================================
-- DUMMY DATA INSERTS (20-40 RECORDS PER TABLE)
-- ========================================================

-- 1. Insert 30 Stock Batches
INSERT INTO StockBatch (DrugID, SupplierID, BatchNumber, QuantityReceived, QuantityRemaining, ExpiryDate, DateReceived) VALUES
(1, 1, 'BN-PARA-2401', 500, 320, '2028-06-30', '2026-08-15'),
(1, 1, 'BN-PARA-2402', 300, 45, '2026-11-20', '2026-07-10'),   -- Near expiry (29 days left)
(2, 2, 'BN-AMOX-8801', 400, 180, '2027-12-31', '2026-08-20'),
(3, 3, 'BN-IBUP-1201', 600, 450, '2028-04-15', '2026-09-01'),
(4, 4, 'BN-METF-9901', 250, 80, '2027-08-10', '2026-08-05'),
(5, 5, 'BN-CIPR-4401', 300, 120, '2027-10-15', '2026-09-12'),
(6, 6, 'BN-OMEP-7701', 350, 210, '2027-02-28', '2026-09-18'),   -- 91-180 days
(7, 7, 'BN-CETI-3301', 500, 390, '2028-09-15', '2026-09-22'),
(8, 8, 'BN-AZIT-5501', 200, 65, '2027-05-30', '2026-08-28'),
(9, 9, 'BN-AMLO-2201', 400, 290, '2028-08-20', '2026-09-25'),
(10, 10, 'BN-LOSA-1101', 300, 175, '2027-11-15', '2026-09-10'),
(11, 5, 'BN-ALUM-6601', 800, 520, '2028-12-01', '2026-08-12'),
(12, 6, 'BN-METR-5501', 450, 310, '2027-09-18', '2026-09-05'),
(13, 2, 'BN-SALB-7701', 150, 45, '2027-04-30', '2026-08-18'),
(14, 11, 'BN-PRED-8801', 300, 190, '2028-01-15', '2026-09-15'),
(15, 1, 'BN-DOXY-9901', 250, 110, '2027-07-22', '2026-08-30'),
(16, 12, 'BN-ATOR-3301', 200, 95, '2027-12-10', '2026-09-20'),
(17, 9, 'BN-ORS-4401', 1000, 780, '2029-03-31', '2026-09-28'),
(18, 13, 'BN-DICL-5501', 180, 70, '2027-06-15', '2026-08-25'),
(19, 4, 'BN-ERYT-6601', 220, 85, '2027-09-30', '2026-09-02'),
(20, 3, 'BN-VITC-7701', 1200, 920, '2029-05-15', '2026-10-01'),
(21, 1, 'BN-CEFT-8801', 250, 140, '2027-11-30', '2026-09-10'),
(22, 14, 'BN-INSU-9901', 120, 40, '2026-12-15', '2026-08-15'),  -- Near expiry (54 days left)
(23, 6, 'BN-COTR-1101', 500, 340, '2028-03-20', '2026-09-12'),
(24, 2, 'BN-AMCL-2201', 350, 190, '2027-10-25', '2026-09-22'),
(25, 9, 'BN-MVIT-3301', 150, 60, '2027-08-15', '2026-09-26'),
(1, 1, 'BN-PARA-OLD1', 200, 15, '2026-05-10', '2025-05-10'),    -- Expired with stock (compliance alert)
(2, 2, 'BN-AMOX-OLD1', 150, 12, '2026-07-15', '2025-07-15'),    -- Expired with stock (compliance alert)
(11, 5, 'BN-ALUM-EXP1', 300, 30, '2027-01-05', '2026-01-05'),   -- Near expiry (75 days left)
(22, 14, 'BN-INSU-EXP1', 60, 10, '2027-03-20', '2026-03-20');   -- Expiring in ~150 days

-- 2. Insert 20 Purchase Orders
INSERT INTO PurchaseOrder (SupplierID, CreatedByUserID, OrderDate, Status) VALUES
(1, 1, '2025-08-01', 'Received'),
(2, 4, '2025-08-05', 'Received'),
(3, 1, '2025-08-10', 'Received'),
(4, 4, '2025-08-15', 'Received'),
(5, 1, '2025-08-20', 'Received'),
(6, 4, '2025-08-25', 'Received'),
(7, 1, '2025-09-01', 'Received'),
(8, 4, '2025-09-05', 'Received'),
(9, 1, '2025-09-10', 'Received'),
(10, 4, '2025-09-15', 'Received'),
(11, 1, '2025-09-20', 'Received'),
(12, 4, '2025-09-25', 'Received'),
(13, 1, '2025-10-01', 'Received'),
(14, 4, '2025-10-05', 'Received'),
(1, 1, '2025-10-10', 'Pending'),
(2, 4, '2025-10-12', 'Pending'),
(5, 1, '2025-10-15', 'Pending'),
(7, 4, '2025-10-16', 'Pending'),
(3, 1, '2025-10-18', 'Cancelled'),
(4, 4, '2025-10-19', 'Cancelled');

-- 3. Insert 35 Purchase Order Items
INSERT INTO PurchaseOrderItem (POID, DrugID, QuantityOrdered, UnitCost) VALUES
(1, 1, 500, 300.00),
(1, 21, 250, 10000.00),
(2, 2, 400, 800.00),
(2, 24, 350, 5500.00),
(3, 3, 600, 500.00),
(3, 20, 1200, 180.00),
(4, 4, 250, 950.00),
(4, 19, 220, 1000.00),
(5, 5, 300, 1600.00),
(5, 11, 800, 3200.00),
(6, 6, 350, 1100.00),
(6, 12, 450, 650.00),
(7, 7, 500, 380.00),
(8, 8, 200, 3000.00),
(9, 9, 400, 1250.00),
(9, 17, 1000, 480.00),
(10, 10, 300, 1900.00),
(11, 14, 300, 700.00),
(12, 16, 200, 2200.00),
(13, 18, 180, 4200.00),
(14, 22, 120, 18500.00),
(15, 1, 400, 320.00),
(15, 21, 200, 10500.00),
(16, 2, 300, 820.00),
(16, 24, 200, 5800.00),
(17, 5, 250, 1650.00),
(17, 11, 500, 3300.00),
(18, 7, 400, 390.00),
(18, 25, 150, 14000.00),
(19, 3, 300, 500.00),
(20, 4, 200, 950.00),
(1, 15, 250, 900.00),
(2, 13, 150, 8000.00),
(7, 23, 500, 750.00),
(8, 25, 100, 14500.00);
