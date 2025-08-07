# Events API Documentation

## Overview

The Events API is a comprehensive REST API for managing events, cities, user subscriptions, and search functionality. This API provides endpoints for event discovery, submission, search, and beta program management.

**Base URL:** `https://api.portalx.space/api/v1/`

**API Version:** 1.0.0

## Authentication

Most endpoints are publicly accessible. Some endpoints may require authentication:

- **Bearer Token:** Include `Authorization: Bearer <token>` in request headers
- **API Key:** Include `X-API-Key: <api_key>` in request headers

## Response Format

All API responses follow a consistent format:

```json
{
  "status": "success|error",
  "success": true|false,
  "message": "Human readable message",
  "data": {...}
}
```

## Error Handling

### HTTP Status Codes

- `200` - OK: Request successful
- `201` - Created: Resource created successfully
- `400` - Bad Request: Invalid request data
- `401` - Unauthorized: Authentication required
- `403` - Forbidden: Insufficient permissions
- `404` - Not Found: Resource not found
- `422` - Unprocessable Entity: Validation errors
- `500` - Internal Server Error: Server error
- `503` - Service Unavailable: External service unavailable

### Error Response Format

```json
{
  "detail": "Error message",
  "field_errors": {
    "field_name": ["Field-specific error messages"]
  }
}
```

---

## Endpoints

### Events

#### 1. List Active Events

Get a paginated list of all active events (events with start date >= today).

**Endpoint:** `GET /events/active/`

**Authentication:** Not required

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page` | integer | No | 1 | Page number for pagination |
| `page_size` | integer | No | 24 | Number of results per page (max 100) |

**Response Format:**

```json
{
  "count": 156,
  "next": "https://api.portalx.space/api/v1/events/active/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Summer Music Festival",
      "event_image": "https://api.portalx.space/media/events/festival.jpg",
      "start_date": "2025-08-15",
      "end_date": "2025-08-17",
      "description": "A three-day music festival featuring local and international artists.",
      "venue": "Central Park Amphitheater, 123 Park Ave, New York, NY",
      "link": "https://summermusicfest.com",
      "city": {
        "id": 1,
        "city_name": "New York",
        "city_ascii": "New York",
        "lat": "40.712800",
        "lng": "-74.006000",
        "region": {
          "state_name": "New York",
          "state_code": "NY",
          "lat": "42.165726",
          "lng": "-74.948051",
          "country": {
            "country_name": "United States",
            "iso2_code": "US",
            "iso3_code": "USA"
          }
        }
      },
      "featured": true
    }
  ]
}
```

**Example Request:**

```bash
curl -X GET "https://api.portalx.space/api/v1/events/active/?page=1&page_size=10" \
  -H "Accept: application/json"
```

**Possible Errors:**

- `400 Bad Request`: Invalid pagination parameters

---

#### 2. Home Page Events

Get events and featured events for the home page display.

**Endpoint:** `GET /events/`

**Authentication:** Optional (returns more data if authenticated)

**Response Format:**

```json
{
  "status": "success",
  "success": true,
  "message": "Events retrieved successfully",
  "events": [
    {
      "id": 1,
      "title": "Summer Music Festival",
      "event_image": "https://api.portalx.space/media/events/festival.jpg",
      "start_date": "2025-08-15",
      "end_date": "2025-08-17",
      "description": "A three-day music festival...",
      "venue": "Central Park Amphitheater",
      "link": "https://summermusicfest.com",
      "city": {...},
      "featured": true
    }
  ],
  "featured_events": [
    {
      "id": 2,
      "title": "Tech Conference 2025",
      "event_image": "https://api.portalx.space/media/events/tech.jpg",
      "start_date": "2025-09-01",
      "end_date": null,
      "description": "Annual technology conference...",
      "venue": "Convention Center",
      "link": "https://techconf2025.com",
      "city": {...},
      "featured": true
    }
  ]
}
```

**Example Request:**

```bash
curl -X GET "https://api.portalx.space/api/v1/events/" \
  -H "Accept: application/json"
