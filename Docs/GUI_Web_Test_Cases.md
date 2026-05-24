# GUI / Web Test Cases

**Project**: Agricultural Crop Rotation Management System
**Testing Layer**: Web (HTTP routes + rendered HTML)
**Tools**: FastAPI TestClient (automated), Browser (manual exploratory)
**Test File**: `tests/test_gui_web.py`
**Author**: denis
**Date**: 2026-05-24

---

## Test Environment

| Item | Value |
|---|---|
| Framework | FastAPI + Jinja2 |
| Test Client | `starlette.testclient.TestClient` |
| Data State | Fresh `InMemoryRepository` seeded via `seed_data()` per test |
| Naming Convention | `Feature_StateUnderTest_ExpectedBehavior` |

---

## TC-DASH — Dashboard

### TC-DASH-01
| Field | Value |
|---|---|
| **ID** | TC-DASH-01 |
| **Title** | Dashboard shows aggregated yield for all seeded crops |
| **Preconditions** | App initialized with seeded data (4 crops, 5 fields, 15 harvests) |
| **Steps** | 1. Send `GET /` |
| **Expected** | HTTP 200; response body contains crop names "Wheat", "Corn", "Soybeans", "Alfalfa" |
| **Automated** | Yes — `test_Dashboard_SeededData_ShowsCropNamesAndYields` |
| **Status** | Pass |

### TC-DASH-02
| Field | Value |
|---|---|
| **ID** | TC-DASH-02 |
| **Title** | Dashboard Wheat total yield matches sum of all Wheat harvests |
| **Preconditions** | Seeded data loaded |
| **Steps** | 1. Send `GET /` |
| **Expected** | Response body contains "152.0" (35.0 + 40.0 + 50.0 + 27.0 = 152.0 tons of Wheat) |
| **Automated** | Yes — `test_Dashboard_SeededData_WheatYieldIsCorrect` |
| **Status** | Pass |

---

## TC-FIELD — Field Management

### TC-FIELD-01
| Field | Value |
|---|---|
| **ID** | TC-FIELD-01 |
| **Title** | Field list page shows all seeded fields |
| **Preconditions** | Seeded data loaded |
| **Steps** | 1. Send `GET /fields` |
| **Expected** | HTTP 200; response contains "North Plot", "South Plot", "East Meadow", "West Acre", "Central Basin" |
| **Automated** | Yes — `test_ListFields_SeededData_ShowsAllFiveFields` |
| **Status** | Pass |

### TC-FIELD-02
| Field | Value |
|---|---|
| **ID** | TC-FIELD-02 |
| **Title** | New field form renders correctly |
| **Preconditions** | App running |
| **Steps** | 1. Send `GET /fields/new` |
| **Expected** | HTTP 200; response contains `<form` and inputs for name, size_hectares, soil_type |
| **Automated** | Yes — `test_NewFieldForm_Request_Returns200WithForm` |
| **Status** | Pass |

### TC-FIELD-03
| Field | Value |
|---|---|
| **ID** | TC-FIELD-03 |
| **Title** | Creating a valid field redirects to /fields and field appears in list |
| **Preconditions** | Seeded data loaded |
| **Steps** | 1. POST `/fields` with `name=River Plot`, `size_hectares=7.5`, `soil_type=Sandy` 2. GET `/fields` |
| **Expected** | POST returns 303 redirect to `/fields`; subsequent GET shows "River Plot" |
| **Automated** | Yes — `test_CreateField_ValidInput_AppearsInFieldsList` |
| **Status** | Pass |

### TC-FIELD-04
| Field | Value |
|---|---|
| **ID** | TC-FIELD-04 |
| **Title** | Negative size_hectares is accepted without error (BUG-01 / C_05) |
| **Preconditions** | Seeded data loaded |
| **Steps** | 1. POST `/fields` with `name=Bad Field`, `size_hectares=-10.0`, `soil_type=Clay` |
| **Expected** | **Current behavior**: 303 redirect, field stored with negative size (defect — should be rejected). Correct behavior: HTTP 422 or re-render form with error. |
| **Automated** | Yes — `test_CreateField_NegativeSizeHectares_AcceptedByServer` |
| **Status** | Fail (defect confirmed) |

