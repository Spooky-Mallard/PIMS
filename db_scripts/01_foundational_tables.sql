-- 1. USER TABLE
CREATE TABLE IF NOT EXISTS "User" (
    UserID SERIAL PRIMARY KEY,
    FullName VARCHAR(100) NOT NULL,
    Username VARCHAR(50) UNIQUE NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL,
    Role VARCHAR(20) CHECK (Role IN ('Director', 'OperationsManager', 'Pharmacist', 'Cashier', 'Dispenser')),
    Phone VARCHAR(20),
    Status VARCHAR(10) CHECK (Status IN ('Active', 'Inactive'))
);

-- 2. SUPPLIER TABLE
CREATE TABLE IF NOT EXISTS Supplier (
    SupplierID SERIAL PRIMARY KEY,
    CompanyName VARCHAR(120) NOT NULL,
    ContactPerson VARCHAR(100),
    Phone VARCHAR(20),
    Email VARCHAR(100),
    Address VARCHAR(200)
);

-- 3. DRUG TABLE
CREATE TABLE IF NOT EXISTS Drug (
    DrugID SERIAL PRIMARY KEY,
    DrugName VARCHAR(150) NOT NULL,
    Category VARCHAR(60),
    Manufacturer VARCHAR(100),
    NDARegNo VARCHAR(40),
    UnitPrice DECIMAL(10, 2) NOT NULL,
    ReorderLevel INT NOT NULL
);

-- ========================================================
-- DUMMY DATA INSERTS (20 RECORDS EACH)
-- ========================================================

-- Insert 20 Users
INSERT INTO "User" (FullName, Username, PasswordHash, Role, Phone, Status) VALUES 
('Sabano Zubedah', 'sabanoz', 'hashed123', 'Pharmacist', '+256700000001', 'Active'),
('Mumbere Matthew', 'mumberem', 'hashed123', 'Dispenser', '+256700000002', 'Active'),
('Alex Okello', 'alexo', 'hashed123', 'Director', '+256700000003', 'Active'),
('Grace Akello', 'gracea', 'hashed123', 'OperationsManager', '+256700000004', 'Active'),
('David Mukasa', 'davidm', 'hashed123', 'Cashier', '+256700000005', 'Active'),
('Sarah Namubiru', 'sarahn', 'hashed123', 'Pharmacist', '+256700000006', 'Active'),
('Brian Kintu', 'briank', 'hashed123', 'Dispenser', '+256700000007', 'Inactive'),
('Joan Nsubuga', 'joann', 'hashed123', 'Cashier', '+256700000008', 'Active'),
('Peter Kato', 'peterk', 'hashed123', 'Pharmacist', '+256700000009', 'Active'),
('Lillian Achieng', 'lilliana', 'hashed123', 'Dispenser', '+256700000010', 'Active'),
('Emmanuel Wasswa', 'emmanuelw', 'hashed123', 'OperationsManager', '+256700000011', 'Active'),
('Christine Tumusiime', 'christinet', 'hashed123', 'Cashier', '+256700000012', 'Inactive'),
('Joseph Omondi', 'josepho', 'hashed123', 'Pharmacist', '+256700000013', 'Active'),
('Mary Atuhaire', 'marya', 'hashed123', 'Dispenser', '+256700000014', 'Active'),
('Samuel Musoke', 'samuelm', 'hashed123', 'Director', '+256700000015', 'Active'),
('Patricia Nabirye', 'patrician', 'hashed123', 'Cashier', '+256700000016', 'Active'),
('Francis Mugisha', 'francism', 'hashed123', 'Pharmacist', '+256700000017', 'Inactive'),
('Rita Kamikazi', 'ritak', 'hashed123', 'Dispenser', '+256700000018', 'Active'),
('Isaac Ssebaggala', 'isaacs', 'hashed123', 'Cashier', '+256700000019', 'Active'),
('Harriet Chebet', 'harrietc', 'hashed123', 'Pharmacist', '+256700000020', 'Active');

