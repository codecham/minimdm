# MiniMDM API

A mini Mobile Device Management REST API built with Django and Django REST Framework.

This project is a technical exercise implementing a simplified MDM platform where users manage their devices by organizing them into fleets.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Testing the API with Swagger](#testing-the-api-with-swagger)
3. [API Reference](#api-reference)
4. [Running Tests](#running-tests)
5. [Available Commands](#available-commands)
6. [Technical Decisions](#technical-decisions)
7. [Extra Features](#extra-features)
8. [Known Limitations](#known-limitations)
9. [Possible Improvements](#possible-improvements)

---

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Make (optional, but recommended)

### Installation

```bash
git clone <repository-url>
cd minimdm
make setup
```

This single command will:
1. Create the `.env` file from `.env.example`
2. Build and start the Docker containers
3. Run database migrations
4. Seed the database with test data

### Test Accounts

| Role  | Username | Password   |
|-------|----------|------------|
| Admin | admin    | admin123   |
| User  | alice    | alice123   |
| User  | bryan    | bryan123   |

### URLs

| Service     | URL                                |
|-------------|------------------------------------|
| API Root    | http://localhost:8000/api/          |
| Swagger UI  | http://localhost:8000/api/docs/     |
| ReDoc       | http://localhost:8000/api/redoc/    |
| Database UI | http://localhost:8081/              |

---

## Testing the API with Swagger

Swagger UI is the recommended way to explore and test the API. Open http://localhost:8000/api/docs/ in your browser.

### Step 1: Get an authentication token

1. Find the **POST /api/auth/token/** endpoint in the "Authentication" section
2. Click "Try it out"
3. Enter credentials, for example:
```json
{
  "username": "alice",
  "password": "alice123"
}
```
4. Click "Execute"
5. In the response, copy the `token` value. The response also includes `user_id` and `username` for convenience.

### Step 2: Authorize your requests

1. Click the **Authorize** button at the top right of the page
2. In the value field, type: `Token <your-token>` (with the space after "Token")
   - Example: `Token 9a8b7c6d5e4f3a2b1c0d...`
3. Click "Authorize", then "Close"

All subsequent requests will now include your authentication token.

### Step 3: Explore the endpoints

You are now authenticated and can test any endpoint. Here are some things to try:

**See your profile:**
- `GET /api/users/me/` -- returns your user info and your fleets

**Manage fleets:**
- `GET /api/fleets/` -- list your fleets (includes device count for each fleet)
- `POST /api/fleets/` with `{"name": "My New Fleet"}` -- create a fleet

**Manage devices:**
- `GET /api/devices/` -- list all your devices
- `GET /api/devices/?fleet=1` -- filter devices by fleet (use the `fleet` parameter)
- `POST /api/devices/` with `{"fleet": 1}` -- create a device (serial number is auto-generated)
- `POST /api/devices/` with `{"fleet": 1, "serial_number": "550e8400-e29b-41d4-a716-446655440000"}` -- create a device with a specific serial number
- `PATCH /api/devices/{id}/` with `{"fleet": 2}` -- move a device to another fleet
- `DELETE /api/devices/{id}/` -- delete a device

**Admin-only (login as admin):**
- `GET /api/users/` -- list all users
- `POST /api/users/` -- create a new user

---

## API Reference

### Authentication

| Method | Endpoint            | Description              | Auth Required |
|--------|---------------------|--------------------------|---------------|
| POST   | /api/auth/token/    | Get authentication token | No            |

**Request body:** `{"username": "...", "password": "..."}`

**Response:** `{"token": "...", "user_id": 1, "username": "..."}`

### Users

| Method | Endpoint          | Description                  | Permission          |
|--------|-------------------|------------------------------|---------------------|
| GET    | /api/users/       | List all users               | Admin only          |
| POST   | /api/users/       | Create a new user            | Admin only          |
| GET    | /api/users/{id}/  | Get user details with fleets | Admin or self       |
| GET    | /api/users/me/    | Get own profile with fleets  | Any authenticated   |

**Create user body:** `{"username": "...", "email": "...", "password": "..."}` (password minimum 8 characters)

### Fleets

| Method | Endpoint          | Description       | Permission |
|--------|-------------------|-------------------|------------|
| GET    | /api/fleets/      | List own fleets   | Owner      |
| POST   | /api/fleets/      | Create a fleet    | Authenticated |
| GET    | /api/fleets/{id}/ | Get fleet details | Owner      |

**Create fleet body:** `{"name": "..."}`

**Response includes:** `device_count` -- the number of devices in the fleet.

Fleet names must be unique per user. The owner is automatically set to the authenticated user.

### Devices

| Method | Endpoint           | Description            | Permission  |
|--------|--------------------|------------------------|-------------|
| GET    | /api/devices/      | List own devices       | Fleet owner |
| POST   | /api/devices/      | Create a device        | Fleet owner |
| GET    | /api/devices/{id}/ | Get device details     | Fleet owner |
| PUT    | /api/devices/{id}/ | Full update a device   | Fleet owner |
| PATCH  | /api/devices/{id}/ | Partial update a device| Fleet owner |
| DELETE | /api/devices/{id}/ | Delete a device        | Fleet owner |

**Query parameters:**

| Parameter | Type | Description              |
|-----------|------|--------------------------|
| fleet     | int  | Filter devices by fleet ID |

**Create device body:** `{"fleet": 1}` or `{"fleet": 1, "serial_number": "...", "os_version": 12}`

- `fleet` (required) -- the fleet ID. Must be a fleet owned by the authenticated user.
- `serial_number` (optional) -- a valid UUID. Auto-generated if not provided.
- `os_version` (optional) -- a positive integer.

**Moving a device between fleets:** `PATCH /api/devices/{id}/` with `{"fleet": 2}`. The user must own both the current fleet and the target fleet.

---

## Running Tests

```bash
make test
```

The test suite contains 43 tests covering:

- **Authentication** (5 tests) -- token obtain, invalid credentials, token response content
- **Users** (13 tests) -- list, create, detail, permissions, /me/ endpoint
- **Fleets** (9 tests) -- list, create, detail, unique names, device count
- **Devices** (16 tests) -- CRUD, fleet move, fleet filter, permissions, serial number handling

---

## Available Commands

```bash
make setup      # First time setup (build + migrate + seed)
make start      # Start containers
make stop       # Stop containers
make restart    # Restart containers
make test       # Run tests
make seed       # Seed database with test data
make logs       # View logs
make shell      # Open Django shell
make bash       # Open bash in web container
make urls       # Show useful URLs and test accounts
make help       # Show all available commands
```

---

## Technical Decisions

### Why Token Authentication over JWT?

Token authentication is built into Django REST Framework, simple to set up, and sufficient for this exercise. JWT would add external dependencies and complexity (token refresh, expiration handling) without meaningful benefit here.

### Why admin-only for user management?

In a B2B MDM context like Famoco, user accounts are typically managed by administrators, not self-registered. Regular users can only view their own profile through `GET /api/users/me/` or `GET /api/users/{id}/` (their own ID).

### Why filter querysets instead of checking permissions on each object?

For fleets and devices, the queryset is filtered at the ViewSet level:

```python
def get_queryset(self):
    return Fleet.objects.filter(owner=self.request.user)
```

This means users never even "see" resources that don't belong to them. A request for another user's fleet returns 404 (not 403), which is more secure -- it doesn't reveal whether the resource exists.

### Why explicit mixins instead of full ModelViewSet?

For Users and Fleets, only specific actions are needed (list, create, retrieve). Using explicit mixins instead of ModelViewSet avoids exposing unneeded endpoints (update, delete) and reduces the attack surface.

### Why validate fleet ownership in the serializer?

Fleet ownership is validated in `DeviceSerializer.validate_fleet()` rather than in the view. This catches invalid fleet assignments (creating a device in someone else's fleet, or moving a device to a fleet you don't own) before any database operation, and returns clear error messages.

### Why optional serial numbers?

In a real MDM context, devices have physical serial numbers assigned by the manufacturer. The API accepts a user-provided serial number to reflect this reality. If not provided, a UUID is auto-generated for convenience during testing or when the serial number is not yet known.

---

## Extra Features

Beyond the core requirements, the following features were added:

- **GET /api/users/me/** -- convenience endpoint to access own profile without knowing your user ID
- **Enriched token response** -- the token endpoint returns `user_id` and `username` alongside the token, so clients know who they are immediately after login
- **Device count on fleets** -- fleet responses include `device_count` to quickly see how many devices are in each fleet
- **Optional serial number** -- devices can be created with or without a serial number; auto-generated if not provided
- **Swagger UI documentation** -- interactive API documentation with detailed descriptions for every endpoint
- **Database seeding** -- a management command (`make seed`) populates the database with realistic test data
- **Makefile** -- simplified project management with colored output
- **Database UI** -- pgweb interface for inspecting the database directly

---

## Known Limitations

- **No pagination** -- list endpoints return all results, which could cause performance issues with large datasets
- **No rate limiting** -- the API is not protected against abuse or brute-force attacks
- **Tokens don't expire** -- once issued, authentication tokens are valid indefinitely
- **No audit log** -- device movements between fleets are not tracked historically
- **PUT behaves like PATCH** -- DRF's default ModelViewSet does not enforce strict PUT semantics (missing fields are not reset to null)

---

## Possible Improvements

- Add pagination for list endpoints
- Add filtering by `os_version`
- Add device movement history (audit log of fleet changes)
- Add bulk operations (create or move multiple devices at once)
- Implement token expiration
- Add rate limiting

---

## Tech Stack

| Component       | Technology                | Version |
|-----------------|---------------------------|---------|
| Framework       | Django                    | 6.0     |
| API             | Django REST Framework     | 3.16    |
| Database        | PostgreSQL                | 16      |
| Documentation   | drf-spectacular           | 0.29    |
| Testing         | pytest-django             | 4.10    |
| Containerization| Docker and Docker Compose | Latest  |
| Python          |                           | 3.13    |

---

## Project Structure

```
minimdm/
├── config/
│   ├── settings.py            # Django and DRF configuration
│   ├── urls.py                # Root URL routing
│   └── ...
├── mdm/
│   ├── models.py              # Fleet and Device models
│   ├── serializers.py         # API serializers with validation
│   ├── views.py               # ViewSets with Swagger documentation
│   ├── permissions.py         # IsAdminUser, IsAdminOrSelf
│   ├── authentication.py      # Token authentication view
│   ├── urls.py                # API router
│   ├── fixtures/
│   │   └── seed_data.json     # Test data
│   ├── management/
│   │   └── commands/
│   │       └── seed_db.py     # Database seeding command
│   └── tests/
│       ├── conftest.py        # Shared test fixtures
│       ├── test_auth.py
│       ├── test_users.py
│       ├── test_fleets.py
│       └── test_devices.py
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── requirements.txt
└── README.md
```