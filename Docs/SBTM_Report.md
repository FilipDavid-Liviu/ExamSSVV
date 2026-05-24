# Session-Based Test Management (SBTM) Report

**Project**: Agricultural Crop Rotation Management System
**Testing Type**: Exploratory Testing
**Tester**: denis (denisgre205@gmail.com)
**Period**: 2026-05-24

---

## Overall Summary

| Metric | Value |
|---|---|
| Total Sessions | 4 |
| Total Duration (hours) | 1.50 |
| Bugs Found | 6 |
| Questions / Open Items | 3 |
| Next-Time Ideas | 2 |

---

## Time Breakdown (across all sessions)

| Activity | Hours | % |
|---|---|---|
| Test Execution | 0.95 | 63% |
| Session Setup | 0.25 | 17% |
| Bug Investigation | 0.30 | 20% |

---

## Area Summary

| Area | Sessions | Duration (hrs) | Bugs Found |
|---|---|---|---|
| CRUD — Fields & Crops | 1 | 0.35 | 1 |
| HARVEST VALIDATION | 1 | 0.40 | 3 |
| REPORTING & CASCADE | 1 | 0.35 | 1 |
| NAVIGATION & UI | 1 | 0.40 | 1 |

---

## Session Sheets

---

### Session ET-01

| Field | Value |
|---|---|
| Session ID | ET-01 |
| Charter | Explore field and crop CRUD operations — boundary inputs, empty states, and data persistence across page navigations |
| Area | CRUD — Fields & Crops |
| Tester | denis |
| Date | 2026-05-24 |
| Start Time | 09:00 |
| Duration | 0.35 hrs (~21 min) |

**Time Breakdown**

| Activity | Time |
|---|---|
| Setup (app start, navigation orientation) | 5 min |
| Test Execution | 12 min |
| Bug Investigation | 4 min |

**Test Notes**

- Navigated to `/fields` — all 5 seeded fields displayed correctly (North Plot, South Plot, East Meadow, West Acre, Central Basin).
- Created a new field via `/fields/new` with valid data (name: "Test Plot", size: 5.5, soil: "Loam") — field appeared immediately in list. **Pass.**
- Attempted to create a field with `size_hectares = -10.0` — **accepted without error**. Negative field size stored and displayed as "-10.0 ha". This should be rejected.
- Created a crop via `/crops/new` with `expected_yield_per_hectare = -3.0` — **accepted without error**. Same validation gap as fields.
- Edited an existing field (North Plot) — form pre-filled correctly. Updated name to "North Plot (Edit Test)" — change reflected in list. **Pass.**
- Deleted a field — immediately removed from list. Navigated back to confirm. **Pass.**
- Tested empty state: deleted all fields manually — page showed "No fields registered." **Pass.**

**Bugs Found**

| Bug ID | Description | Severity |
|---|---|---|
| BUG-01 | Negative values for `size_hectares` (Field) and `expected_yield_per_hectare` (Crop) are accepted and stored without validation. Domain model lacks `ge=0` constraint on these fields. | Medium |

**Questions / Ideas**

- Q1: Should field names be unique? Currently two fields can share the same name, which is confusing in harvest registration dropdowns.
- Idea: Add client-side input validation (HTML `min` attribute on number fields in `field_form.html` and `crop_form.html`).

---

### Session ET-02

| Field | Value |
|---|---|
| Session ID | ET-02 |
| Charter | Explore harvest registration — boundary values for quality_rating, invalid field/crop IDs, yield values, and the error handling path |
| Area | HARVEST VALIDATION |
| Tester | denis |
| Date | 2026-05-24 |
| Start Time | 09:30 |
| Duration | 0.40 hrs (~24 min) |

**Time Breakdown**

| Activity | Time |
|---|---|
| Setup | 3 min |
| Test Execution | 14 min |
| Bug Investigation | 7 min |

**Test Notes**

- Navigated to `/harvests/new` — dropdowns for fields and crops populate correctly from seeded data. **Pass.**
- Registered a valid harvest (Field: North Plot, Crop: Wheat, Date: 2026-05-24, Yield: 12.5, Quality: 3) — appeared in harvests list. **Pass.**
- Tested quality_rating boundaries using browser DevTools to modify the form value before submission:
  - Rating = 0: **Pydantic ValidationError → 422 response.** Correctly rejected.
  - Rating = 1: Accepted. **Pass.**
  - Rating = 5: Accepted. **Pass.**
  - Rating = 6: **Pydantic ValidationError → 422 response.** Correctly rejected.
- Attempted to register a harvest by manually POSTing with a non-existent `field_id=999` (via curl/DevTools) — **page silently redirects to `/harvests`. Harvest was NOT created, but user receives NO error message.** This is a critical UX defect.
- Attempted to edit an existing harvest and changed `field_id` to a non-existent ID (999) via DevTools — **edit succeeded.** The harvest was saved with `field_id=999`. Harvests list shows "Unknown" as field name. This is a data integrity defect.
- Tested `actual_yield_tons = -5.0` directly via POST — **Pydantic ValidationError → 422.** Correctly rejected.
- Attempted `actual_yield_tons = 0.0` — accepted. **Pass** (boundary is `ge=0`).

**Bugs Found**

