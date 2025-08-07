# Geography API Documentation

## Overview

The Geography API provides endpoints for managing countries, states/locations, and cities. This API supports full CRUD operations with proper authentication and permission handling.

**Base URL:** `https://api.yourapp.com/api/v1/geography/`

## Authentication & Permissions

- **Read Operations (GET):** Public access allowed
- **Write Operations (POST, PUT, PATCH, DELETE):** Authentication required
- **Permission Class:** `ReadOnlyOrAuthenticated`

---

## Countries API

### 1. List Countries

Get a list of all validated countries.

**Endpoint:** `GET /geography/countries/`

**Authentication:** Not required

**Response Format:**

```json
[
  {
    "country_name": "United States",
    "iso2_code": "US",
    "iso3_code": "USA"
  },
  {
    "country_name": "Canada",
    "iso2_code": "CA", 