### TC-FIELD-05
| Field | Value |
|---|---|
| **ID** | TC-FIELD-05 |
| **Title** | Edit field form is pre-filled with existing data |
| **Preconditions** | Seeded data: Field ID 1 = "North Plot", 10.5 ha, Clay Loam |
| **Steps** | 1. Send `GET /fields/1/edit` |
| **Expected** | HTTP 200; response contains "North Plot", "10.5", "Clay Loam" |
| **Automated** | Yes — `test_EditField_ExistingId_Returns200WithPrefilledData` |
| **Status** | Pass |

### TC-FIELD-06
| Field | Value |
|---|---|
| **ID** | TC-FIELD-06 |
| **Title** | Edit form for non-existent field ID silently shows a create form (UX defect) |
| **Preconditions** | No field with ID 9999 |
| **Steps** | 1. Send `GET /fields/9999/edit` |
| **Expected** | **Current behavior**: HTTP 200, shows "Register New Field" form (template guards on `{% if field %}`). Correct behavior: HTTP 404 or redirect with error message. |
| **Automated** | Yes — `test_EditField_NonExistentId_ShowsNewFieldForm` |
| **Status** | Pass (defect is UX regression — no crash, but misleading form shown) |

### TC-FIELD-07
| Field | Value |
|---|---|
| **ID** | TC-FIELD-07 |
| **Title** | Updating a field reflects changes in the list |
| **Preconditions** | Seeded data: Field ID 1 = "North Plot" |
| **Steps** | 1. POST `/fields/1/update` with `name=North Plot Updated`, `size_hectares=11.0`, `soil_type=Clay Loam` 2. GET `/fields` |
| **Expected** | POST returns 303; GET shows "North Plot Updated" |
| **Automated** | Yes — `test_UpdateField_ValidInput_ChangesAppearInList` |
| **Status** | Pass |

### TC-FIELD-08
| Field | Value |
|---|---|
| **ID** | TC-FIELD-08 |
| **Title** | Deleting a field removes it from the list |
| **Preconditions** | Seeded data: Field ID 1 exists |
| **Steps** | 1. POST `/fields/1/delete` 2. GET `/fields` |
| **Expected** | POST returns 303; GET does not contain "North Plot" |
| **Automated** | Yes — `test_DeleteField_ExistingId_FieldRemovedFromList` |
| **Status** | Pass |

### TC-FIELD-09
| Field | Value |
|---|---|
| **ID** | TC-FIELD-09 |
| **Title** | Deleting a field also removes its associated harvests (cascade) |
| **Preconditions** | Seeded data: Field 1 has harvests 1, 6, 11 |
| **Steps** | 1. POST `/fields/1/delete` 2. GET `/harvests` |
| **Expected** | Harvests that referenced Field 1 are no longer in the list |
| **Automated** | Yes — `test_DeleteField_WithHarvests_CascadeDeletesHarvests` |
| **Status** | Pass |

---

## TC-CROP — Crop Management

### TC-CROP-01
| Field | Value |
|---|---|
| **ID** | TC-CROP-01 |
| **Title** | Crop list page shows all seeded crops |
| **Preconditions** | Seeded data loaded |
| **Steps** | 1. Send `GET /crops` |
| **Expected** | HTTP 200; response contains "Wheat", "Corn", "Soybeans", "Alfalfa" |
| **Automated** | Yes — `test_ListCrops_SeededData_ShowsAllFourCrops` |
| **Status** | Pass |

