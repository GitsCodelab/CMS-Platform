# CMS Platform

A comprehensive content management system with dual-database support (Oracle XE & PostgreSQL), built with FastAPI backend and React/Bootstrap frontend, orchestrated with Apache Airflow.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.12+ (for local backend development)
- Linux/WSL2 environment recommended

### Startup with Docker Compose

```bash
# Start all services in background
docker compose up -d

# View logs (optional)
docker compose logs -f

# Verify all containers are running
docker compose ps

# Stop all services
docker compose down
```

### Access Points

| Service | URL | Default Credentials |
|---------|-----|-------------------|
| **Frontend (React)** | http://localhost:3000 | - |
| **Backend API** | http://localhost:8000 | - |
| **Airflow UI** | http://localhost:8080 | airflow / airflow |
| **WSO2 APIM Admin** | https://localhost:9443/admin | admin / admin |
| **WSO2 APIM Publisher** | https://localhost:9443/publisher | admin / admin |
| **WSO2 APIM Developer** | https://localhost:9443/devportal | - |
| **APIM Gateway (HTTP)** | http://localhost:8280 | - |
| **APIM Gateway (HTTPS)** | https://localhost:8243 | - |
| **Oracle Database** | localhost:1521/xepdb1 | sys / oracle |
| **PostgreSQL** | localhost:5432/cms | postgres / postgres |

---

## 📱 Frontend - React with Bootstrap

### Status
✅ **Frontend is fully operational and accessible at http://localhost:3000**

### Overview

The frontend is a modern React application built with:
- **React 18.2.0** - UI framework
- **Vite 5.4.21** - Build tool for fast development
- **Bootstrap 5.3.0** - CSS framework for professional styling
- **Axios 1.15.0** - HTTP client for API communication

**Recent Fixes:**
- ✅ Fixed PostCSS configuration error (removed unused tailwindcss plugin)
- ✅ Corrected Docker port mapping (3000 instead of 3001)
- ✅ Frontend now starts successfully and serves on http://localhost:3000

### Architecture

```
frontend/
├── src/
│   ├── components/
│   │   ├── MainLayout.jsx       # Main app layout with sidebar menu
│   │   ├── TestDatabase.jsx     # Database management page
│   │   ├── DataTable.jsx        # Reusable data table component
│   │   └── RecordForm.jsx       # CRUD form component
│   ├── hooks/
│   │   ├── useOracle.js         # Custom hook for Oracle operations
│   │   └── usePostgres.js       # Custom hook for PostgreSQL operations
│   ├── api/
│   │   └── client.js            # Axios HTTP client configuration
│   ├── App.jsx                  # Root component
│   ├── index.css                # Global styles
│   └── main.jsx                 # Entry point
├── index.html                   # HTML template
├── package.json                 # Dependencies
├── vite.config.js               # Vite configuration
└── tailwind.config.js           # Tailwind CSS configuration
```

### Features

**Main Menu Navigation:**
- 🧪 **Test** - Database management tools
  - Database Management - CRUD operations on Oracle & PostgreSQL
- ⚙️ **Settings** - Configuration options (placeholder)
- 📊 **Reports** - Data visualization & exports (placeholder)
- ❓ **Help** - Documentation & FAQ (placeholder)

**Database Management:**
- **Tab-based interface** for Oracle & PostgreSQL databases
- **Data table** with edit/delete actions
- **Add/Edit form** with validation
- **Delete confirmation modal** for safety
- **Real-time data sync** with backend API
- **Error handling** and user feedback
- **Responsive design** for desktop and tablet

**UI Features:**
- ☰ **Collapsible sidebar** for more content space
- 🎨 **Light theme** with professional blue accents
- 📱 **Responsive layout** using Bootstrap grid system
- ⌨️ **Keyboard-friendly** form controls

### Local Development Setup

#### 1. Install Dependencies

```bash
cd frontend
npm install --legacy-peer-deps
```