```

**Possible Errors:**

- `500 Internal Server Error`: Server error while retrieving events

---

#### 3. Submit New Event

Submit a new event with optional image upload and user account creation.

**Endpoint:** `POST /events/submit/`

**Authentication:** Not required (public submission)

**Content-Type:** `multipart/form-data` (for image uploads) or `application/json`

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Event title (max 300 chars) |
| `start_date` | date | Yes | Event start date (YYYY-MM-DD) |
| `end_date` | date | No | Event end date (YYYY-MM-DD) |
| `city` | integer | Yes | City ID where event takes place |
| `when` | string | No | Time description (e.g., "7:00 PM - 10:00 PM") |
| `description` | text | No | Detailed event description |
| `venue` | string | Yes | Event venue name and address (max 400 chars) |
| `event_source` | string | No | Source of event (default: "user_submitted") |
| `link` | url | No | External event link |
| `event_image` | file | No | Event banner image |
| `first_name` | string | Yes | Submitter's first name (max 100 chars) |
| `last_name` | string | Yes | Submitter's last name (max 100 chars) |
| `email` | email | Yes | Submitter's email address (max 100 chars) |
| `phone` | string | No | Submitter's phone number (max 15 chars) |
| `create_account` | boolean | No | Create user account for submitter (default: false) |

**Event Source Choices:**
- `all_events_in`
- `eventbrite`
- `user_submitted` (default)
- `serp_api_google_event`
- `artidea`
- `added_by_admin`
- `luma`
- `ticketmaster`

**Request Example (JSON):**

```json
{
  "title": "Community Art Workshop",
  "start_date": "2025-08-20",
  "end_date": "2025-08-20",
  "city": 1,
  "when": "2:00 PM - 5:00 PM",
  "description": "Join us for a hands-on art workshop where participants will learn watercolor techniques.",
  "venue": "Community Center, 456 Main St, New York, NY",
  "link": "https://communityart.com/workshop",
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "jane.doe@example.com",
  "phone": "+1-555-0123",
  "create_account": true
}
```

**Success Response (201 Created):**

```json
{
  "id": 123,
  "title": "Community Art Workshop",
  "event_image": "/static/home/assets/img/error/no-image-placeholder.jpg",
  "start_date": "2025-08-20",
  "end_date": "2025-08-20",
  "description": "Join us for a hands-on art workshop...",
  "venue": "Community Center, 456 Main St, New York, NY",
  "link": "https://communityart.com/workshop",
  "city": {
    "id": 1,
    "city_name": "New York",
    "city_ascii": "New York",
    "lat": "40.712800",
    "lng": "-74.006000",
    "region": {...}
  },
  "featured": false
}
```

**Example Request:**

```bash
curl -X POST "https://api.portalx.space/api/v1/events/submit/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Community Art Workshop",
    "start_date": "2025-08-20",
    "city": 1,
    "venue": "Community Center",
    "first_name": "Jane",
    "last_name": "Doe",
    "email": "jane.doe@example.com"
  }'
```

**Possible Errors:**

- `400 Bad Request`: Validation errors
- `422 Unprocessable Entity`: Invalid data format

**Validation Rules:**

- Email must be unique if `create_account` is true
- Start date must be in the future
- City must exist and be active
- Phone number format validation

---

#### 4. Get Active Cities

Get all active cities available for event submission.

**Endpoint:** `GET /events/submit/`

**Authentication:** Not required

**Response Format:**

```json
[
  {
    "id": 1,
    "city_name": "New York",
    "city_ascii": "New York",
    "lat": "40.712800",
    "lng": "-74.006000",
    "region": {
      "state_name": "New York",
      "state_code": "NY",
      "lat": "42.165726",
      "lng": "-74.948051",
      "country": {
        "country_name": "United States",
        "iso2_code": "US",
        "iso3_code": "USA"
      }
    }
  },
  {
    "id": 2,
    "city_name": "Los Angeles",
    "city_ascii": "Los Angeles",
    "lat": "34.052234",
    "lng": "-118.243685",
    "region": {
      "state_name": "California",
      "state_code": "CA",
      "lat": "36.116203",
      "lng": "-119.681564",
      "country": {
        "country_name": "United States",
        "iso2_code": "US",
        "iso3_code": "USA"
      }
    }
  }
]
```

**Example Request:**

```bash
curl -X GET "https://api.portalx.space/api/v1/events/submit/" \
  -H "Accept: application/json"
