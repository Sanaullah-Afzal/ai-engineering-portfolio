# Cold Chain Logistics FDE Setup & Execution Guide

This document covers the end-to-end setup, data ingestion, security view configuration, vector DB synchronization, agent testing, and audit log setup for the Cold Chain Logistics FDE system.

---

## Phase 0: Infrastructure & Data Ingestion

### 1. Database & Docker Container Setup
- **Dataset Location:** Ensure the source dataset is downloaded at `data/source/data.txt`.
- **MSSQL Docker Instance:** Spin up the legacy SQL Server container using Docker (locally or on an AWS EC2 instance).

#### Docker Run Commands

* **Single-line Execution:**
  ```bash
  docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=FdeEnterprisePass123!" -p 1433:1433 --name legacy-mssql -d mcr.microsoft.com/mssql/server:2022-latest
  ```

* **Multi-line Execution (Windows PowerShell / CMD):**
  ```cmd
  docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=FdeEnterprisePass123!" ^
     -p 1433:1433 --name legacy-mssql ^
     -d mcr.microsoft.com/mssql/server:2022-latest
  ```

* **Multi-line Execution (Unix / Linux / macOS):**
  ```bash
  docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=FdeEnterprisePass123!" \
     -p 1433:1433 --name legacy-mssql \
     -d mcr.microsoft.com/mssql/server:2022-latest
  ```

* **Multi-line Execution with Persistent Volume (Recommended for EC2 / Production):**
  > *Maps a Docker named volume to the internal SQL Server data directory to ensure data persists even if the container stops or crashes.*

  ```bash
  docker run -v mssql_data:/var/opt/mssql \
    -e "ACCEPT_EULA=Y" \
    -e "MSSQL_SA_PASSWORD=FdeEnterprisePass123!" \
    -p 1433:1433 \
    --name legacy-mssql \
    -d mcr.microsoft.com/mssql/server:2022-latest
  ```

---

### 2. Dependencies & Ingestion Execution
1. Ensure the ODBC Driver 18 for SQL Server is installed on your local host environment.
2. Install project dependencies:
   ```bash
   uv add -r .\requirements.txt
   ```
3. Run the ingestion script:
   ```bash
   python scripts\ingest_legacy_data.py
   ```

---

### 3. Database Connection Configuration

#### Tools Required
- **Azure Data Studio:** [Download Azure Data Studio](https://learn.microsoft.com/en-us/previous-versions/azure-data-studio/download-azure-data-studio?tabs=win-install%2Cwin-user-install%2Credhat-install%2Cwindows-uninstall%2Credhat-uninstall)
- **VS Code Extension (Recommended):** `SQL Server (mssql)` by Microsoft (use the server icon, not the cylinder icon).

#### Admin Connection Settings (`sa` profile)
* **Profile Name:** `legacy-mssql`
* **Server Name:** `localhost`
* **Port:** `1433`
* **Trust Server Certificate:** 🟩 **Enabled / Checked** *(Crucial for Docker connections)*
* **Authentication Type:** `SQL Login`
* **User Name:** `sa`
* **Password:** `FdeEnterprisePass123!`
* **Save Password:** 🟩 **Checked**
* **Database Name:** `master` (or select from database list)
* **Encrypt:** ⚠️ **Optional** (or `False`)

#### Validation Query
Open a new query window (`Ctrl + N`) and run:
```sql
SELECT COUNT(*) AS total_rows FROM dbo.TBL_SC_FLEET_HIST_RAW;
```

---

## Phase 1: Vector Database & SOP Ingestion

1. Log in to [Pinecone Console](https://app.pinecone.io/) and generate an API key.
2. Add your Pinecone API key to the project `.env` file:
   ```env
   PINECONE_API_KEY=your_pinecone_api_key_here
   ```
3. Ingest the Compliance SOP vector embeddings:
   ```bash
   python scripts\ingest_sop_pinecone.py
   ```

---

## Phase 2: Data Security & Read-Only Agent Profile

1. Open `scripts/setup_security_and_view.sql` in VS Code and execute the query using the `sa` profile.
2. Create a new database connection in VS Code / Azure Data Studio for the restricted agent profile:

#### Agent Profile Connection Settings (`USR_FDE_RO`)
* **Profile Name:** `agent-fde-ro`
* **Input Type:** `Parameters`
* **Server Name:** `localhost`
* **Port:** `1433`
* **Trust Server Certificate:** 🟩 **Enabled / Checked**
* **Authentication Type:** `SQL Login`
* **User Name:** `USR_FDE_RO`
* **Password:** `AgentPassword2026!`
* **Save Password:** 🟩 **Checked**
* **Database Name:** `master`
* **Encrypt:** **Optional** (or `False`)

#### Security Validation Queries

```sql
-- TEST 1: MUST SUCCEED (Read access granted to security view)
SELECT TOP 5 * FROM FDE_VIEWS.VW_ACTIVE_FLEET;

-- TEST 2: MUST FAIL (Direct table access denied)
SELECT TOP 5 * FROM dbo.TBL_SC_FLEET_HIST_RAW;
```

---

## Phase 3: Agent Orchestration Testing

Run the background tool bindings and execution engine:
```bash
python src\agent_tools.py
python src\orchestrator.py
```

### Dispatcher Test Cases

* **Test Case 1: The "Domino Effect" Test (Tool-Calling Orchestration)**
  > *"Find any active shipments near Los Angeles (Latitude ~33.8, Longitude ~-118.1). Check the local weather there, and tell me if the current cargo temperature violates the SOP for fresh perishables."*

* **Test Case 2: The "Restraint" Test (Direct Knowledge Routing)**
  > *"I'm a new dispatcher on the night shift. Can you quickly explain the difference between a Tier 1 and Tier 2 escalation?"*

---

## Phase 4: Agent Audit Logging Setup

Connect using the admin (`sa`) user, open a new SQL editor tab, and create the audit logging table and permission grant:

```sql
-- Create Audit Log table under security schema
CREATE TABLE FDE_VIEWS.AgentAuditLog (
    LogID INT IDENTITY(1,1) PRIMARY KEY,
    Timestamp DATETIME DEFAULT GETDATE(),
    SessionID VARCHAR(50),
    NodeExecuted VARCHAR(50),
    ToolName VARCHAR(100),
    Content NVARCHAR(MAX) -- Safely stores JSON payloads and LLM outputs
);

-- Grant write-only permission on the audit log table to the agent user
GRANT INSERT ON FDE_VIEWS.AgentAuditLog TO USR_FDE_RO;
```

---

## Phase 5: Streamlit Web UI Launch

Launch the interactive dashboard UI for real-time fleet monitoring and agent interaction:

```bash
streamlit run src\ui.py
```