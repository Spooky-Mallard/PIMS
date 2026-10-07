CREATE TABLE "User" (
    UserID SERIAL PRIMARY KEY,
    FullName VARCHAR(100) NOT NULL,
    Username VARCHAR(50) UNIQUE NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL,
    Role VARCHAR(20) CHECK (Role IN ('Director', 'OperationsManager', 'Pharmacist', 'Cashier', 'Dispenser')),
    Phone VARCHAR(20),
    Status VARCHAR(10) CHECK (Status IN ('Active', 'Inactive'))
);

CREATE TABLE Supplier (
    SupplierID SERIAL PRIMARY KEY,
    CompanyName VARCHAR(120) NOT NULL,
    ContactPerson VARCHAR(100),
    Phone VARCHAR(20),
    Email VARCHAR(100),
    Address VARCHAR(200)
);

CREATE TABLE Drug (
    DrugID SERIAL PRIMARY KEY,
    DrugName VARCHAR(150) NOT NULL,
    Category VARCHAR(60),
    Manufacturer VARCHAR(100),
    NDARegNo VARCHAR(40),
    UnitPrice DECIMAL(10, 2) NOT NULL,
    ReorderLevel INT NOT NULL
);

INSERT INTO "User" (FullName, Username, PasswordHash, Role, Phone, Status) VALUES 
('Sabano Zubedah', 'sabanoz', 'hashed123', 'Pharmacist', '+256700000001', 'Active'),
('Mumbere Matthew', 'mumberem', 'hashed123', 'Dispenser', '+256700000002', 'Active');

INSERT INTO Supplier (CompanyName, ContactPerson, Phone, Email, Address) VALUES 
('Pharma Supplies Ltd', 'John Doe', '+256701111111', 'contact@pharmasupplies.com', 'Kampala, Uganda'),
('Kigali Meds', 'Jane Smith', '+256702222222', 'sales@kigalimeds.rw', 'Kigali, Rwanda');

INSERT INTO Drug (DrugName, Category, Manufacturer, NDARegNo, UnitPrice, ReorderLevel) VALUES 
('Paracetamol 500mg', 'Analgesic', 'Cipla', 'NDA/101', 500.00, 100),
('Amoxicillin 250mg', 'Antibiotic', 'GSK', 'NDA/102', 1200.00, 50);