| Bug ID | Description | Severity |
|---|---|---|
| BUG-02 | Silent failure on harvest registration with non-existent field/crop ID. User is redirected to `/harvests` with no feedback indicating the harvest was not created. (`web.py:157-158`: `except ValueError as e: pass`) | High |
| BUG-03 | Harvest edit (`POST /harvests/{id}/update`) does not validate `field_id` or `crop_id` existence. A harvest can be updated to reference a non-existent field or crop, producing "Unknown" in the harvests list. | High |
| BUG-04 | Accessing `GET /harvests/{id}/edit` with a non-existent ID results in a 500 Internal Server Error because the template attempts to access attributes on a `None` harvest object. | Medium |

**Questions / Ideas**

- Q2: Should harvest date be restricted to past dates only? Currently future harvest dates (e.g., 2099-12-31) are accepted.

---

### Session ET-03

| Field | Value |
|---|---|
| Session ID | ET-03 |
| Charter | Explore the dashboard yield report accuracy and cascade delete behavior across fields, crops, and harvests |
| Area | REPORTING & CASCADE |
| Tester | denis |
| Date | 2026-05-24 |
| Start Time | 10:00 |
| Duration | 0.35 hrs (~21 min) |

**Time Breakdown**

| Activity | Time |
|---|---|
| Setup | 4 min |
| Test Execution | 12 min |
| Bug Investigation | 5 min |

**Test Notes**

- Visited dashboard `/` — yield report shows all 4 crops with aggregated total yields. Manually verified Wheat total: 35.0 + 40.0 + 50.0 + 27.0 = **152.0 tons**. Dashboard matched. **Pass.**
- Added a new harvest (Wheat, 10.0 tons) then refreshed dashboard — Wheat total updated to 162.0. **Pass.**
- Deleted a field (North Plot, which has 3 associated harvests) — field removed. Navigated to `/harvests` — North Plot harvests (IDs 1, 6, 11) are gone. Dashboard yield totals updated accordingly. Cascade delete works. **Pass.**
- Deleted a crop (Corn, which has 3 associated harvests) — navigated to `/harvests` — Corn harvests gone. Dashboard no longer shows Corn row. **Pass.**
- Created a harvest, then manually noted its ID. Deleted the crop referenced by the harvest directly. Then navigated to `/harvests` — the harvest was already removed via cascade. **Pass.**
- Verified: after all harvests for a crop are deleted, the crop still appears in the crops list (only the harvest records are removed, not the crop itself). **Pass** — correct behavior.
- Created a harvest for a field+crop, then deleted the field. Verified the crop still exists and can be used for new harvests. **Pass.**

**Bugs Found**

| Bug ID | Description | Severity |
|---|---|---|
| BUG-05 | After manually crafting a harvest that references a deleted crop (via direct POST with devtools, exploiting BUG-03), `generate_yield_report` silently skips that harvest's yield. The dashboard total is lower than the actual total without any warning to the user. | Low |

**Questions / Ideas**

- Idea: Add a "Last Updated" timestamp to the dashboard report so users know how current the data is.

---

### Session ET-04

| Field | Value |
|---|---|
| Session ID | ET-04 |
| Charter | Explore navigation links, URL manipulation, confirmation dialogs, and overall UI consistency across all pages |
| Area | NAVIGATION & UI |
| Tester | denis |
| Date | 2026-05-24 |
| Start Time | 10:30 |
| Duration | 0.40 hrs (~24 min) |

**Time Breakdown**

| Activity | Time |
|---|---|
| Setup | 3 min |
| Test Execution | 17 min |
| Bug Investigation | 4 min |

**Test Notes**

- Verified navigation bar links: Home (→ `/`), Fields (→ `/fields`), Crops (→ `/crops`), Harvests (→ `/harvests`) — all functional. **Pass.**
- "Add New Field" button on `/fields` links to `/fields/new`. **Pass.** Same for crops and harvests.
- Confirmed delete buttons on harvests list show a JavaScript `confirm()` dialog before submitting. **Pass.**
- Tested URL manipulation: navigated directly to `/fields/9999/edit` (non-existent ID) — **500 Internal Server Error**. Expected: a 404 or redirect with a message. This is a UX defect.
- Same test for `/crops/9999/edit` — **500 Internal Server Error**. Same defect.
- Same test for `/harvests/9999/edit` — **500 Internal Server Error**. Same defect.
- Accessed `/fields/new` directly (no referrer) — form displays correctly. **Pass.**
- Checked form labels and input types: all number inputs have appropriate `type="number"` and `step` attributes in harvest form. Field and crop forms missing `min="0"` on numeric inputs (consistent with BUG-01).
- Tested back-navigation after creating a field — browser back button goes to `/fields/new` form, which is harmless (empty form re-displayed). **Pass.**
- Verified that deleting a non-existent entity via `POST /fields/9999/delete` returns a redirect to `/fields` with no error — silent no-op. **Acceptable behavior** but worth documenting.

**Bugs Found**

| Bug ID | Description | Severity |
|---|---|---|
| BUG-06 | Navigating to `/fields/{id}/edit`, `/crops/{id}/edit`, or `/harvests/{id}/edit` with a non-existent ID causes a 500 Internal Server Error because the template receives a `None` object. Should return 404 or redirect with an error message. | Medium |

**Questions / Ideas**

- Q3: Should there be a confirmation step for deleting fields or crops (given they cascade-delete all associated harvests)? Currently only harvest delete has a `confirm()` dialog. Deleting a field silently removes all its harvests.