-- Insert 20 Suppliers
INSERT INTO Supplier (CompanyName, ContactPerson, Phone, Email, Address) VALUES 
('Pharma Supplies Ltd', 'John Doe', '+256701111111', 'contact@pharmasupplies.com', 'Kampala, Uganda'),
('Kigali Meds', 'Jane Smith', '+256702222222', 'sales@kigalimeds.rw', 'Kigali, Rwanda'),
('Abacus Pharma', 'Sanjay Patel', '+256703333333', 'info@abacuspharma.com', 'Kampala, Uganda'),
('Renal Remedies', 'David Ochieng', '+256704444444', 'orders@renalremedies.com', 'Entebbe, Uganda'),
('Quality Chemicals', 'Florence Babirye', '+256705555555', 'support@qcil.co.ug', 'Luzira, Uganda'),
('East Africa Pharmaceuticals', 'Michael Kironde', '+256706666666', 'sales@eapharma.com', 'Jinja, Uganda'),
('Universal Corporation', 'Anita Sharma', '+254707777777', 'contact@universalcorp.ke', 'Nairobi, Kenya'),
('Medreich Africa', 'Robert Kibuuka', '+256708888888', 'info@medreich.co.ug', 'Kampala, Uganda'),
('Laborex Uganda', 'Esther Nantongo', '+256709999999', 'orders@laborex.ug', 'Kampala, Uganda'),
('Sun Pharma Ltd', 'Rahul Verma', '+256710000001', 'info@sunpharma.com', 'Kampala, Uganda'),
('AstraZeneca EA', 'Clara Wanjiku', '+254710000002', 'contact@astrazeneca.co.ke', 'Nairobi, Kenya'),
('Novartis Africa', 'George Mugerwa', '+256710000003', 'sales@novartis.ug', 'Kampala, Uganda'),
('Bayer Healthcare', 'Linda Nnamdi', '+256710000004', 'info@bayer.co.ug', 'Kampala, Uganda'),
('Pfizer Uganda', 'James Bwambale', '+256710000005', 'contact@pfizer.ug', 'Kampala, Uganda'),
('Sanofi EA', 'Rachel Adhiambo', '+254710000006', 'info@sanofi.co.ke', 'Nairobi, Kenya'),
('GlaxoSmithKline', 'Tom Kyagulanyi', '+256710000007', 'orders@gsk.ug', 'Kampala, Uganda'),
('Cipla Quality Chemical', 'Emmanuel Kato', '+256710000008', 'sales@ciplaqcil.co.ug', 'Kampala, Uganda'),
('Meditech Pharma', 'Susan Mbabazi', '+256710000009', 'info@meditech.ug', 'Mbarara, Uganda'),
('Healthline Distributors', 'Paul Sserwadda', '+256710000010', 'sales@healthline.ug', 'Kampala, Uganda'),
('Apex Pharmaceuticals', 'Doreen Kashemire', '+256710000011', 'contact@apexpharma.ug', 'Gulu, Uganda');

-- Insert 20 Drugs
INSERT INTO Drug (DrugName, Category, Manufacturer, NDARegNo, UnitPrice, ReorderLevel) VALUES 
('Paracetamol 500mg', 'Analgesic', 'Cipla', 'NDA/101', 500.00, 100),
('Amoxicillin 250mg', 'Antibiotic', 'GSK', 'NDA/102', 1200.00, 50),
('Ibuprofen 400mg', 'Anti-inflammatory', 'Abacus', 'NDA/103', 800.00, 80),
('Metformin 500mg', 'Antidiabetic', 'Sun Pharma', 'NDA/104', 1500.00, 60),
('Ciprofloxacin 500mg', 'Antibiotic', 'Laborex', 'NDA/105', 2500.00, 40),
('Omeprazole 20mg', 'Antacid', 'QCIL', 'NDA/106', 1800.00, 70),
('Cetirizine 10mg', 'Antihistamine', 'Medreich', 'NDA/107', 600.00, 120),
('Azithromycin 500mg', 'Antibiotic', 'Pfizer', 'NDA/108', 4500.00, 30),
('Amlodipine 5mg', 'Antihypertensive', 'Novartis', 'NDA/109', 2000.00, 50),
('Losartan 50mg', 'Antihypertensive', 'Sanofi', 'NDA/110', 3000.00, 45),
('Artemether/Lumefantrine', 'Antimalarial', 'QCIL', 'NDA/111', 5000.00, 150),
('Metronidazole 400mg', 'Antibiotic', 'Universal', 'NDA/112', 1000.00, 90),
('Salbutamol Inhaler', 'Bronchodilator', 'GSK', 'NDA/113', 12000.00, 20),
('Prednisolone 5mg', 'Corticosteroid', 'Bayer', 'NDA/114', 1100.00, 60),
('Doxycycline 100mg', 'Antibiotic', 'Cipla', 'NDA/115', 1400.00, 40),
('Atorvastatin 20mg', 'Antihyperlipidemic', 'AstraZeneca', 'NDA/116', 3500.00, 35),
('Oral Rehydration Salts', 'Electrolyte', 'Laborex', 'NDA/117', 800.00, 200),
('Diclofenac Gel 1%', 'Analgesic', 'Novartis', 'NDA/118', 6500.00, 25),
('Erythromycin 250mg', 'Antibiotic', 'Sun Pharma', 'NDA/119', 1600.00, 50),
('Vitamin C 500mg', 'Supplement', 'Abacus', 'NDA/120', 300.00, 300),
('Ceftriaxone 1g Injection', 'Antibiotic', 'Cipla', 'NDA/121', 15000.00, 40),
('Human Insulin 100IU/ml', 'Antidiabetic', 'Novo Nordisk', 'NDA/122', 28000.00, 20),
('Co-trimoxazole 480mg', 'Antibiotic', 'Universal', 'NDA/123', 1200.00, 80),
('Amoxiclav 625mg', 'Antibiotic', 'GSK', 'NDA/124', 8500.00, 60),
('Multivitamin Infusion 500ml', 'Supplement', 'Laborex', 'NDA/125', 22000.00, 30);
