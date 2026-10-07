CREATE TABLE Expense (
    ExpenseID SERIAL PRIMARY KEY,
    RecordedByUserID INT REFERENCES "User"(UserID),
    Category VARCHAR(100) NOT NULL,
    Description TEXT,
    Amount DECIMAL(12, 2) NOT NULL,
    ExpenseDate DATE NOT NULL
);

CREATE TABLE Payroll (
    PayrollID SERIAL PRIMARY KEY,
    StaffUserID INT REFERENCES "User"(UserID),
    RecordedByUserID INT REFERENCES "User"(UserID),
    Amount DECIMAL(12, 2) NOT NULL,
    PaymentDate DATE NOT NULL,
    PaymentType VARCHAR(20) CHECK (PaymentType IN ('Salary', 'Advance', 'Bonus'))
);

INSERT INTO Expense (RecordedByUserID, Category, Description, Amount, ExpenseDate) VALUES 
(1, 'Utilities', 'October Electricity Bill', 150000.00, '2025-10-01'),
(1, 'Rent', 'Pharmacy Rent for Oct', 2000000.00, '2025-10-02');

INSERT INTO Payroll (StaffUserID, RecordedByUserID, Amount, PaymentDate, PaymentType) VALUES 
(1, 1, 1500000.00, '2025-09-30', 'Salary'),
(2, 1, 1000000.00, '2025-09-30', 'Salary');
