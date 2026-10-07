CREATE TABLE Sale (
    SaleID SERIAL PRIMARY KEY,
    CashierUserID INT REFERENCES "User"(UserID),
    ReceiptNumber VARCHAR(30) UNIQUE NOT NULL,
    CustomerName VARCHAR(100),
    SaleDate TIMESTAMP NOT NULL,
    SubTotal DECIMAL(10, 2) NOT NULL,
    VATAmount DECIMAL(10, 2) NOT NULL,
    TotalAmount DECIMAL(10, 2) NOT NULL,
    PaymentType VARCHAR(20) CHECK (PaymentType IN ('Cash', 'MobileMoney', 'Card'))
);

CREATE TABLE SaleItem (
    SaleItemID SERIAL PRIMARY KEY,
    SaleID INT REFERENCES Sale(SaleID),
    BatchID INT REFERENCES StockBatch(BatchID),
    Quantity INT NOT NULL,
    UnitPrice DECIMAL(10, 2) NOT NULL,
    LineTotal DECIMAL(10, 2) NOT NULL
);

CREATE TABLE DispensingRegister (
    RegisterID SERIAL PRIMARY KEY,
    SaleItemID INT UNIQUE REFERENCES SaleItem(SaleItemID),
    DispensedByUserID INT REFERENCES "User"(UserID),
    DateDispensed TIMESTAMP NOT NULL,
    PrescriptionRef VARCHAR(100)
);

INSERT INTO Sale (CashierUserID, ReceiptNumber, CustomerName, SaleDate, SubTotal, VATAmount, TotalAmount, PaymentType) VALUES 
(1, 'RCPT-1001', 'Walk-in', '2025-10-05 10:30:00', 5000.00, 900.00, 5900.00, 'Cash'),
(2, 'RCPT-1002', 'Alice Mukasa', '2025-10-06 14:15:00', 12000.00, 2160.00, 14160.00, 'MobileMoney');

INSERT INTO SaleItem (SaleID, BatchID, Quantity, UnitPrice, LineTotal) VALUES 
(1, 1, 10, 500.00, 5000.00),
(2, 2, 10, 1200.00, 12000.00);

INSERT INTO DispensingRegister (SaleItemID, DispensedByUserID, DateDispensed, PrescriptionRef) VALUES 
(1, 1, '2025-10-05 10:35:00', NULL),
(2, 2, '2025-10-06 14:20:00', 'RX-2025-998');
