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

### Overview

The frontend is a modern React application built with:
- **React 18.2.0** - UI framework
- **Vite 5.4.21** - Build tool for fast development
- **Bootstrap 5.3.0** - CSS framework for professional styling
- **Axios 1.15.0** - HTTP client for API communication

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
| cms-apim | wso2/wso2am:4.0.0 | 8280, 8243, 9443, 9611 | WSO2 API Manager gateway |

---

## 🌐 WSO2 API Manager (APIM)

### Overview

WSO2 API Manager is an enterprise-grade API management platform that provides centralized API governance, security, and monetization.

### Quick Start

**Access WSO2 APIM:**
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

### Architecture

```
wso2-stack/apim/
├── README.md                    # Quick start guide
├── API_REGISTRATION.md          # Step-by-step API registration
├── POLICIES.md                  # Policy configuration guide
├── PRODUCTION.md                # Production deployment guide
├── POLICIES.md                  # API security policies
├── Dockerfile                   # APIM container image
├── docker-compose.yml           # APIM Docker service definition
├── .env                         # Environment configuration
├── start.sh                     # Quick start script
└── cms-api-definition.json      # OpenAPI/Swagger definition for CMS APIs
```

### Configuration

**Environment Variables:**
```env
DB_TYPE=postgresql                  # Database type
DB_HOSTNAME=cms-postgresql          # PostgreSQL host
DB_PORT=5432                        # PostgreSQL port
DB_NAME=wso2am                      # Database name
DB_USERNAME=postgres                # DB username
DB_PASSWORD=postgres                # DB password
ADMIN_USERNAME=admin                # APIM admin user
ADMIN_PASSWORD=admin                # APIM admin password
API_GATEWAY_HOST=cms-apim           # Gateway hostname
API_GATEWAY_HTTP_PORT=8280          # Gateway HTTP port
API_GATEWAY_HTTPS_PORT=8243         # Gateway HTTPS port
```

### Registering CMS APIs

**Step 1: Access Publisher Portal**
1. Open https://localhost:9443/publisher
2. Login with admin credentials
3. Accept SSL certificate

**Step 2: Create API**
1. Click **Create** → **Create New API**
2. Select **REST API**
3. Enter API details:
   - Name: `CMS Test API`
   - Context: `/cms/test`
   - Version: `1.0.0`
   - Backend URL: `http://cms-backend:8000/test`

**Step 3: Publish API**
1. Configure endpoints
2. Apply policies (OAuth2, throttling, CORS)
3. Click **Publish**
4. API available at: `https://localhost:8243/cms/test/1.0.0`

**Step 4: Test API**
```bash
# Generate OAuth2 token
TOKEN=$(curl -X POST "https://localhost:9443/oauth2/token" \
  -H "Authorization: Basic YWRtaW46YWRtaW4=" \
  -d "grant_type=client_credentials" -k -s | jq -r '.access_token')

# Call API
curl -X GET "https://localhost:8243/cms/test/1.0.0/oracle" \
  -H "Authorization: Bearer $TOKEN" -k
```

### Integration with Frontend

Update frontend API client to route through APIM gateway:

```javascript
// frontend/src/api/client.js
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'https://localhost:8243/cms/v1',
  httpsAgent: {
    rejectUnauthorized: false  // For development only
  }
});

// Add token injection
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default apiClient;
```

### Documentation

For detailed information, see:
- **[wso2-stack/apim/README.md](wso2-stack/apim/README.md)** - APIM overview and quick start
- **[wso2-stack/apim/API_REGISTRATION.md](wso2-stack/apim/API_REGISTRATION.md)** - API registration guide
- **[wso2-stack/apim/POLICIES.md](wso2-stack/apim/POLICIES.md)** - Policy configuration
- **[wso2-stack/apim/PRODUCTION.md](wso2-stack/apim/PRODUCTION.md)** - Production deployment

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
