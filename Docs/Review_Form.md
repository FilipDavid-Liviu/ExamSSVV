# Code Inspection / Review Form

**Project**: Agricultural Crop Rotation Management System
**Language / Technology**: Python 3, FastAPI, Pydantic, Jinja2
**Review Type**: Walkthrough (individual inspection)
**Reviewer**: denis (denisgre205@gmail.com)
**Date**: 2026-05-24

---

## Review Scope

| Module | File |
|---|---|
| Domain Models | `backend/models/domain.py` |
| Repository | `backend/repository/memory.py` |
| Service | `backend/services/farm_service.py` |
| Web Router | `backend/routers/web.py` |

---

## Phase 1 — Requirements Review

Review of the functional requirements as expressed through the system's specification (inferred from domain model constraints, seed data, and route definitions).

| ID | Defect Description | Location | Category | Severity |
|---|---|---|---|---|
| R_01 | No enumerated set of valid values is defined for `Crop.season`. The seed data uses "Winter", "Summer", "Spring", but any arbitrary string is accepted (e.g., "Rainy", "xyz"). The valid domain is left ambiguous. | Implied spec / `domain.py:12` | Missing Requirement | Medium |
| R_02 | No enumerated set of valid values is defined for `Field.soil_type`. Seed data uses "Clay Loam", "Sandy Loam", "Silt", "Peaty", "Chalky", but the requirement does not restrict or enumerate these values. | Implied spec / `domain.py:8` | Missing Requirement | Medium |
| R_03 | No maximum length constraint is specified for `Field.name` or `Crop.name`. An arbitrarily long string can be submitted and stored, which could break UI rendering or database column limits in future persistence layers. | Implied spec / `domain.py:5,11` | Missing Requirement | Low |
| R_04 | No constraint is specified on the acceptable range for `harvest_date`. Future dates (e.g., 2099-01-01) and arbitrarily old dates are accepted without restriction. | Implied spec / `domain.py:19` | Missing Requirement | Low |
| R_05 | No uniqueness requirement is defined for field names or crop names. Two fields named "North Plot" can coexist with different IDs, which could confuse users selecting from dropdowns during harvest registration. | Implied spec | Missing Requirement | Medium |
| R_06 | The behavior when editing a harvest to reference a non-existent `field_id` or `crop_id` is not specified. The current implementation silently allows this; the requirement should explicitly state whether this is valid or an error. | Implied spec / `web.py:169-186` | Ambiguous Requirement | High |

---

## Phase 2 — Unit Design Review

Review of the design decisions visible in the class and interface structure.

| ID | Defect Description | Location | Category | Severity |
|---|---|---|---|---|
| D_01 | The error propagation strategy for `register_harvest` is inconsistent across layers. The service design raises `ValueError` on invalid IDs, but the web layer design does not propagate this to the user — the router simply discards the exception. The design does not specify how errors should surface to the UI. | `farm_service.py:74-76`, `web.py:157-158` | Design Omission | High |
| D_02 | `update_harvest` is designed to bypass `register_harvest` validation. A direct `Harvest` object is constructed and saved without verifying that `field_id` and `crop_id` reference existing entities. This creates an inconsistency: creation validates existence, but update does not. | `web.py:180-185`, `farm_service.py:66-68` | Design Inconsistency | High |
| D_03 | `Field.size_hectares` and `Crop.expected_yield_per_hectare` lack a `ge=0` constraint in the domain model design, creating an inconsistency with `Harvest.actual_yield_tons` which correctly enforces `ge=0`. Negative field sizes and negative expected yields are structurally invalid but not rejected by the model. | `domain.py:6,13` vs `domain.py:21` | Design Inconsistency | Medium |
| D_04 | The ID generation strategy (`max(existing_ids) + 1`) is not documented in the design and has an implicit assumption: IDs are always positive integers starting from 1. After all entities are deleted, the next ID is 1 again. This could cause confusion if external references (e.g., logs, URLs) pointed to old IDs that are reused. | `farm_service.py:20,44,80` | Design Gap | Low |
| D_05 | No design for feedback or error display in any of the HTML templates. Forms have no error message placeholder or flash message mechanism. The design assumes all operations succeed, leaving users with no recourse when a silent failure occurs. | `frontend/templates/` | Design Omission | High |

---

## Phase 3 — Coding Review

Review of the actual source code for defects against the design and standard coding practices.

| ID | Defect Description | Location | Severity |
|---|---|---|---|
| C_01 | `except ValueError as e: pass` — the exception from `register_harvest` is silently discarded. The user is redirected to `/harvests` regardless of whether the harvest was actually created. There is no indication that the operation failed. This is a functional defect: a failed action produces a success-like response. | `web.py:157-158` | High |
| C_02 | `update_harvest` constructs a `Harvest` object directly and passes it to `service.update_harvest` without calling `register_harvest`. Consequently, `field_id` and `crop_id` are never validated against existing records. A harvest can be edited to reference a field or crop that does not exist, creating a dangling reference that shows "Unknown" in the harvests list. | `web.py:180-185` | High |
| C_03 | `except ValueError as e: pass` also swallows `pydantic.ValidationError` because in Pydantic v2, `ValidationError` is a subclass of `ValueError`. Consequently, invalid `quality_rating` values (e.g., 0 or 6) submitted via the harvest form are silently discarded with no user feedback, instead of being rejected or reported. | `web.py:157-158`, `domain.py:22` | High |
| C_04 | `Field.size_hectares` has no `ge=0` Pydantic validator. Posting a negative value (e.g., `-5.0`) to `POST /fields` is accepted without error and stored in the repository. Same issue for `Crop.expected_yield_per_hectare`. | `domain.py:6,13` | Medium |
| C_05 | `edit_field_form`, `edit_crop_form`, and `edit_harvest_form` each pass a potentially `None` object to the template when a non-existent ID is requested. The templates use `{% if entity %}` guards so they do not crash, but instead silently render an empty "create" form — confusing UX. The correct response is HTTP 404 or a redirect with an error message. | `web.py:41, 87, 164` | Low |
| C_06 | In `generate_yield_report`, harvests referencing a crop ID not present in `report_data` (e.g., after direct repo manipulation) are silently skipped with no warning or log entry. This could produce a yield report that under-counts total production without any indication of data inconsistency. | `farm_service.py:101-102` | Low |
