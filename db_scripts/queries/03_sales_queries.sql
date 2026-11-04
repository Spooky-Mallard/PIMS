-- Q3.1 Daily revenue
SELECT DATE(SaleDate) AS SaleDay,
       COUNT(*) AS NumberOfSales,
       SUM(TotalAmount) AS Revenue
FROM Sale
GROUP BY DATE(SaleDate)
ORDER BY SaleDay DESC;

-- Q3.2 Best-selling drugs by quantity sold
SELECT d.DrugName,
       SUM(si.Quantity) AS UnitsSold,
       SUM(si.LineTotal) AS Revenue
FROM SaleItem si
JOIN StockBatch sb ON sb.BatchID = si.BatchID
JOIN Drug d        ON d.DrugID = sb.DrugID
GROUP BY d.DrugID, d.DrugName
ORDER BY UnitsSold DESC
LIMIT 10;

-- Q3.3 Sales performance per cashier
SELECT u.FullName AS Cashier,
       COUNT(s.SaleID) AS Sales,
       SUM(s.TotalAmount) AS TotalSold
FROM "User" u
JOIN Sale s ON s.CashierUserID = u.UserID
GROUP BY u.UserID, u.FullName
ORDER BY TotalSold DESC;

-- Q3.4 Revenue and VAT by payment type
SELECT PaymentType,
       COUNT(*) AS Transactions,
       SUM(VATAmount) AS TotalVAT,
       SUM(TotalAmount) AS TotalRevenue
FROM Sale
GROUP BY PaymentType;

-- Q3.5 Compliance: sold items that have NOT been dispensed yet
SELECT s.ReceiptNumber, d.DrugName, si.Quantity
FROM SaleItem si
JOIN Sale s        ON s.SaleID = si.SaleID
JOIN StockBatch sb ON sb.BatchID = si.BatchID
JOIN Drug d        ON d.DrugID = sb.DrugID
LEFT JOIN DispensingRegister dr ON dr.SaleItemID = si.SaleItemID
WHERE dr.RegisterID IS NULL;

-- Q3.6 Dispensing log: who dispensed what and when
SELECT dr.DateDispensed, d.DrugName, si.Quantity,
       u.FullName AS DispensedBy, dr.PrescriptionRef
FROM DispensingRegister dr
JOIN SaleItem si   ON si.SaleItemID = dr.SaleItemID
JOIN StockBatch sb ON sb.BatchID = si.BatchID
JOIN Drug d        ON d.DrugID = sb.DrugID
JOIN "User" u      ON u.UserID = dr.DispensedByUserID
ORDER BY dr.DateDispensed DESC;

-- Q3.7 Reusable view for reports: sales detail (one row per sold line)
CREATE OR REPLACE VIEW vw_sales_detail AS
SELECT s.SaleID, s.ReceiptNumber, s.SaleDate, s.PaymentType,
       u.FullName AS Cashier, d.DrugName, si.Quantity, si.UnitPrice, si.LineTotal
FROM Sale s
JOIN SaleItem si   ON si.SaleID = s.SaleID
JOIN StockBatch sb ON sb.BatchID = si.BatchID
JOIN Drug d        ON d.DrugID = sb.DrugID
JOIN "User" u      ON u.UserID = s.CashierUserID;