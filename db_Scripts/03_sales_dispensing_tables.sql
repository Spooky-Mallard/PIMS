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

CREATE TABLE SaleItem (
    SaleItemID SERIAL PRIMARY KEY,
    SaleID INT REFERENCES Sale(SaleID),
    BatchID INT REFERENCES StockBatch(BatchID),
    Quantity INT NOT NULL,
    UnitPrice DECIMAL(10, 2) NOT NULL,
    LineTotal DECIMAL(10, 2) NOT NULL
);

INSERT INTO Sale (CashierUserID, ReceiptNumber, CustomerName, SaleDate, SubTotal, VATAmount, TotalAmount, PaymentType) VALUES 
(1, 'RCPT-1001', 'Walk-in', '2025-10-05 10:30:00', 5000.00, 900.00, 5900.00, 'Cash'),
(2, 'RCPT-1002', 'Alice Mukasa', '2025-10-06 14:15:00', 12000.00, 2160.00, 14160.00, 'MobileMoney'),
(1, 'RCPT-1003', 'John Ssali', '2025-10-07 09:10:00', 3000.00, 540.00, 3540.00, 'Cash'),
(2, 'RCPT-1004', 'Grace Nansubuga', '2025-10-08 11:25:00', 7500.00, 1350.00, 8850.00, 'MobileMoney'),
(1, 'RCPT-1005', 'Peter Owino', '2025-10-09 14:00:00', 15000.00, 2700.00, 17700.00, 'Card'),
(2, 'RCPT-1006', 'Walk-in', '2025-10-10 08:45:00', 2000.00, 360.00, 2360.00, 'Cash'),
(1, 'RCPT-1007', 'Mary Achieng', '2025-10-11 10:30:00', 4500.00, 810.00, 5310.00, 'MobileMoney'),
(2, 'RCPT-1008', 'Robert Tumwine', '2025-10-12 13:15:00', 9000.00, 1620.00, 10620.00, 'Card'),
(1, 'RCPT-1009', 'Sarah Nabirye', '2025-10-13 09:50:00', 20000.00, 3600.00, 23600.00, 'Cash'),
(2, 'RCPT-1010', 'Michael Odongo', '2025-10-14 15:20:00', 6000.00, 1080.00, 7080.00, 'MobileMoney'),
(1, 'RCPT-1011', 'Esther Nakimuli', '2025-10-15 11:05:00', 11000.00, 1980.00, 12980.00, 'Card'),
(2, 'RCPT-1012', 'Walk-in', '2025-10-16 08:30:00', 2500.00, 450.00, 2950.00, 'Cash'),
(1, 'RCPT-1013', 'David Kiwanuka', '2025-10-17 12:40:00', 13500.00, 2430.00, 15930.00, 'MobileMoney'),
(2, 'RCPT-1014', 'Florence Among', '2025-10-18 10:15:00', 8000.00, 1440.00, 9440.00, 'Card'),
(1, 'RCPT-1015', 'James Okello', '2025-10-19 14:50:00', 17000.00, 3060.00, 20060.00, 'Cash'),
(2, 'RCPT-1016', 'Walk-in', '2025-10-20 09:25:00', 3500.00, 630.00, 4130.00, 'MobileMoney'),
(1, 'RCPT-1017', 'Ruth Nambi', '2025-10-21 11:40:00', 10000.00, 1800.00, 11800.00, 'Card'),
(2, 'RCPT-1018', 'Samuel Mugisha', '2025-10-22 13:55:00', 6500.00, 1170.00, 7670.00, 'Cash'),
(1, 'RCPT-1019', 'Walk-in', '2025-10-23 08:10:00', 19000.00, 3420.00, 22420.00, 'MobileMoney'),
(2, 'RCPT-1020', 'Grace Nansubuga', '2025-10-24 15:30:00', 4000.00, 720.00, 4720.00, 'Card');

INSERT INTO SaleItem (SaleID, BatchID, Quantity, UnitPrice, LineTotal) VALUES 
(1, 1, 10, 500.00, 5000.00),
(2, 2, 10, 1200.00, 12000.00);
(3, 1, 5, 600.00, 3000.00),
(4, 2, 10, 750.00, 7500.00),
(5, 1, 15, 1000.00, 15000.00),
(6, 2, 4, 500.00, 2000.00),
(7, 1, 9, 500.00, 4500.00),
(8, 2, 6, 1500.00, 9000.00),
(9, 1, 20, 1000.00, 20000.00),
(10, 2, 12, 500.00, 6000.00),
(11, 1, 11, 1000.00, 11000.00),
(12, 2, 5, 500.00, 2500.00),
(13, 1, 9, 1500.00, 13500.00),
(14, 2, 8, 1000.00, 8000.00),
(15, 1, 17, 1000.00, 17000.00),
(16, 2, 7, 500.00, 3500.00),
(17, 1, 10, 1000.00, 10000.00),
(18, 2, 13, 500.00, 6500.00),
(19, 1, 19, 1000.00, 19000.00),
(20, 2, 8, 500.00, 4000.00);

INSERT INTO DispensingRegister (SaleItemID, DispensedByUserID, DateDispensed, PrescriptionRef) VALUES 
(1, 1, '2025-10-05 10:35:00', NULL),
(2, 2, '2025-10-06 14:20:00', 'RX-2025-998');
(3, 1, '2025-10-07 09:15:00', NULL),
(4, 2, '2025-10-08 11:30:00', 'RX-2025-1004'),
(5, 1, '2025-10-09 14:05:00', NULL),
(6, 2, '2025-10-10 08:50:00', NULL),
(7, 1, '2025-10-11 10:35:00', 'RX-2025-1007'),
(8, 2, '2025-10-12 13:20:00', NULL),
(9, 1, '2025-10-13 09:55:00', 'RX-2025-1009'),
(10, 2, '2025-10-14 15:25:00', NULL),
(11, 1, '2025-10-15 11:10:00', NULL),
(12, 2, '2025-10-16 08:35:00', NULL),
(13, 1, '2025-10-17 12:45:00', 'RX-2025-1013'),
(14, 2, '2025-10-18 10:20:00', NULL),
(15, 1, '2025-10-19 14:55:00', NULL),
(16, 2, '2025-10-20 09:30:00', 'RX-2025-1016'),
(17, 1, '2025-10-21 11:45:00', NULL),
(18, 2, '2025-10-22 14:00:00', NULL),
(19, 1, '2025-10-23 08:15:00', 'RX-2025-1019'),
(20, 2, '2025-10-24 15:35:00', NULL);


