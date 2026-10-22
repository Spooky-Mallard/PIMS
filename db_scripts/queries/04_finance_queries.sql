-- Q4.1 Monthly expenses by category
SELECT DATE_TRUNC('month', ExpenseDate) AS Month,
       Category,
       SUM(Amount) AS TotalExpense
FROM Expense
GROUP BY DATE_TRUNC('month', ExpenseDate), Category
ORDER BY Month DESC, TotalExpense DESC;

-- Q4.2 Total paid to each staff member, split by payment type
SELECT u.FullName, p.PaymentType, SUM(p.Amount) AS TotalPaid
FROM Payroll p
JOIN "User" u ON u.UserID = p.StaffUserID
GROUP BY u.UserID, u.FullName, p.PaymentType
ORDER BY u.FullName, p.PaymentType;

-- Q4.3 Expense categories costing more than 500,000 in total
SELECT Category, SUM(Amount) AS TotalExpense
FROM Expense
GROUP BY Category
HAVING SUM(Amount) > 500000
ORDER BY TotalExpense DESC;

-- Q4.4 Who recorded the most financial entries (audit)
SELECT u.FullName,
       (SELECT COUNT(*) FROM Expense e WHERE e.RecordedByUserID = u.UserID) AS ExpensesRecorded,
       (SELECT COUNT(*) FROM Payroll p WHERE p.RecordedByUserID = u.UserID) AS PayrollRecorded
FROM "User" u
ORDER BY ExpensesRecorded + PayrollRecorded DESC;

-- Q4.5 Monthly profit = revenue - expenses - payroll
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
FULL OUTER JOIN payroll p  ON p.Month = COALESCE(r.Month, e.Month)
ORDER BY Month DESC;

-- Q4.6 Reusable view for reports: monthly financial summary
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