```

---

### Search

#### 5. Search Events

Search for events using a query string with pagination support.

**Endpoint:** `GET /search/`

**Authentication:** Not required

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | Yes | Search query for events (1-200 chars) |
| `page` | integer | No | Page number for pagination |
| `page_size` | integer | No | Number of results per page (max 100) |

**Response Format:**

```json
{
  "count": 25,
  "next": "https://api.portalx.space/api/v1/search/?q=music&page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Summer Music Festival",
      "event_image": "https://api.portalx.space/media/events/festival.jpg",
      "start_date": "2025-08-15",
      "end_date": "2025-08-17",
      "description": "A three-day music festival...",
      "venue": "Central Park Amphitheater",
      "link": "https://summermusicfest.com",
      "city": {...},
      "featured": true
    }
  ]
}
```

**Example Requests:**

```bash
# Basic search
curl -X GET "https://api.portalx.space/api/v1/search/?q=music" \
  -H "Accept: application/json"

# Search with pagination
curl -X GET "https://api.portalx.space/api/v1/search/?q=festival&page=1&page_size=10" \
  -H "Accept: application/json"
```

**Search Features:**

- Full-text search across event titles and descriptions
- Location-based filtering
- Date range filtering
- Relevance-based ranking

**Possible Errors:**

- `400 Bad Request`: Missing or invalid query parameter
- `422 Unprocessable Entity`: Query too long or too short

---

#### 6. Search Suggestions

Get autocomplete suggestions for search queries from events, cities, and zip codes.

**Endpoint:** `GET /search/suggestions/`

**Authentication:** Not required

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | Yes | Query string for autocomplete (1-100 chars) |

**Response Format:**

```json
[
  {
    "name": "Summer Music Festival",
    "type": "Event"
  },
  {
    "name": "New York",
    "type": "City"
  },
  {
    "name": "10001",
    "type": "ZipCode"
  },
  {
    "name": "Jazz Concert",
    "type": "Event"
  }
]
```

**Suggestion Types:**

- `Event`: Event titles
- `City`: City names
- `ZipCode`: Postal codes

**Example Request:**

```bash
curl -X GET "https://api.portalx.space/api/v1/search/suggestions/?q=new" \
  -H "Accept: application/json"
```

**Features:**

- Real-time suggestions as you type
- Deduplication of similar results
- Limited to top 20 most relevant suggestions
- Searches across multiple data sources (events, cities, zip codes)

**Possible Errors:**

- `400 Bad Request`: Missing or invalid query parameter
- `503 Service Unavailable`: Search service temporarily unavailable

---

### Beta Program

#### 7. Join Beta Program

Subscribe to the beta program with contact information.

**Endpoint:** `POST /events/beta/subscribe/`

**Authentication:** Not required

**Content-Type:** `application/json`

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `first_name` | string | Yes | Subscriber's first name (max 300 chars) |
| `last_name` | string | Yes | Subscriber's last name (max 300 chars) |
| `phone` | string | Yes | Subscriber's phone number (max 300 chars) |
| `email` | email | Yes | Subscriber's email address (max 300 chars) |

**Request Example:**

```json
{
  "first_name": "John",
  "last_name": "Smith",
  "phone": "+1-555-0199",
  "email": "john.smith@example.com"
}
```

**Success Response (201 Created):**

```json
{
  "status": "success",
  "message": "Thank you for joining our beta program",
  "subscriber": {
    "first_name": "John",
    "last_name": "Smith",
    "phone": "+1-555-0199",
    "email": "john.smith@example.com"
  }
}
```

**Example Request:**

```bash
curl -X POST "https://api.portalx.space/api/v1/events/beta/subscribe/" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Smith",
    "phone": "+1-555-0199",
    "email": "john.smith@example.com"
  }'