#### 2. Start Development Server

```bash
npm run dev
```

Access at http://localhost:3000

The dev server includes:
- Hot module replacement (HMR) for instant updates
- Vite's fast build system
- Proxy to backend API (`/api` → http://localhost:8000)

#### 3. Build for Production

```bash
npm run build
```

Creates optimized bundle in `dist/` directory.

#### 4. Preview Production Build

```bash
npm run preview
```

### How to Use the Frontend

#### 1. Database Management (Main Feature)

**Accessing Database Management:**
1. Click "🧪 Test" menu item
2. Click "Database Management" submenu
3. View existing records in the table

**Viewing Data:**
- **Oracle Database Tab** - Shows records from Oracle XE
- **PostgreSQL Database Tab** - Shows records from PostgreSQL DWH
- Click tabs to switch between databases
- Table displays: ID, Name, Description, Status

**Adding New Record:**
1. Click "+ Add New" button
2. Fill in the form:
   - **ID** - Unique identifier (required)
   - **Name** - Record name (required)
   - **Description** - Additional details (optional)
   - **Status** - active/inactive (default: active)
3. Click "Save" to submit
4. Success/error message displayed
5. Table refreshes automatically

**Editing Record:**
1. Click "Edit" button on any table row
2. Form populates with record data
3. ID field is disabled (cannot change primary key)
4. Update Name, Description, or Status
5. Click "Save" to submit
6. Table updates automatically

**Deleting Record:**
1. Click "Delete" button on any table row
2. Confirmation modal appears
3. Click "Delete" to confirm or "Cancel" to abort
4. Record removed from database
5. Table refreshes automatically

**Menu Toggle:**
- Click "☰" button in header to collapse sidebar
- Click "▶" button to expand sidebar
- Useful for viewing more content on smaller screens

#### 2. API Integration

The frontend communicates with the backend API:

```javascript
// Oracle Database endpoints
GET    /oracle/test         // Get all records
GET    /oracle/test/{id}    // Get single record
POST   /oracle/test         // Create record
PUT    /oracle/test/{id}    // Update record
DELETE /oracle/test/{id}    // Delete record

// PostgreSQL Database endpoints
GET    /postgres/test       // Get all records
GET    /postgres/test/{id}  // Get single record
POST   /postgres/test       // Create record
PUT    /postgres/test/{id}  // Update record
DELETE /postgres/test/{id}  // Delete record
```

Request/Response Format:
```javascript
// Create/Update Request
{
  "id": "1",
  "name": "Test Record",
  "description": "Sample description",
  "status": "active"
}

// Response
{
  "id": "1",
  "name": "Test Record",
  "description": "Sample description",
  "status": "active"
}
```

#### 3. Troubleshooting

**Issue: Frontend won't load**
- Solution: Ensure backend is running: `docker compose up -d`
- Check: http://localhost:8000/health

**Issue: API calls fail (CORS error)**
- Solution: Backend CORSMiddleware is enabled (allow_origins=["*"])
- Check: http://localhost:8000/oracle/test

**Issue: Data not showing**
- Solution: Check browser console for errors (F12 → Console tab)
- Verify: Test data exists in databases

**Issue: Form validation error**
- Solution: Ensure ID and Name are filled (both required)
- Try: Clear form and try again

**Issue: Menu not collapsing**
- Solution: Click "☰" button in header to toggle sidebar
- Works on all page transitions

### Component Documentation

#### MainLayout.jsx
- Main application container
- Sidebar navigation with menu items
- Header with page title and menu toggle
- Routes content to appropriate component

#### TestDatabase.jsx
- Database management page
- Tab switching between Oracle/PostgreSQL
- Displays DataTable component
- Manages RecordForm visibility
- Handles delete confirmation logic

#### DataTable.jsx
- Reusable table component
- Displays records in Bootstrap table
- Edit/Delete action buttons
- Loading spinner while fetching
- "No records found" message when empty

#### RecordForm.jsx
- CRUD form component
- Bootstrap form controls
- Client-side validation (ID, Name required)
- Dynamic form for add/edit operations
- Submit/Cancel buttons with loading state

#### Hooks (useOracle.js, usePostgres.js)
- Custom React hooks for database operations
- State management: records, loading, error
- Methods: fetchRecords, createRecord, updateRecord, deleteRecord
- Handles API communication with error handling

#### API Client (client.js)
- Axios HTTP client configuration
- Base URL: http://localhost:8000 (development)
- Headers: application/json
- Exports: oracleAPI, postgresAPI objects with CRUD methods

### Styling with Bootstrap

The frontend uses **Bootstrap 5.3.0** CSS framework:

**Key Bootstrap Classes Used:**
- Grid: `d-flex`, `container`, `row`, `col-lg-*`
- Forms: `form-control`, `form-label`, `form-select`
- Buttons: `btn`, `btn-primary`, `btn-success`, `btn-danger`
- Tables: `table`, `table-striped`, `table-hover`
- Navigation: `nav`, `nav-tabs`, `nav-item`, `nav-link`
- Modals: `modal`, `modal-dialog`, `modal-content`
- Alerts: `alert`, `alert-danger`, `alert-info`

**Color Scheme:**
- Primary Blue: #2563eb
- Light Blue Background: #f0f3ff
- Success Green: #28a745
- Danger Red: #dc3545
- Light Gray: #f8f9fa

### Deployment

**Docker Deployment:**
The frontend is automatically deployed via Docker Compose:

```yaml
cms-frontend:
  image: node:18-alpine
  container_name: cms-frontend
  working_dir: /app
  command: sh -c "npm install && npm run dev"
  depends_on:
    cms-backend:
      condition: service_started
  volumes:
    - ./frontend:/app
    - /app/node_modules
  ports:
    - "3000:3000"
  environment:
    - VITE_API_URL=http://cms-backend:8000
  networks:
    - cms-platform-net
```

---

## 🔧 FastAPI Backend

### Overview

The backend provides a RESTful API for CRUD operations on both Oracle and PostgreSQL databases.

### Architecture

```
backend/
├── app/
│   ├── __init__.py              # FastAPI app factory and router registration
│   ├── config.py                # Configuration and environment variables
│   ├── database/
│   │   ├── oracle.py            # Oracle database operations
│   │   └── postgres.py          # PostgreSQL database operations
│   ├── routers/
│   │   ├── oracle.py            # Oracle API endpoints
│   │   └── postgres.py          # PostgreSQL API endpoints
│   └── schemas/
│       └── test.py              # Pydantic request/response models
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
└── .env                         # Environment variables
```

### FastAPI Endpoints

#### Health Check
```
GET /health
Response: {"status": "healthy", "api": "CMS Platform API", "version": "1.0.0"}
```

#### Oracle Endpoints
```
GET    /oracle/test              # Get all records
GET    /oracle/test/{id}         # Get record by ID
POST   /oracle/test              # Create new record
PUT    /oracle/test/{id}         # Update record
DELETE /oracle/test/{id}         # Delete record
```

#### PostgreSQL Endpoints
```
GET    /postgres/test            # Get all records
GET    /postgres/test/{id}       # Get record by ID
POST   /postgres/test            # Create new record
PUT    /postgres/test/{id}       # Update record
DELETE /postgres/test/{id}       # Delete record
```

### Backend Development

#### Local Setup

```bash
# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Run development server
cd backend && python run.py
```

#### Environment Variables (.env)

```env
# Oracle Configuration
ORACLE_HOST=localhost
ORACLE_PORT=1521
ORACLE_SERVICE=xepdb1
ORACLE_USER=cms_user
ORACLE_PASSWORD=oracle

# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=cms
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

---

## 🗄️ Database Setup

### Oracle XE

**Connection:**
- Host: cms-oracle-xe:1521
- Service: xepdb1
- Admin User: sys (password: oracle)

**Test Data Table:**
```sql
CREATE TABLE test (
  ID NUMBER PRIMARY KEY,
  NAME VARCHAR2(255) NOT NULL,
  DESCRIPTION VARCHAR2(500),
  STATUS VARCHAR2(50)
);
```

### PostgreSQL

**Connection:**
- Host: cms-postgresql:5432
- Database: cms
- User: postgres (password: postgres)

**Test Data Table:**
```sql
CREATE TABLE test (
  ID SERIAL PRIMARY KEY,
  NAME VARCHAR(255) NOT NULL,
  DESCRIPTION VARCHAR(500),
  STATUS VARCHAR(50)
);
```

---

## 📊 Data Orchestration (Airflow)

### Accessing Airflow
- **URL:** http://localhost:8080
- **Username:** airflow
- **Password:** airflow

### DAGs Available
- `hello_test` - Basic test DAG
- `hello_bash` - Bash operator example
- `test_oracle` - Oracle database test
- `test_connections` - Connection testing

### Database Connection

Airflow uses PostgreSQL for metadata storage:
```
Host: cms-postgresql
Port: 5432
User: postgres
Password: postgres
Database: cms
```

Connection URI: `postgresql+psycopg2://postgres:postgres@cms-postgresql:5432/cms`

### Authentication

SimpleAuthManager is configured with:
- **Default User:** airflow
- **Default Password:** airflow

---

## 📦 Docker Compose Services

| Service | Image | Port | Description |
|---------|-------|------|-------------|
| cms-frontend | node:18-alpine | 3000 | React frontend with Vite |
| cms-backend | python:3.12-slim | 8000 | FastAPI REST API |
| cms-oracle-xe | gvenzl/oracle-xe:21.3.0 | 1521 | Oracle database |
| cms-postgresql | postgres:15.3 | 5432 | PostgreSQL database |
| cms-airflow | apache/airflow:3.0.0 | 8080 | Airflow orchestration |
| cms-apim | wso2/wso2am:4.3.0 | 8280, 8243, 9443, 9611 | WSO2 API Manager gateway |

---

## 🌐 WSO2 API Manager (APIM)

### Overview

WSO2 API Manager is an enterprise-grade API management platform that provides centralized API governance, security, and monetization.

### Quick Start

**Access WSO2 APIM:**

1. **Add `apim.local` to your hosts file** (on your client machine):
   ```bash
   # Linux/Mac
   echo "127.0.0.1 apim.local" | sudo tee -a /etc/hosts
   
   # Windows (run as Administrator)
   Add "127.0.0.1 apim.local" to C:\Windows\System32\drivers\etc\hosts
   ```

2. **Access using hostname:**
   ```
   Admin Console:      https://apim.local:9443/admin
   Publisher Portal:   https://apim.local:9443/publisher
   Developer Portal:   https://apim.local:9443/devportal
   API Gateway (HTTP):  http://apim.local:8280
   API Gateway (HTTPS): https://apim.local:8243
   ```
   
   **Alternative (without hostname):**
   ```
   Admin Console:      https://localhost:9443/admin
   Publisher Portal:   https://localhost:9443/publisher
   Developer Portal:   https://localhost:9443/devportal
   API Gateway (HTTP):  http://localhost:8280
   API Gateway (HTTPS): https://localhost:8243
   ```

**Default Credentials:**
- Username: `admin`
- Password: `admin`

**Note:** Accept the self-signed SSL certificate on first access.

### Features

✅ **API Gateway**
- Request/response mediation and transformation
- Policy enforcement (throttling, authentication, CORS)
- Traffic shaping and rate limiting
- Request/response logging and analytics
- Full API lifecycle management

✅ **Publisher Portal**
- Create and publish APIs
- Manage API versions and endpoints
- Apply policies and security measures
- Monitor API usage and performance
- Configure OAuth2 scopes

✅ **Developer Portal**
- Browse and discover published APIs
- Subscribe to APIs and manage subscriptions
- Generate and manage API keys
- View API documentation and samples
- Monitor own API usage

✅ **Security**
- OAuth2 authentication and authorization
- API key management
- Rate limiting and throttling
- Request validation
- Data transformation and masking

✅ **PostgreSQL Backend** (Production Ready)
- Persistent data storage using PostgreSQL
- 252 database tables for full API management
- User management and authentication store
- API registry and subscription tracking
- Audit logs and analytics data

### Architecture

```
wso2-stack/apim/
├── README.md                    # Quick start guide
├── API_REGISTRATION.md          # Step-by-step API registration
├── COMPLETE_API_REGISTRATION_GUIDE.md  # Comprehensive API registration guide
├── POLICIES.md                  # Policy configuration guide
├── PRODUCTION.md                # Production deployment guide
├── APIM_INTEGRATION.md          # WSO2 stack integration notes
├── Dockerfile                   # APIM container image (includes PostgreSQL JDBC driver)
├── docker-compose.yml           # APIM Docker service definition
├── deployment.toml              # APIM configuration with PostgreSQL backend
├── .env                         # Environment configuration
├── start.sh                     # Quick start script
└── cms-api-definition.json      # OpenAPI/Swagger definition for CMS APIs
```

**APIM Database Schema:**
- **Location:** PostgreSQL `wso2am` database
- **Total Tables:** 252 (51 core + 201 APIM-specific)
- **Core Tables:** User management, registry, permissions, domains
- **APIM Tables:** APIs, subscriptions, policies, gateway configurations
- **Initialization:** Automatic via SQL scripts on first startup (manual if needed)

### Configuration

**APIM Hostname Configuration:**

The APIM is configured with hostname `apim.local` for modern API gateway patterns:

```toml
# deployment.toml - Server Configuration
[server]
hostname = "apim.local"           # API Gateway hostname
base_path = "https://apim.local:9443"
server_name = "WSO2 API Manager"
```

**PostgreSQL Database Configuration:**

```toml
# deployment.toml - Database Configuration
[database.identity_db]
type = "postgresql"
url = "jdbc:postgresql://cms-postgresql:5432/wso2am"
username = "postgres"
password = "postgres"
driver = "org.postgresql.Driver"

[database.shared_db]
type = "postgresql"
url = "jdbc:postgresql://cms-postgresql:5432/wso2am"
username = "postgres"
password = "postgres"
driver = "org.postgresql.Driver"

[database.apim_db]
type = "postgresql"
url = "jdbc:postgresql://cms-postgresql:5432/wso2am"
username = "postgres"
password = "postgres"
driver = "org.postgresql.Driver"
```

**Environment Variables:**
```env
# Database Configuration
DB_TYPE=postgresql                  # Database type (PostgreSQL)
DB_HOSTNAME=cms-postgresql          # PostgreSQL host
DB_PORT=5432                        # PostgreSQL port
DB_NAME=wso2am                      # Database name
DB_USERNAME=postgres                # DB username
DB_PASSWORD=postgres                # DB password

# APIM Admin Configuration
ADMIN_USERNAME=admin                # APIM admin user
ADMIN_PASSWORD=admin                # APIM admin password

# Gateway Configuration
API_GATEWAY_HOST=apim.local         # Gateway hostname (or localhost)
API_GATEWAY_HTTP_PORT=8280          # Gateway HTTP port
API_GATEWAY_HTTPS_PORT=8243         # Gateway HTTPS port
ADMIN_CONSOLE_PORT=9443             # Admin console HTTPS port
```

**PostgreSQL JDBC Driver:**
- **Version:** 42.5.0
- **Location in Container:** `/home/wso2carbon/wso2am-4.3.0/lib/postgresql-42.5.0.jar`
- **Status:** Automatically included in Docker image build
- **Configuration:** Located in Dockerfile via curl download

### Database Schema Initialization

**Automatic Initialization (Docker Startup):**
When APIM starts for the first time with PostgreSQL backend, the schema is automatically initialized through database initialization scripts located in the container.

**Manual Initialization (if needed):**
If the database schema needs to be manually created:

```bash
# Initialize core WSO2 Carbon schema (51 tables)
cd /home/samehabib/CMS-Platform
docker compose exec cms-apim cat /home/wso2carbon/wso2am-4.3.0/dbscripts/postgresql.sql | \
  docker compose exec -T cms-postgresql psql -U postgres wso2am

# Initialize APIM-specific schema (201 tables)
docker compose exec cms-apim cat /home/wso2carbon/wso2am-4.3.0/dbscripts/apimgt/postgresql.sql | \
  docker compose exec -T cms-postgresql psql -U postgres wso2am

# Verify schema creation
docker compose exec cms-postgresql psql -U postgres wso2am -c \
  "SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = 'public';"
```

**Expected Result:**
```
 table_count
-------------
         252
```

**Database Tables Created:**
- **Core User Store (51 tables):** um_domain, um_user, um_role, reg_resource, reg_path, etc.
- **APIM Gateway (201 tables):** am_api, am_api_resource, am_gateway_config, am_subscription, etc.

### Registering CMS APIs

**Step 1: Access Publisher Portal**
1. Open https://apim.local:9443/publisher (or https://localhost:9443/publisher)
2. Login with admin credentials (admin / admin)
3. Accept SSL certificate warning (self-signed)

### Registering CMS Backend API

**Quick Reference:**

| Step | Action |
|------|--------|
| 1 | Access Publisher: https://apim.local:9443/publisher (or localhost:9443) with admin/admin |
| 2 | Click **Create** → **Design a new REST API** |
| 3 | Enter Name: `CMS Test API`, Context: `/cms`, Backend: `http://cms-backend:8000` |
| 4 | Add Resources: `/oracle/test`, `/postgres/test`, `/health` |
| 5 | Configure endpoints and apply OAuth2 + throttling policies |
| 6 | Click **Publish** |
| 7 | Gateway endpoints available at: `https://apim.local:8243/cms/1.0.0/` (or localhost:8243) |

**For Complete Step-by-Step Instructions:**

See **[wso2-stack/apim/COMPLETE_API_REGISTRATION_GUIDE.md](wso2-stack/apim/COMPLETE_API_REGISTRATION_GUIDE.md)** with:
- Detailed screenshots and workflows
- API testing examples (cURL, Postman, API try-it-out)
- Frontend integration code samples
- OAuth2 token generation
- Troubleshooting guide
- Production best practices

**Key Endpoints After Registration:**

```
# Using apim.local hostname (recommended)
# Oracle Test API
GET    https://apim.local:8243/cms/1.0.0/oracle/test
GET    https://apim.local:8243/cms/1.0.0/oracle/test/{id}
POST   https://apim.local:8243/cms/1.0.0/oracle/test
PUT    https://apim.local:8243/cms/1.0.0/oracle/test/{id}
DELETE https://apim.local:8243/cms/1.0.0/oracle/test/{id}

# PostgreSQL Test API
GET    https://apim.local:8243/cms/1.0.0/postgres/test
GET    https://apim.local:8243/cms/1.0.0/postgres/test/{id}
POST   https://apim.local:8243/cms/1.0.0/postgres/test
PUT    https://apim.local:8243/cms/1.0.0/postgres/test/{id}
DELETE https://apim.local:8243/cms/1.0.0/postgres/test/{id}

# Health Check
GET    https://apim.local:8243/cms/1.0.0/health

# Alternative using localhost
# Replace apim.local with localhost in all URLs above
```

**Quick Test with cURL:**

```bash
# 1. Generate OAuth2 token
TOKEN=$(curl -s -X POST "https://apim.local:9443/oauth2/token" \
  -H "Authorization: Basic YWRtaW46YWRtaW4=" \
  -d "grant_type=client_credentials" \
  -k | jq -r '.access_token')

# 2. Test the API
curl -X GET "https://apim.local:8243/cms/1.0.0/oracle/test" \
  -H "Authorization: Bearer $TOKEN" \
  -k -s | jq '.'

# 3. Create a new record
curl -X POST "https://apim.local:8243/cms/1.0.0/oracle/test" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "name": "APIM Test Record",
    "description": "Created through API Manager",
    "status": "active"
  }' \
  -k -s | jq '.'

# Note: Replace apim.local with localhost if hostname is not configured
```

**Update Frontend to Use APIM:**

**Step 1: Update `frontend/src/api/client.js`**

```javascript
import axios from 'axios';

// Use APIM gateway instead of direct backend
const apiClient = axios.create({
  baseURL: 'https://apim.local:8243/cms/1.0.0',  // or localhost:8243 if hostname not configured
  timeout: 5000,
  httpsAgent: {
    rejectUnauthorized: false  // For development only!
  }
});

// Inject API Key or OAuth2 token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

export const oracleAPI = {
  getAll: () => apiClient.get('/oracle/test'),
  getById: (id) => apiClient.get(`/oracle/test/${id}`),
  create: (data) => apiClient.post('/oracle/test', data),
  update: (id, data) => apiClient.put(`/oracle/test/${id}`, data),
  delete: (id) => apiClient.delete(`/oracle/test/${id}`)
};

export const postgresAPI = {
  getAll: () => apiClient.get('/postgres/test'),
  getById: (id) => apiClient.get(`/postgres/test/${id}`),
  create: (data) => apiClient.post('/postgres/test', data),
  update: (id, data) => apiClient.put(`/postgres/test/${id}`, data),
  delete: (id) => apiClient.delete(`/postgres/test/${id}`)
};

export default apiClient;
```

**Step 2: Generate Access Token**

In frontend, after getting access token from APIM:

```javascript
// Store token for API calls
const token = response.data.access_token;
localStorage.setItem('accessToken', token);
```

### Troubleshooting APIM with PostgreSQL

**Issue 1: ClassNotFoundException: org.postgresql.Driver**

Error in logs:
```
ClassNotFoundException: org.postgresql.Driver
```

Cause: PostgreSQL JDBC driver is not present in APIM container classpath

Solution:
- Ensure Dockerfile includes JDBC driver download:
  ```dockerfile
  RUN cd /home/wso2carbon/wso2am-4.3.0/lib && \
      curl -L -o postgresql-42.5.0.jar https://jdbc.postgresql.org/download/postgresql-42.5.0.jar && \
      chmod 644 postgresql-42.5.0.jar
  ```
- Rebuild APIM image: `docker compose build --no-cache cms-apim`
- Restart APIM: `docker compose restart cms-apim`

**Issue 2: ERROR: relation 'um_domain' does not exist**

Error in logs:
```
PSQLException: ERROR: relation 'um_domain' does not exist
```

Cause: Database schema is not initialized. WSO2 APIM does NOT auto-create PostgreSQL schema on first startup (unlike embedded H2 database)

Solution:
- Manually initialize the database schema (see **Database Schema Initialization** section above)
- Run the two SQL scripts in order:
  1. `postgresql.sql` (core WSO2 tables)
  2. `apimgt/postgresql.sql` (APIM-specific tables)
- Restart APIM after schema creation

**Issue 3: apim.local hostname not resolving**

Error in browser:
```
Cannot reach apim.local
```

Cause: Hostname not added to client machine's hosts file

Solution:
- Add entry to `/etc/hosts` (Linux/Mac) or `C:\Windows\System32\drivers\etc\hosts` (Windows):
  ```
  127.0.0.1 apim.local
  ```
- Use alternative: `https://localhost:9443` instead of `https://apim.local:9443`

**Issue 4: Connection refused on port 8280, 8243, or 9443**

Error in browser:
```
Connection refused
```

Cause: APIM container not running or ports not mapped correctly

Solution:
- Check container status: `docker compose ps cms-apim`
- View logs: `docker compose logs cms-apim`
- If container is exiting, check for JDBC driver or schema errors (Issues 1-2)
- Verify ports in docker-compose.yml are published correctly

**Issue 5: Database connection pool error**

Error in logs:
```
Failed to obtain JDBC Connection
PSQLException: Connection to localhost:5432 refused
```

Cause: PostgreSQL container is not running or not accessible from APIM container

Solution:
- Ensure PostgreSQL is running: `docker compose ps cms-postgresql`
- Check containers are on same network: `docker network inspect cms-platform_cms-platform-net`
- Verify database credentials in deployment.toml match PostgreSQL configuration
- Restart both services: `docker compose restart cms-postgresql cms-apim`

### Documentation & Guides

For detailed information, see:
- **[wso2-stack/apim/COMPLETE_API_REGISTRATION_GUIDE.md](wso2-stack/apim/COMPLETE_API_REGISTRATION_GUIDE.md)** - ⭐ **START HERE** - Complete step-by-step guide with all details
- **[wso2-stack/apim/README.md](wso2-stack/apim/README.md)** - APIM overview and quick start
- **[wso2-stack/apim/API_REGISTRATION.md](wso2-stack/apim/API_REGISTRATION.md)** - Additional API registration tips
- **[wso2-stack/apim/POLICIES.md](wso2-stack/apim/POLICIES.md)** - Policy configuration and security
- **[wso2-stack/apim/PRODUCTION.md](wso2-stack/apim/PRODUCTION.md)** - Production deployment checklist

### Docker Commands

```bash
# Start all services
docker compose up -d

# Start specific service
docker compose up -d cms-apim
docker compose up -d cms-backend
docker compose up -d cms-frontend

# View logs
docker compose logs -f [service-name]

# Stop services
docker compose down

# Restart specific service
docker compose restart cms-frontend
docker compose restart cms-apim

# View running containers
docker compose ps
```

---

## 🔐 Security Notes

- CORS enabled on backend for frontend communication
- Credentials stored in environment variables
- Database passwords should be changed in production
- API uses standard REST with no authentication (add JWT for production)

---

## 🚀 Production Deployment

### Recommendations

1. **Frontend:**
   - Build static files: `npm run build`
   - Serve with nginx or production server
   - Enable HTTPS with SSL certificates
   - Set production API URL

2. **Backend:**
   - Use production ASGI server (Gunicorn + Uvicorn)
   - Add authentication (JWT tokens)
   - Implement rate limiting
   - Add API logging and monitoring
   - Set secure CORS policies

3. **WSO2 API Manager:**
   - Replace self-signed SSL certificates with CA-signed certificates
   - Change default admin credentials
   - Enable OAuth2 for API security
   - Configure API throttling policies
   - Set up analytics and monitoring
   - Enable backup and disaster recovery
   - See [wso2-stack/apim/PRODUCTION.md](wso2-stack/apim/PRODUCTION.md) for detailed guidance

4. **Databases:**
   - Enable backup and recovery
   - Set up replication
   - Configure proper user permissions
   - Monitor disk space and performance

5. **Monitoring:**
   - Set up container health checks
   - Add centralized logging
   - Monitor API response times
   - Track database queries

---

## 📝 License

ISC

## 👨‍💻 Author

Sameh Habib

---

## 🤝 Support

For issues or questions:
1. Check logs: `docker compose logs -f`
2. Verify services: `docker compose ps`
3. Test connectivity: `curl http://localhost:8000/health`
4. Review component documentation above
