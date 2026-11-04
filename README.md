# 💊 Sekarungi Pharmaceuticals Ltd — PIMS
### Pharmaceutical Information Management System
**Makerere University** | College of Computing and Information Sciences  
**Course**: BCS 2206 Database Management Systems | **Case Study**: Sekarungi Pharmaceuticals Ltd  

[![Python Version](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Database](https://img.shields.io/badge/PostgreSQL-16%20Neon-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://neon.tech/)
[![Frontend](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Architecture](https://img.shields.io/badge/ORM-None%20(Pure%20SQL)-0f766e?style=for-the-badge)](file:///Users/spooky/Downloads/School/Database-Management-Systems/DBMS-PROJECT/backend/db.py)
[![License](https://img.shields.io/badge/License-Academic%20Evaluation-gray?style=for-the-badge)](#team--contributors)

---

## 📖 Executive Summary & Background

**Sekarungi Pharmaceuticals Ltd** is a licensed mid-scale pharmaceutical distributor and community retail pharmacy based in Kampala, Uganda. The enterprise coordinates pharmaceutical imports, regional distribution to healthcare facilities, walk-in prescription dispensing, and internal financial accounting.

### The Problem
Prior to PIMS, operations suffered from:
- **Inventory Spoilage & FEFO Failure**: High rates of drug expiration caused by lack of First-Expired, First-Out (FEFO) batch tracking.
- **Stockouts & Unmet Demand**: Delays in restocking essential antibiotics and chronic therapeutic drugs due to manual reorder calculations.
- **Regulatory Compliance Gaps**: Difficulties auditing prescription reference numbers and dispenser accountability required by the National Drug Authority (NDA).
- **Financial Leakage**: Discrepancies between point-of-sale revenues, 18% standard VAT accounting, overhead expenses, and staff payroll disbursements.

### The Solution: PIMS
The **Pharmaceutical Information Management System (PIMS)** is an end-to-end relational database solution powered by **PostgreSQL** (hosted on Neon Serverless Cloud) and accessed through an interactive **Streamlit** dashboard. Built strictly with **raw SQL via `psycopg2`** (*zero ORM*), PIMS delivers enterprise data integrity, automated accounting, live inventory alerts, and board-level reporting.

---

## 🏛️ System Architecture & Database Design

The relational database architecture is normalized to **Third Normal Form (3NF)** across **11 core entities**, backed by **4 analytical reporting views**, check constraints, foreign keys, and serial primary keys.

```
+-----------------------------------------------------------------------------------+
|                        SEKARUNGI PIMS RELATIONAL MODEL                            |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [ User ] <-------+---------------+-------------------------+                     |
|                   |               |                         |                     |
|                   | CreatedBy     | Cashier                 | DispensedBy         |
|                   v               v                         v                     |
|  [ Supplier ] <- [ PurchaseOrder ]  [ Sale ] <----------- [ DispensingRegister ]  |
|         ^              |              |                             ^             |
|         |              v              v                             |             |
|         +-- [ StockBatch ] <--- [ SaleItem ] -----------------------+             |
|                    |                  |                                           |
|                    v                  |                                           |
|                 [ Drug ] <------------+                                           |
|                                                                                   |
|  [ Expense ] <--- RecordedBy: User                                                |
|  [ Payroll ] <--- StaffUser & RecordedBy: User                                    |
+-----------------------------------------------------------------------------------+
```

### 1. Relational Entities (11 Tables)
| Domain | Entity Table | Primary Key | Description & Foreign Keys |
| :--- | :--- | :--- | :--- |
| **Foundational** | `"User"` | `UserID` | Staff accounts, bcrypt-compatible password hashes, and RBAC roles (`Director`, `OperationsManager`, `Pharmacist`, `Cashier`, `Dispenser`). |
| | `Supplier` | `SupplierID` | Registered drug importers, contact persons, phones, emails, and physical addresses. |
| | `Drug` | `DrugID` | Formulary catalog with pharmacological categories, manufacturers, NDA registration numbers, unit prices, and reorder levels. |
| **Purchasing & Stock** | `StockBatch` | `BatchID` | Delivery batches tracking `BatchNumber`, quantity received/remaining, delivery date, and `ExpiryDate` (FEFO). References `Drug` and `Supplier`. |
| | `PurchaseOrder` | `POID` | Vendor orders tracking order date, creation user, and lifecycle status (`Pending`, `Received`, `Cancelled`). |
| | `PurchaseOrderItem`| `POItemID` | Line items linking ordered pharmaceuticals to purchase orders with unit wholesale costs. |
| **Sales & Dispensing** | `Sale` | `SaleID` | Retail and wholesale receipts capturing cashier ID, customer name, timestamp, payment method (`Cash`, `MobileMoney`, `Card`), and automated 18% VAT. |
| | `SaleItem` | `SaleItemID` | Sold drug lines resolving transactions against specific inventory batches with unit prices and line totals. |
| | `DispensingRegister`| `RegisterID`| Regulatory audit register linking sold lines to dispensing pharmacists and NDA prescription reference codes. |
| **Financial Accounting** | `Expense` | `ExpenseID` | Categorized operational overheads (premises rent, power, generator fuel, NDA licensing, biohazard waste disposal) with auditing user IDs. |
| | `Payroll` | `PayrollID` | Staff compensation disbursements (`Salary`, `Advance`, `Bonus`) linked to recipient and authorizing manager. |

### 2. Analytical Reporting Views
- `vw_current_stock`: Computes aggregated active inventory across all batches per pharmaceutical item, evaluated against reorder thresholds.
- `vw_purchase_order_summary`: Summarizes purchase orders with vendor names, order dates, and total procurement spend.
- `vw_sales_detail`: Denormalized flat view linking receipts, cashiers, drug names, batch lot numbers, quantities sold, and line totals.
- `vw_monthly_financial_summary`: Consolidated monthly Profit & Loss view joining gross retail sales revenue against operational overheads and payroll to compute true net operating profit.

---

## 💻 Tech Stack & Architectural Principles

- **Database Engine**: PostgreSQL 16 on [Neon Serverless Cloud](https://neon.tech/).
- **Database Driver**: `psycopg2-binary` (Raw SQL execution).
  > **Strict Architectural Rule**: **Zero ORM** (Object-Relational Mapping such as SQLAlchemy or Django ORM is forbidden by course specification). All database communications utilize parameterized raw SQL strings to demonstrate transactional precision and index utilization.
- **Frontend Framework**: [Streamlit](https://streamlit.io/) with custom teal/slate medical styling.
- **Data Analytics & Visualizations**: [Pandas](https://pandas.pydata.org/) & [Plotly Express/Graph Objects](https://plotly.com/python/).
- **Vector Graphics**: Dual-theme Crow's Foot Entity-Relationship Diagrams in scalable SVG (`pims_erd.svg` and `pims_erd_dark.svg`).

---

## 🖥️ Application Features & Modules

The Streamlit web interface is partitioned into 6 operational sub-systems accessible via the sidebar navigation:

```
├── app.py                         # Application entrypoint & medical UI styling
├── backend/
│   ├── db.py                      # psycopg2 connection pool & raw SQL query helpers
│   └── init_db.py                 # Single-source-of-truth database initializer
├── db_scripts/                    # Canonical relational schema & seed scripts
│   ├── 01_foundational_tables.sql
│   ├── 02_inventory_purchasing_tables.sql
│   ├── 03_sales_dispensing_tables.sql
│   ├── 04_financial_tables.sql
│   └── queries/                   # Course SQL query files (PIMS-6 to PIMS-9)
│       ├── 01_inventory_queries.sql
│       ├── 02_purchasing_queries.sql
│       ├── 03_sales_queries.sql
│       └── 04_finance_queries.sql
├── modules/
│   ├── dashboard.py               # Executive KPI cards & real-time activity feeds
│   ├── schema_viewer.py           # ERD viewer with dark canvas toggle & Data Dictionary
│   ├── tables_browser.py          # Live 11-table browser with search & CSV export
│   ├── forms.py                   # 5 sectioned data entry & POS transaction forms
│   ├── queries_runner.py          # Tabbed query runner with dynamic parameter sliders
│   └── reports.py                 # Plotly P&L, sales trends, FEFO analytics & text report
└── assets/                        # High-contrast vector ERD diagrams
    ├── pims_erd.svg
    └── pims_erd_dark.svg
```

### Module Breakdown
1. **🏠 Executive Dashboard** (`modules/dashboard.py`):
   - Real-time Neon PostgreSQL engine metadata and ping indicator.
   - 4 high-level KPI cards: Catalog Pharmaceuticals count, Total Warehouse Stock Units, Cumulative Retail Revenue, and Compliance Alerts.
   - Actionable warning banners highlighting expired lots or low-stock items requiring restock.
   - Live activity feeds displaying recent sales and regulated dispensing events.
2. **📑 ERD & Data Dictionary** (`modules/schema_viewer.py`):
   - Vector Crow's Foot ERD rendering with an interactive **"🌙 Dark Slate (Matches UI)"** vs **"☀️ Clean Light Canvas"** toggle.
   - Searchable Data Dictionary detailing attributes, primary/foreign keys, PostgreSQL data types, nullability, and operational descriptions for all 11 tables.
   - One-click SVG diagram download buttons.
3. **🗃️ Database Tables Browser** (`modules/tables_browser.py`):
   - Live inspection of all 11 database relations directly from Neon PostgreSQL.
   - Global multi-column text filtering and record count metrics.
   - One-click CSV export for any selected relation.
   - Expandable raw SQL DDL schema viewer.
4. **📝 Data Entry & POS Forms** (`modules/forms.py`):
   - **Add New Drug**: Catalog registration with pharmacological category and reorder thresholds.
   - **Receive Stock Batch**: Inbound delivery logging with manufacturer lot codes and FEFO expiration dates.
   - **Point of Sale (POS) Checkout**: Automated 18% VAT calculation (`SubTotal * 0.18`), atomic stock balance decrement (`QuantityRemaining - %s`), and instant prescription dispensing registration.
   - **Record Operating Expense**: Audited operational expense logging with category selection.
   - **Staff Member Registration**: Secure staff onboarding with role check validation.
5. **🔍 SQL Query Explorer** (`modules/queries_runner.py`):
   - Tabbed execution for all coursework queries: Inventory (PIMS-6), Purchasing (PIMS-7), Sales (PIMS-8), Finance (PIMS-9).
   - Dynamic parameter controls (slider for expiry window days, top supplier limit slider, PO status filters, minimum spend thresholds).
   - Latency timer (ms), formatted Pandas DataFrames, CSV export, and raw SQL viewer.
   - **Interactive Custom SQL Console** allowing examiners to execute custom `SELECT` statements.
6. **📊 Graphical Reports & Analytics** (`modules/reports.py`):
   - **Monthly Profit & Loss (P&L)**: Plotly grouped bar chart comparing Gross Sales Revenue vs Operational Expenses vs Staff Payroll vs Net Profit with positive commercial profit margins.
   - **Sales Analytics**: Daily revenue trend line chart, payment channel distribution donut chart, and top 10 pharmaceuticals horizontal bar chart.
   - **Inventory Health & FEFO Expiry**: Lot risk classification pie chart (Expired, Near Expiry $\le$ 90 days, Expiring Soon, Adequate Shelf-Life) and stock valuation rankings.
   - **Official Printable Text Report**: Standardized, board-ready executive audit report with timestamps and one-click `.txt` download.

---

## 🚀 Installation & Local Setup

### Prerequisites
- Python 3.9 or higher.
- A Neon Serverless PostgreSQL database connection URL (or any PostgreSQL 14+ instance).
- Git installed on your local machine.

### Step 1: Clone Repository
```bash
git clone https://github.com/Spooky-Mallard/PIMS.git
cd PIMS/DBMS-PROJECT
```

### Step 2: Create and Activate Virtual Environment
```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Required Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Database Connection
Create a `.env` file inside the `DBMS-PROJECT/` directory (referencing `.env.example`):
```bash
cp backend/.env.example .env
```
Populate `.env` with your Neon PostgreSQL connection string:
```env
DATABASE_URL=postgresql://neondb_owner:YOUR_PASSWORD@ep-YOUR-PROJECT.us-east-2.aws.neon.tech/neondb?sslmode=require
```

### Step 5: Initialize Schema & Seed Data (Optional)
To create all 11 tables, 4 reporting views, and populate 348 coordinated records directly from the canonical SQL scripts:
```bash
python backend/init_db.py
```

### Step 6: Launch the Streamlit Application
```bash
# Standard Streamlit development server:
streamlit run app.py

# OR production server with custom Tornado health routes:
python server.py
```
Open your browser and navigate to: **`http://localhost:8501`**

---

## 🌐 Cloud Deployment (Render) & Health Keep-Alive API

The application includes production server hooks and HTTP health endpoints specifically tailored for zero-downtime deployment on [Render](https://render.com) and continuous uptime monitoring.

### 1. Render Web Service Configuration

You can deploy the application on Render either manually or automatically using the included `render.yaml` Blueprint.

#### Manual Dashboard Setup:
1. Log in to [Render Dashboard](https://dashboard.render.com/) and click **New + > Web Service**.
2. Connect your GitHub repository: `Spooky-Mallard/PIMS`.
3. Configure the following service settings:
   - **Name**: `sekarungi-pims`
   - **Environment**: `Python 3`
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python server.py`
   - **Health Check Path**: `/health` (or `/_stcore/health`)
4. Add the required Environment Variable:
   - `DATABASE_URL`: `postgresql://neondb_owner:YOUR_PASSWORD@ep-YOUR-PROJECT.us-east-2.aws.neon.tech/neondb?sslmode=require`

#### Blueprint Setup (One-Click):
Render will automatically detect the provided [render.yaml](file:///Users/spooky/Downloads/School/Database-Management-Systems/DBMS-PROJECT/render.yaml) blueprint file at the repository root and provision the service with optimized settings.

---

### 2. Available Health Check Endpoints

The server exposes four health check paths on the single HTTP port assigned by Render (`$PORT`):

| Endpoint | Method | Response Type | Description |
| :--- | :--- | :--- | :--- |
| **`/health`** | `GET` | `application/json` (HTTP 200/503) | **Primary Keep-Alive Endpoint.** Returns JSON system status and live Neon PostgreSQL connectivity check. |
| **`/api/health`** | `GET` | `application/json` (HTTP 200/503) | API alias for automated monitoring suites and uptime pingers. |
| **`/_stcore/health`** | `GET` | `text/html` (HTTP 200 `ok`) | Built-in Streamlit readiness probe used by cloud orchestrators. |
| **`/healthz`** | `GET` | `text/html` (HTTP 200 `ok`) | Kubernetes-standard health probe. |

#### Sample Response (`GET /health` or `GET /api/health`):
```json
{
  "status": "healthy",
  "service": "Sekarungi PIMS",
  "database": {
    "connected": true,
    "engine": "neondb",
    "host": "neon.tech"
  }
}
```

---

### 3. Preventing Render Free-Tier Spin-Down (24/7 Keep-Alive)

Render free-tier web services automatically spin down into "sleep mode" after **15 minutes** of HTTP inactivity. When a subsequent user visits, the application suffers a 30–60 second cold start.

To keep the application continuously warm and instantly responsive 24/7, configure an external automated pinger to send an HTTP `GET` request to your `/health` endpoint every **10 minutes**:

#### Option A: Free Uptime Monitoring Services (Recommended)
1. **[UptimeRobot](https://uptimerobot.com)** (Free):
   - Add New Monitor -> Type: `HTTP(s)`
   - Friendly Name: `Sekarungi PIMS Health`
   - URL: `https://your-service-name.onrender.com/health`
   - Monitoring Interval: `Every 5 minutes` or `Every 10 minutes`
2. **[Cron-job.org](https://cron-job.org)** (Free):
   - Create a cron job pointing to `https://your-service-name.onrender.com/health` scheduled every 10 minutes.
3. **[Better Stack / Better Uptime](https://betterstack.com)** (Free tier available).

#### Option B: GitHub Actions Scheduled Cron Workflow
An example GitHub Actions workflow is provided at [`.github/workflows/keep_alive.yml.example`](file:///Users/spooky/Downloads/School/Database-Management-Systems/DBMS-PROJECT/.github/workflows/keep_alive.yml.example).
To activate it:
```bash
cp .github/workflows/keep_alive.yml.example .github/workflows/keep_alive.yml
```
Update the `APP_URL` variable with your live Render URL, commit, and push. GitHub will automatically ping the `/health` endpoint every 10 minutes.

---

## 🧪 Database Verification & Query Testing

To verify database connectivity and check record counts across all 11 tables via raw Python:
```bash
python -c "
from backend.db import test_connection, fetch_dataframe
ok, info = test_connection()
print(f'Neon DB Status: {ok} | Engine: {info}')

tables = ['\"User\"', 'Supplier', 'Drug', 'StockBatch', 'PurchaseOrder', 'PurchaseOrderItem', 'Sale', 'SaleItem', 'DispensingRegister', 'Expense', 'Payroll']
for t in tables:
    count = fetch_dataframe(f'SELECT COUNT(*) FROM {t};').iloc[0, 0]
    print(f'  {t:<22}: {count:3d} records')
"
```

---

## 👥 Team & Contributors

This project was developed for the **BCS 2206 Database Management Systems** course at **Makerere University** by **Team PIMS**:

| Contributor | GitHub Handle | Role & Deliverables |
| :--- | :--- | :--- |
| **Matthew Mumbere** *(Lead)* | [@Spooky-Mallard](https://github.com/Spooky-Mallard) | Lead System Architecture, Raw SQL Driver (`backend/db.py`), App Shell (`app.py`), Executive Dashboard (`modules/dashboard.py`), and Financial Profit Modeling. |
| **Sabano Zubedah** | [@Angel-coder-max](https://github.com/Angel-coder-max) | Foundational Schema (`01_foundational_tables.sql`), Supplier Procurement Queries (`02_purchasing_queries.sql`), and Transaction Forms (`modules/forms.py`). |
| **Karen Nakibuuka** | [@Kar3n-N](https://github.com/Kar3n-N) | Sales & Dispensing Relations (`03_sales_dispensing_tables.sql`), Live Tables Browser (`modules/tables_browser.py`), and ERD Schema Viewer (`modules/schema_viewer.py`). |
| **Reagan Ankunda** | [@reaganankunda4-alt](https://github.com/reaganankunda4-alt) | Financial Schema (`04_financial_tables.sql`), Accounting & Payroll Queries (`04_finance_queries.sql`), Query Explorer (`modules/queries_runner.py`), and Graphical Reports (`modules/reports.py`). |

---

## 📜 Git & Workflow Strategy

- **Production Branch (`main`)**: Verified, production-ready code for deployment.
- **Integration Branch (`dev`)**: Continuous integration branch where all tested pull requests are merged.
- **Feature Branches (`feature/<name>`)**: Isolated branches for specific components and deliverables.
- **Strict Merging Protocol**:
  - All pull requests must be merged using regular merge commits: `gh pr merge <PR> --merge`.
  - **Rebase and squash merges are strictly forbidden** to preserve complete academic commit history and individual member contributions.

---

## ⚖️ License & Academic Notice

This project was developed for academic evaluation purposes in the Department of Computer Science, Makerere University. All dummy data is synthetically generated for Sekarungi Pharmaceuticals Ltd and does not represent confidential medical patient records.