### TC-CROP-02
| Field | Value |
|---|---|
| **ID** | TC-CROP-02 |
| **Title** | Creating a valid crop appears in the crop list |
| **Preconditions** | Seeded data loaded |
| **Steps** | 1. POST `/crops` with `name=Barley`, `expected_yield_per_hectare=4.2`, `season=Autumn` 2. GET `/crops` |
| **Expected** | POST returns 303; GET shows "Barley" |
| **Automated** | Yes — `test_CreateCrop_ValidInput_AppearsInCropsList` |
| **Status** | Pass |

### TC-CROP-03
| Field | Value |
|---|---|
| **ID** | TC-CROP-03 |
| **Title** | Deleting a crop also removes its associated harvests (cascade) |
| **Preconditions** | Seeded data: Crop 1 (Wheat) has harvests 1, 5, 7, 13 |
| **Steps** | 1. POST `/crops/1/delete` 2. GET `/harvests` |
| **Expected** | Harvests referencing Crop 1 are no longer listed |
| **Automated** | Yes — `test_DeleteCrop_WithHarvests_CascadeDeletesHarvests` |
| **Status** | Pass |

---

## TC-HARV — Harvest Management

### TC-HARV-01
| Field | Value |
|---|---|
| **ID** | TC-HARV-01 |
| **Title** | Harvest list shows joined field and crop names |
| **Preconditions** | Seeded data loaded |
| **Steps** | 1. Send `GET /harvests` |
| **Expected** | HTTP 200; response contains "North Plot", "Wheat", "Corn" (joined names, not IDs) |
| **Automated** | Yes — `test_ListHarvests_SeededData_ShowsFieldAndCropNames` |
| **Status** | Pass |

### TC-HARV-02
| Field | Value |
|---|---|
| **ID** | TC-HARV-02 |
| **Title** | New harvest form shows field and crop dropdowns |
| **Preconditions** | Seeded data loaded |
| **Steps** | 1. Send `GET /harvests/new` |
| **Expected** | HTTP 200; response contains `<select` elements with seeded field and crop names |
| **Automated** | Yes — `test_NewHarvestForm_ShowsFieldAndCropDropdowns` |
| **Status** | Pass |

### TC-HARV-03
| Field | Value |
|---|---|
| **ID** | TC-HARV-03 |
| **Title** | Creating a valid harvest appears in the harvests list |
| **Preconditions** | Seeded data: Field 1, Crop 1 exist |
| **Steps** | 1. POST `/harvests` with valid field_id=1, crop_id=1, harvest_date=2026-05-24, actual_yield_tons=10.0, quality_rating=3 2. GET `/harvests` |
| **Expected** | POST returns 303; new harvest appears in list |
| **Automated** | Yes — `test_CreateHarvest_ValidInput_AppearsInHarvestsList` |
| **Status** | Pass |

### TC-HARV-04
| Field | Value |
|---|---|
| **ID** | TC-HARV-04 |
| **Title** | Creating harvest with non-existent field_id silently fails with no user feedback (BUG-02 / C_01) |
| **Preconditions** | No field with ID 999 exists |
| **Steps** | 1. POST `/harvests` with field_id=999, crop_id=1, harvest_date=2026-05-24, actual_yield_tons=5.0, quality_rating=2 2. GET `/harvests` |
| **Expected** | **Current behavior**: POST returns 303, harvest is NOT created, no error shown (defect). Correct behavior: error message displayed to user. |
| **Automated** | Yes — `test_CreateHarvest_NonExistentFieldId_SilentlyFails` |
| **Status** | Fail (defect confirmed) |

### TC-HARV-05
| Field | Value |
|---|---|
| **ID** | TC-HARV-05 |
| **Title** | quality_rating=0 silently fails — ValidationError swallowed by `except ValueError` (C_03) |
| **Preconditions** | Seeded data loaded |
| **Steps** | 1. POST `/harvests` with quality_rating=0, valid field_id=1, crop_id=1 2. Count rows in `GET /harvests` before and after |
| **Expected** | **Current behavior**: 303 redirect, harvest NOT created, no error shown. `pydantic.ValidationError` (which IS-A `ValueError` in Pydantic v2) is caught by `except ValueError: pass`. Correct behavior: HTTP 422 or form re-render with error. |
| **Automated** | Yes — `test_CreateHarvest_QualityRatingZero_SilentlyFails` |
| **Status** | Fail (defect confirmed — same silent failure mechanism as BUG-02) |

