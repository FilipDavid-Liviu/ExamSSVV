# Task 3 Testing Summary

This document summarizes the additional software testing techniques applied to the Agricultural System, extending the foundation from Task 2. Three techniques are covered: Inspection/Code Review, Exploratory Testing (SBTM), and GUI/Web Testing.

## 1. Testing Framework & Philosophy

- **Tools**: Inspection conducted manually; exploratory sessions followed the SBTM (Session-Based Test Management) methodology; GUI/web tests automated using FastAPI `TestClient`.
- **Methodology**: All automated tests adhere to the **Arrange-Act-Assert (AAA)** pattern and the **Roy Osherove naming convention** (`MethodName_StateUnderTest_ExpectedBehavior`).

---

## 2. Inspection / Code Review

A formal walkthrough of the codebase was conducted across three phases: Requirements, Unit Design, and Coding. The review follows the structure of standard inspection forms (Lab01 format).

**Document**: `Docs/Review_Form.md`

**Review Scope**:

| Module | File |
|---|---|
| Domain Models | `backend/models/domain.py` |
| Repository | `backend/repository/memory.py` |
| Service | `backend/services/farm_service.py` |
| Web Router | `backend/routers/web.py` |

**Summary of defects found**:

| Phase | Defects Found | Highlights |
|---|---|---|
| Requirements | 6 | No enumeration of valid `season` / `soil_type` values; no field name uniqueness requirement; unspecified behavior when editing a harvest with a non-existent field/crop ID |
| Design | 5 | Silent failure path for `register_harvest` errors not designed into the UI; `update_harvest` bypasses validation; inconsistent `ge=0` constraints across domain models |
| Coding | 6 | `except ValueError: pass` in `web.py:157` swallows both `ValueError` and Pydantic's `ValidationError` (which is a `ValueError` subclass); `update_harvest` stores dangling field/crop references; missing `ge=0` validators on `Field` and `Crop` models |

**Key finding**: `pydantic.ValidationError` is a subclass of `ValueError` in Pydantic v2. The broad `except ValueError: pass` block in `web.py:157-158` therefore silently discards all Pydantic model validation errors raised inside `register_harvest`, including out-of-range `quality_rating` values. This amplifies the blast radius of a single poorly-scoped exception handler.

---

## 3. Exploratory Testing (SBTM)

Session-based exploratory testing was performed in 4 focused sessions following the SBTM methodology. Each session had a specific charter, a time budget, and produced structured findings.

**Document**: `Docs/SBTM_Report.md`

| Session | Charter Area | Duration | Bugs Found |
|---|---|---|---|
| ET-01 | CRUD — Fields & Crops | 0.35 hrs | 1 |
| ET-02 | Harvest Validation & Error Handling | 0.40 hrs | 3 |
| ET-03 | Reporting & Cascade Delete | 0.35 hrs | 1 |
| ET-04 | Navigation & UI Consistency | 0.40 hrs | 1 |
| **Total** | | **1.50 hrs** | **6 bugs** |

**Time Breakdown (all sessions)**:

| Activity | Hours | % |
|---|---|---|
| Test Execution | 0.95 | 63% |
| Session Setup | 0.25 | 17% |
| Bug Investigation | 0.30 | 20% |

**Key bugs surfaced**:
- **BUG-01**: Negative `size_hectares` (Field) and `expected_yield_per_hectare` (Crop) accepted and stored without error — no `ge=0` validator on these fields.
- **BUG-02**: Silent failure when registering a harvest with a non-existent `field_id` or `crop_id` — user receives no feedback, redirect happens as if success.
- **BUG-03**: Harvest edit bypasses field/crop existence validation — dangling references stored, showing "Unknown" in the harvests list.
- **BUG-04**: Navigating to `/fields/{bad_id}/edit` or similar with a non-existent ID shows an empty create form instead of a 404.
- **Open questions**: Should harvest dates be restricted to the past? Should field names be unique?

---

## 4. GUI / Web Testing

Formal test cases were defined covering all web routes and rendered HTML. Tests are automated using FastAPI's `TestClient` with a fresh seeded `InMemoryRepository` per test, ensuring full isolation between tests.

**Test Case Document**: `Docs/GUI_Web_Test_Cases.md`
**Test Code**: `tests/test_gui_web.py`

**Coverage by area**:

| Area | Test Cases | Pass | Defect confirmed |
|---|---|---|---|
| Dashboard | 2 | 2 | 0 |
| Fields | 9 | 9 | 2 (documented behavior) |
| Crops | 3 | 3 | 0 |
| Harvests | 15 | 15 | 3 (documented behavior) |
| **Total** | **29** | **29** | **5** |

All 29 tests pass. Tests that document confirmed defects assert the *current (buggy) behavior* so they act as regression guards — they will need to be updated when the defects are fixed.

**Notable test patterns**:
- `test_CreateHarvest_NonExistentFieldId_SilentlyFails` — verifies harvest count is unchanged after a silently-failed POST.
- `test_UpdateHarvest_NonExistentFieldId_AcceptsWithoutValidation` — verifies "Unknown" appears in the list after storing a dangling reference.
- `test_CreateHarvest_QualityRatingZero_SilentlyFails` / `test_CreateHarvest_QualityRatingSix_SilentlyFails` — demonstrates that Pydantic `ValidationError` is swallowed by `except ValueError`.

---

## 5. Execution Results

Executing the full test suite (Tasks 2 + 3):

```bash
pytest tests/ -v
```

**Outcome**:
- **61 Total Tests Passed** (12 BBT + 12 WBT + 8 Integration + 29 GUI/Web).
- **100% Statement and Branch Coverage** maintained across all core logic modules.
- All GUI/Web tests pass; defects are documented as behavioral assertions rather than expected failures.
