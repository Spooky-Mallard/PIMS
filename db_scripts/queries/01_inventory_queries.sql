-- Q1.1 Every batch with its drug and supplier names
SELECT sb.BatchID, d.DrugName, s.CompanyName AS Supplier,
       sb.BatchNumber, sb.QuantityRemaining, sb.ExpiryDate
FROM StockBatch sb
JOIN Drug d     ON d.DrugID = sb.DrugID
JOIN Supplier s ON s.SupplierID = sb.SupplierID
ORDER BY sb.ExpiryDate;

-- Q1.2 Drugs whose total remaining stock is below the reorder level
SELECT d.DrugID, d.DrugName, d.ReorderLevel,
       COALESCE(SUM(sb.QuantityRemaining), 0) AS TotalStock
FROM Drug d
LEFT JOIN StockBatch sb ON sb.DrugID = d.DrugID
GROUP BY d.DrugID, d.DrugName, d.ReorderLevel
HAVING COALESCE(SUM(sb.QuantityRemaining), 0) < d.ReorderLevel
ORDER BY TotalStock ASC;

-- Q1.3 Batches expiring within the next 90 days (still in stock)
SELECT d.DrugName, sb.BatchNumber, sb.QuantityRemaining, sb.ExpiryDate,
       (sb.ExpiryDate - CURRENT_DATE) AS DaysLeft
FROM StockBatch sb
JOIN Drug d ON d.DrugID = sb.DrugID
WHERE sb.QuantityRemaining > 0
  AND sb.ExpiryDate BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '90 days'
ORDER BY sb.ExpiryDate;

-- Q1.4 Expired batches that still have stock (must be removed)
SELECT d.DrugName, sb.BatchNumber, sb.QuantityRemaining, sb.ExpiryDate
FROM StockBatch sb
JOIN Drug d ON d.DrugID = sb.DrugID
WHERE sb.ExpiryDate < CURRENT_DATE AND sb.QuantityRemaining > 0;

-- Q1.5 Stock value per drug (remaining quantity x unit price)
SELECT d.DrugName,
       SUM(sb.QuantityRemaining) AS UnitsInStock,
       SUM(sb.QuantityRemaining * d.UnitPrice) AS StockValue
FROM Drug d
JOIN StockBatch sb ON sb.DrugID = d.DrugID
GROUP BY d.DrugID, d.DrugName
ORDER BY StockValue DESC;

-- Q1.6 Reusable view for reports: current stock per drug
CREATE OR REPLACE VIEW vw_current_stock AS
SELECT d.DrugID, d.DrugName, d.Category, d.ReorderLevel,
       COALESCE(SUM(sb.QuantityRemaining), 0) AS TotalStock
FROM Drug d
LEFT JOIN StockBatch sb ON sb.DrugID = d.DrugID
GROUP BY d.DrugID, d.DrugName, d.Category, d.ReorderLevel;
