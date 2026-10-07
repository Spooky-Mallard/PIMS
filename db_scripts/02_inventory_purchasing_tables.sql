CREATE TABLE StockBatch (
    BatchID SERIAL PRIMARY KEY,
    DrugID INT REFERENCES Drug(DrugID),
    SupplierID INT REFERENCES Supplier(SupplierID),
    BatchNumber VARCHAR(40) NOT NULL,
    QuantityReceived INT NOT NULL,
    QuantityRemaining INT NOT NULL,
    ExpiryDate DATE NOT NULL,
    DateReceived DATE NOT NULL
);

CREATE TABLE PurchaseOrder (
    POID SERIAL PRIMARY KEY,
    SupplierID INT REFERENCES Supplier(SupplierID),
    CreatedByUserID INT REFERENCES "User"(UserID),
    OrderDate DATE NOT NULL,
    Status VARCHAR(20) CHECK (Status IN ('Pending', 'Received', 'Cancelled'))
);

CREATE TABLE PurchaseOrderItem (
    POItemID SERIAL PRIMARY KEY,
    POID INT REFERENCES PurchaseOrder(POID),
    DrugID INT REFERENCES Drug(DrugID),
    QuantityOrdered INT NOT NULL,
    UnitCost DECIMAL(10, 2) NOT NULL
);

-- Dummy records
INSERT INTO StockBatch (DrugID, SupplierID, BatchNumber, QuantityReceived, QuantityRemaining, ExpiryDate, DateReceived) VALUES
(1, 1, 'BATCH-001', 500, 500, '2028-01-01', '2025-10-01'),
(2, 2, 'BATCH-002', 200, 150, '2027-05-15', '2025-10-02');

INSERT INTO PurchaseOrder (SupplierID, CreatedByUserID, OrderDate, Status) VALUES
(1, 1, '2025-09-20', 'Received'),
(2, 1, '2025-09-25', 'Pending');

INSERT INTO PurchaseOrderItem (POID, DrugID, QuantityOrdered, UnitCost) VALUES
(1, 1, 500, 300.00),
(2, 2, 200, 1000.00);
