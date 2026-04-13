# Service Records — Overview

The Service Records service manages the lifecycle of maintenance and service history entries associated with assets.

## Purpose

Provides a centralized log of all service events performed on an asset, including scheduled maintenance, repairs, and inspections.

## Key Concepts

- **Record** — A single service event tied to an asset, a timestamp, and a technician.
- **Asset** — The entity being serviced (vehicle, equipment, etc.).
- **Status** — The current state of a record: `pending`, `in_progress`, `completed`, `cancelled`.

## Responsibilities

- Create, update, and retrieve service records
- Associate records with assets and technicians
- Emit events when record status changes
- Archive completed records after a retention period