```

**Possible Errors:**

- `400 Bad Request`: Validation errors
  - Email already exists
  - Phone number already exists
  - Invalid email format
  - Missing required fields

---

#### 8. Alternative Beta Signup

Alternative endpoint for beta program subscription (backward compatibility).

**Endpoint:** `POST /beta/join/`

**Authentication:** Not required

This endpoint is identical to `/events/beta/subscribe/` and is provided for backward compatibility.

---

## Data Models

### Event Object

```json
{
  "id": 1,
  "title": "string (max 300 chars)",
  "event_image": "url or null",
  "start_date": "date (YYYY-MM-DD)",
  "end_date": "date (YYYY-MM-DD) or null",
  "description": "text or null",
  "venue": "string (max 400 chars)",
  "link": "url or null",
  "city": "City object",
  "featured": "boolean"
}
```

### City Object

```json
{
  "id": "integer",
  "city_name": "string (max 250 chars)",
  "city_ascii": "string (max 250 chars)",
  "lat": "decimal (max 10 digits, 6 decimal places)",
  "lng": "decimal (max 10 digits, 6 decimal places)",
  "region": "Location object"
}
```

### Location (State) Object

```json
{
  "state_name": "string (max 250 chars)",
  "state_code": "string (max 5 chars)",
  "lat": "string (max 15 chars)",
  "lng": "string (max 15 chars)",
  "country": "Country object"
}
```

### Country Object

```json
{
  "country_name": "string (max 100 chars)",
  "iso2_code": "string (max 20 chars)",
  "iso3_code": "string (max 20 chars)"
}
```

### Beta Subscriber Object

```json
{
  "first_name": "string (max 300 chars)",
  "last_name": "string (max 300 chars)",
  "phone": "string (max 300 chars)",
  "email": "email (max 300 chars)"
}
```

## Rate Limiting

API requests are rate-limited to ensure fair usage:

- **Anonymous users:** 100 requests per hour
- **Authenticated users:** 1000 requests per hour
- **Search endpoints:** 500 requests per hour per IP

Rate limit headers are included in responses:

- `X-RateLimit-Limit`: Request limit per hour
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Time when rate limit resets (Unix timestamp)

## Pagination

All list endpoints support pagination using the following parameters:

- `page`: Page number (starts from 1)
- `page_size`: Number of items per page (default: 24, max: 100)

Pagination responses include:

- `count`: Total number of items
- `next`: URL for next page (null if last page)
- `previous`: URL for previous page (null if first page)
- `results`: Array of items for current page

## CORS

The API supports Cross-Origin Resource Sharing (CORS) for web applications:

- Allowed origins: All origins (`*`) for public endpoints
- Allowed methods: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `OPTIONS`
- Allowed headers: `Content-Type`, `Authorization`, `X-API-Key`

## Webhooks

For event submissions and updates, the API can send webhooks to configured endpoints:

### Event Submitted

Triggered when a new event is submitted.

**Payload:**

```json
{
  "event": "event.submitted",
  "data": {
    "event_id": 123,
    "title": "Community Art Workshop",
    "submitter_email": "jane.doe@example.com",
    "submitted_at": "2025-08-05T14:30:00Z"
  }
}
```

## SDKs and Libraries

Official SDKs are available for popular programming languages:

- **JavaScript/Node.js:** `npm install events-api-client`
- **Python:** `pip install events-api-python`
- **PHP:** `composer require events-api/php-client`

## Support

For API support and questions:

- **Documentation:** https://docs.portalx.space/api
- **Support Email:** api-support@portalx.space
- **Status Page:** https://status.portalx.space
- **GitHub Issues:** https://github.com/yourapp/api-issues

## Changelog

### Version 1.0.0 (Current)

- Initial API release
- Event management endpoints
- Search and suggestions
- Beta program subscription
- Comprehensive documentation

---

*Last updated: August 5, 2025*