### TC-HARV-06
| Field | Value |
|---|---|
| **ID** | TC-HARV-06 |
| **Title** | quality_rating=6 silently fails — ValidationError swallowed by `except ValueError` (C_03) |
| **Preconditions** | Seeded data loaded |
| **Steps** | 1. POST `/harvests` with quality_rating=6, valid field_id=1, crop_id=1 2. Count rows in `GET /harvests` before and after |
| **Expected** | **Current behavior**: 303 redirect, harvest NOT created, no error shown. Correct behavior: HTTP 422 or form re-render. |
| **Automated** | Yes — `test_CreateHarvest_QualityRatingSix_SilentlyFails` |
| **Status** | Fail (defect confirmed) |

### TC-HARV-07
| Field | Value |
|---|---|
| **ID** | TC-HARV-07 |
| **Title** | Updating harvest with non-existent field_id succeeds without validation (BUG-03 / C_02) |
| **Preconditions** | Seeded data: Harvest 1 exists; no field with ID 999 |
| **Steps** | 1. POST `/harvests/1/update` with field_id=999, crop_id=1, harvest_date=2024-01-01, actual_yield_tons=5.0, quality_rating=3 2. GET `/harvests` |
| **Expected** | **Current behavior**: update accepted, harvest shows "Unknown" as field name (defect). Correct behavior: error or rejection. |
| **Automated** | Yes — `test_UpdateHarvest_NonExistentFieldId_AcceptsWithoutValidation` |
| **Status** | Fail (defect confirmed) |

### TC-HARV-08
| Field | Value |
|---|---|
| **ID** | TC-HARV-08 |
| **Title** | Deleting a harvest removes it from the list |
| **Preconditions** | Seeded data: Harvest ID 1 exists |
| **Steps** | 1. POST `/harvests/1/delete` 2. GET `/harvests` count vs before |
| **Expected** | POST returns 303; harvest list has one fewer entry |
| **Automated** | Yes — `test_DeleteHarvest_ExistingId_RemovesFromList` |
| **Status** | Pass |

### TC-HARV-09
| Field | Value |
|---|---|
| **ID** | TC-HARV-09 |
| **Title** | Edit harvest form for non-existent ID silently shows create form (UX defect) |
| **Preconditions** | No harvest with ID 9999 |
| **Steps** | 1. Send `GET /harvests/9999/edit` |
| **Expected** | **Current behavior**: HTTP 200, shows empty create form (template guards on `{% if harvest %}`). Correct behavior: HTTP 404 or redirect with error. |
| **Automated** | Yes — `test_EditHarvest_NonExistentId_ShowsNewHarvestForm` |
| **Status** | Pass (UX defect noted — misleading empty form, not a crash) |

---

## Defect Summary

| Bug ID | Test Case | Description | Severity |
|---|---|---|---|
| BUG-01 / C_04 | TC-FIELD-04 | Negative `size_hectares` accepted without validation | Medium |
| BUG-02 / C_01 | TC-HARV-04 | Silent failure on harvest creation with bad field_id | High |
| BUG-03 / C_02 | TC-HARV-07 | Harvest update bypasses field_id/crop_id validation | High |
| BUG-04 / C_03 | TC-HARV-05, TC-HARV-06 | `pydantic.ValidationError` swallowed by `except ValueError`; invalid quality_rating silently accepted | High |
| BUG-05 (UX) / C_05 | TC-FIELD-06, TC-HARV-09 | Edit form for non-existent ID silently shows create form instead of 404 | Low |
