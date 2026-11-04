-- Q2.1 Pending purchase orders with supplier and who created them
SELECT po.POID, s.CompanyName AS Supplier, u.FullName AS CreatedBy, po.OrderDate
FROM PurchaseOrder po
JOIN Supplier s ON s.SupplierID = po.SupplierID
JOIN "User" u   ON u.UserID = po.CreatedByUserID
WHERE po.Status = 'Pending'
ORDER BY po.OrderDate;

-- Q2.2 Total cost of each purchase order (including orders with 0 items)
SELECT po.POID, s.CompanyName AS Supplier, po.Status,
       COALESCE(SUM(poi.QuantityOrdered * poi.UnitCost), 0) AS OrderTotal
FROM PurchaseOrder po
JOIN Supplier s          ON s.SupplierID = po.SupplierID
LEFT JOIN PurchaseOrderItem poi ON poi.POID = po.POID
GROUP BY po.POID, s.CompanyName, po.Status
ORDER BY OrderTotal DESC;

-- Q2.3 Top suppliers by total amount spent (received orders only)
SELECT s.SupplierID, s.CompanyName,
       COUNT(DISTINCT po.POID) AS OrdersCount,
       COALESCE(SUM(poi.QuantityOrdered * poi.UnitCost), 0) AS TotalSpent
FROM Supplier s
JOIN PurchaseOrder po      ON po.SupplierID = s.SupplierID
JOIN PurchaseOrderItem poi ON poi.POID = po.POID
WHERE po.Status = 'Received'
GROUP BY s.SupplierID, s.CompanyName
ORDER BY TotalSpent DESC
LIMIT 5;

-- Q2.4 Drugs that have never been ordered
SELECT d.DrugID, d.DrugName
FROM Drug d
LEFT JOIN PurchaseOrderItem poi ON poi.DrugID = d.DrugID
WHERE poi.POItemID IS NULL;

-- Q2.5 Average and highest purchase cost per drug
SELECT d.DrugID, d.DrugName,
       ROUND(AVG(poi.UnitCost), 2) AS AvgUnitCost,
       MAX(poi.UnitCost) AS HighestUnitCost
FROM Drug d
JOIN PurchaseOrderItem poi ON poi.DrugID = d.DrugID
GROUP BY d.DrugID, d.DrugName
ORDER BY AvgUnitCost DESC;

-- Q2.6 Reusable view for reports: purchase order summary
CREATE OR REPLACE VIEW vw_purchase_order_summary AS
SELECT po.POID, po.OrderDate, po.Status, s.CompanyName AS Supplier,
       u.FullName AS CreatedBy,
       COALESCE(SUM(poi.QuantityOrdered * poi.UnitCost), 0) AS OrderTotal
FROM PurchaseOrder po
JOIN Supplier s ON s.SupplierID = po.SupplierID
JOIN "User" u   ON u.UserID = po.CreatedByUserID
LEFT JOIN PurchaseOrderItem poi ON poi.POID = po.POID
GROUP BY po.POID, po.OrderDate, po.Status, s.CompanyName, u.FullName;
