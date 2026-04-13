# Service Records — API Endpoints

Base path: `/api/v1/service-records`

---

## Create a Record

**POST** `/api/v1/service-records`

Creates a new service record for an asset.

### Request Body

```json
{
  "asset_id": "string",
  "technician_id": "string",
  "service_type": "string",
  "scheduled_at": "ISO 8601 datetime",
  "notes": "string (optional)"
}
```

### Response `201 Created`

```json
{
  "id": "string",
  "asset_id": "string",
  "technician_id": "string",
  "service_type": "string",
  "status": "pending",
  "scheduled_at": "ISO 8601 datetime",
  "created_at": "ISO 8601 datetime"
}
```

---

## Get a Record

**GET** `/api/v1/service-records/{id}`

Returns a single service record by ID.

### Response `200 OK`

```json
{
  "id": "string",
  "asset_id": "string",
  "technician_id": "string",
  "service_type": "string",
  "status": "pending | in_progress | completed | cancelled",
  "scheduled_at": "ISO 8601 datetime",
  "completed_at": "ISO 8601 datetime | null",
  "notes": "string | null"
}
```

---

## Update Record Status

**PATCH** `/api/v1/service-records/{id}/status`

Transitions a record to a new status.

### Request Body

```json
{
  "status": "in_progress | completed | cancelled"
}
```

### Response `200 OK`

Returns the updated record object.

---

## List Records by Asset

**GET** `/api/v1/service-records?asset_id={asset_id}`

Returns all service records for a given asset, ordered by `scheduled_at` descending.
