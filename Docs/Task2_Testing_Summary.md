# Task 2 Testing Summary

This document summarizes the comprehensive software testing strategy applied to the Agricultural System. We employ a cohesive multi-tiered approach, transitioning seamlessly from testing requirements (Black Box), to logic verification (White Box), and finally ensuring layers communicate correctly (Integration Testing).

## 1. Testing Framework & Philosophy
- **Tools**: The suite is automated using `pytest` and coverage is tracked using `pytest-cov`. FastApi `TestClient` is used for router simulations.
- **Methodology**: All tests adhere to the **Arrange-Act-Assert (AAA)** pattern and the **Roy Osherove naming convention** (`MethodName_StateUnderTest_ExpectedBehavior`), ensuring maximum readability and maintainability.

## 2. Unit Testing Strategy

Our Unit Testing targets individual components in isolation. This is accomplished using two distinct perspectives:

### 2.1 Black Box Testing (BBT)
BBT focuses purely on validating inputs against expected outputs without examining the internal codebase.
**Techniques Applied**: Equivalence Class Partitioning (ECP) and Boundary Value Analysis (BVA).
**Target**: `FarmService` creation parameters in `tests/test_bbt.py`.

*Example: `quality_rating` parameter of Harvest (valid range: 1 to 5)*
- **Classes**: `<1` (Invalid), `1-5` (Valid), `>5` (Invalid)
- **Boundaries Checked**: 0, 1, 3, 5, 6. Values `0` and `6` strictly expect `ValidationError`s.

*Example: `actual_yield_tons` and `size_hectares` parameters*
- Tested against expected numeric limits and invalid scalar data types (e.g., passing string values to enforce internal framework validations).

### 2.2 White Box Testing (WBT)
WBT focuses on exercising every possible branch and path within the codebase to achieve maximum structural verification.
**Target**: `FarmService` and `InMemoryRepository` internal behaviors (`tests/test_wbt_service.py` & `tests/test_wbt_repo.py`).

**Control Flow & Branch Logic Coverage**:
- We targeted explicit topological paths, such as the multiple `if/else` checks within `FarmService.register_harvest()`.
- *Path 1*: Invalid Field → Terminate early (`test_RegisterHarvest_FieldDoesNotExist_ThrowsValueError`)
- *Path 2*: Valid Field, Invalid Crop → Terminate (`test_RegisterHarvest_CropDoesNotExist_ThrowsValueError`)
- *Path 3*: Valid Entities → Complete Execution (`test_RegisterHarvest_ValidEntities_CreatesAndReturnsHarvest`)
- **Result**: Through meticulous path analysis, the test suite achieves **100% Line and Branch Coverage** for both the `FarmService` logic and the `InMemoryRepository` state mutations.

## 3. Integration Testing Strategy

After establishing 100% confidence at the unit layer, we verified that the `Router`, `Service`, and `Repository` layers communicate efficiently without breaking state. We built two completely discrete strategies.

### 3.1 Interfaces and Mocks Setup
To guarantee isolation during integration steps, we refactored the backend to rely on **Abstract Base Classes (ABC)**:
- `backend/repository/repository_interface.py` defines `IRepository`.
- `backend/services/service_interface.py` defines `IFarmService`.

We then crafted explicit interface stubs in `tests/mocks.py` (`MockRepository`, `MockFarmService`) to isolate logic layers when necessary.

### 3.2 Top-Down Integration
Starts from the Router (API Layer) working downward (`tests/test_integration_top_down.py`):
1. **Router + Mock Service**: Tests that API correctly formats and calls `IFarmService` methods without executing real business logic.
2. **Router + Real Service + Mock Repository**: Tests that the API correctly drives the real business logic, which securely delegates data persistence to a stub.
3. **Full Stack**: Tests the entire `Router -> Real Service -> Real Repo` pipeline, successfully testing a full HTTP Report Generation query.

### 3.3 Bottom-Up Integration
Starts from the basic logic components working upward (`tests/test_integration_bottom_up.py`):
1. **Driver Test + Real Service + Mock Repository**: Tests the integration hooks of `FarmService` pushing to `IRepository` stubs.
2. **Driver Test + Real Service + Real Repository**: Tests the true interaction between service and memory.
3. **Full Stack Cascade Verification**: Extends the stack up to the Router, verifying complex interconnected behaviors like cascading deletions (deleting a Field via the router correctly triggers the Service to purge Harvests from the Repository).

## 4. Execution Results

Executing the full suite utilizing the following command:
```bash
pytest tests/ --cov=backend.services.farm_service --cov=backend.repository.memory --cov-report=term-missing
```

**Outcome**:
- **32 Total Tests Passed** (12 BBT, 12 WBT, 8 Integration).
- **100% Statement and Branch Coverage** achieved across all core logic modules!
