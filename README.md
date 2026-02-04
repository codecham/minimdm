# MiniMDM API

A mini Mobile Device Management REST API built with Django and Django REST Framework.

## Description

This project is a technical exercise implementing a simplified MDM platform where users can manage their devices by organizing them into fleets.

### Features

- **User Management** - Admin-managed user accounts with token authentication
- **Fleet Management** - Logical groupings of devices, owned by users
- **Device Management** - Full CRUD operations with fleet assignment
- **Permission System** - Users can only access their own resources
- **API Documentation** - Interactive Swagger UI

### Business Rules

- Users must be authenticated to access the API
- Users can only see and manage their own fleets
- Users can only see and manage devices in their own fleets
- Devices can be moved between fleets only if the user owns both fleets
- Fleet names must be unique per user

---

## Tech Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Framework | Django | 6.0 |
| API | Django REST Framework | 3.16 |
| Database | PostgreSQL | 16 |
| Documentation | drf-spectacular | 0.29 |
| Containerization | Docker & Docker Compose | Latest |
| Python | | 3.13 |

---

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Make (optional, but recommended)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd minimdm

# Start the project (one command!)
make setup
```

That's it! The `make setup` command will:
1. Create the `.env` file from `.env.example`
2. Build and start the Docker containers
3. Run database migrations
4. Seed the database with test data

> **Note**: The `.env.example` file contains default values that work out of the box for development. You can modify them if needed.

### Access the Application

| Service | URL |
|---------|-----|
| API | http://localhost:8000/api/ |
| Swagger UI | http://localhost:8000/api/docs/ |
| ReDoc | http://localhost:8000/api/redoc/ |
| Database UI | http://localhost:8080/ |

### Test Accounts

| Role | Username | Password | Description |
|------|----------|----------|-------------|
| Admin | `admin` | `admin123` | Can manage users |
| User | `alice` | `alice123` | Has 2 fleets, 5 devices |
| User | `bob` | `bob123` | Has 1 fleet, 1 device |

---

## Available Commands

Run `make help` to see all available commands:

```
Setup & Installation:
  make setup      - First time setup (build + migrate + seed)
  make build      - Rebuild containers

Start & Stop:
  make start      - Start containers
  make stop       - Stop containers
  make restart    - Restart containers
  make logs       - View logs (Ctrl+C to exit)

Database:
  make migrate    - Run migrations
  make seed       - Seed database with test data
  make flush      - Clear all data from database

Development:
  make shell      - Open Django shell
  make bash       - Open bash in web container
  make test       - Run tests

Utilities:
  make urls       - Show useful URLs
```

---

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/token/` | Obtain authentication token | No |

### Users

| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/api/users/` | List all users | Admin only |
| POST | `/api/users/` | Create a new user | Admin only |
| GET | `/api/users/{id}/` | Get user details with fleets | Admin or owner |

### Fleets

| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/api/fleets/` | List user's fleets | Owner only |
| POST | `/api/fleets/` | Create a new fleet | Authenticated |
| GET | `/api/fleets/{id}/` | Get fleet details | Owner only |

### Devices

| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/api/devices/` | List devices in user's fleets | Owner only |
| POST | `/api/devices/` | Create a device | Fleet owner |
| GET | `/api/devices/{id}/` | Get device details | Fleet owner |
| PUT | `/api/devices/{id}/` | Update device | Fleet owner |
| PATCH | `/api/devices/{id}/` | Partial update device | Fleet owner |
| DELETE | `/api/devices/{id}/` | Delete device | Fleet owner |

#### Query Parameters

| Endpoint | Parameter | Description |
|----------|-----------|-------------|
| GET `/api/devices/` | `fleet` | Filter devices by fleet ID |

---

## API Examples

### Get Authentication Token

```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "alice123"}'
```

### List Fleets

```bash
curl http://localhost:8000/api/fleets/ \
  -H "Authorization: Token <your-token>"
```

### Create a Fleet

```bash
curl -X POST http://localhost:8000/api/fleets/ \
  -H "Authorization: Token <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Production Fleet"}'
```

### Create a Device

```bash
curl -X POST http://localhost:8000/api/devices/ \
  -H "Authorization: Token <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"fleet": 1, "os_version": 12}'
```

### Move Device to Another Fleet

```bash
curl -X PATCH http://localhost:8000/api/devices/1/ \
  -H "Authorization: Token <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"fleet": 2}'
```

### Filter Devices by Fleet

```bash
curl "http://localhost:8000/api/devices/?fleet=1" \
  -H "Authorization: Token <your-token>"
```

---

## Architecture & Design Decisions

### Project Structure

```
minimdm/
├── config/                 # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── mdm/                    # Main application
│   ├── models.py          # Fleet, Device models
│   ├── serializers.py     # API serializers
│   ├── views.py           # ViewSets
│   ├── permissions.py     # Custom permissions
│   ├── urls.py            # API routes
│   ├── fixtures/          # Seed data
│   └── management/        # Custom commands
├── docker-compose.yml
├── Dockerfile
├── Makefile
└── requirements.txt
```

### Key Technical Decisions

#### 1. Token Authentication

**Choice**: DRF Token Authentication over JWT

**Rationale**: Simple, stateless, and built into DRF. JWT would add unnecessary complexity for this exercise.

#### 2. User Permission Strategy

**Choice**: Admin-only for user management

**Rationale**: In a B2B MDM context, admins typically manage user accounts. Regular users can only view their own profile.

| Endpoint | Permission |
|----------|------------|
| `GET /api/users/` | Admin only |
| `POST /api/users/` | Admin only |
| `GET /api/users/{id}/` | Admin or profile owner |

#### 3. Data Isolation

**Choice**: Filter querysets at the ViewSet level

**Rationale**: Users automatically see only their own data. The queryset is filtered before any operation.

```python
def get_queryset(self):
    return Fleet.objects.filter(owner=self.request.user)
```

#### 4. Fleet Ownership Validation

**Choice**: Validate in serializer

**Rationale**: Prevents users from creating devices in or moving devices to fleets they don't own. Validation happens before any database operation.

#### 5. ViewSet Actions

**Choice**: Explicit mixins instead of full ModelViewSet for Users and Fleets

**Rationale**: Only expose needed endpoints. Users have `list`, `create`, `retrieve` but not `update` or `delete`.

---

## Running Tests

```bash
make test
```

The test suite includes 35 tests covering:
- Authentication (token obtain, protected endpoints)
- User endpoints (list, create, detail, permissions)
- Fleet endpoints (list, create, detail, unique names)
- Device endpoints (CRUD, move, filter, permissions)

---

## Known Limitations

- **No pagination** - Large datasets may cause performance issues
- **No rate limiting** - API is not protected against abuse
- **Basic token auth** - Tokens don't expire

---

## Possible Improvements

- Add pagination for list endpoints
- Add device movement history (audit log)
- Add bulk operations for devices
- Add filtering by `os_version`
- Add device count to fleet responses
- Implement token expiration

---

## Author

Codecham