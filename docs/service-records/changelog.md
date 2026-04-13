# Service Records — Changelog

## [Unreleased]

## [1.0.0] — 2026-04-13

### Added
- Initial release of the Service Records service
- `POST /api/v1/service-records` — create a new record
- `GET /api/v1/service-records/{id}` — retrieve a record by ID
- `PATCH /api/v1/service-records/{id}/status` — update record status
- `GET /api/v1/service-records?asset_id=` — list records by asset
- Status lifecycle: `pending` → `in_progress` → `completed` / `cancelled`
