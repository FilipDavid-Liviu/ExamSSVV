import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.routers.web import get_farm_service
from backend.services.farm_service import FarmService
from backend.repository.memory import InMemoryRepository
from backend.repository.seed import seed_data


@pytest.fixture
def client():
    repo = InMemoryRepository()
    seed_data(repo)
    service = FarmService(repo)
    app.dependency_overrides[get_farm_service] = lambda: service
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


# ─── DASHBOARD ────────────────────────────────────────────────────────────────

def test_Dashboard_SeededData_ShowsCropNamesAndYields(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Wheat" in response.content
    assert b"Corn" in response.content
    assert b"Soybeans" in response.content
    assert b"Alfalfa" in response.content


def test_Dashboard_SeededData_WheatYieldIsCorrect(client):
    # Wheat harvests: id 1(35.0) + 5(40.0) + 7(50.0) + 13(27.0) = 152.0
    response = client.get("/")
    assert response.status_code == 200
    assert b"152.0" in response.content


# ─── FIELDS ───────────────────────────────────────────────────────────────────

def test_ListFields_SeededData_ShowsAllFiveFields(client):
    response = client.get("/fields")
    assert response.status_code == 200
    assert b"North Plot" in response.content
    assert b"South Plot" in response.content
    assert b"East Meadow" in response.content
    assert b"West Acre" in response.content
    assert b"Central Basin" in response.content


def test_NewFieldForm_Request_Returns200WithForm(client):
    response = client.get("/fields/new")
    assert response.status_code == 200
    assert b"<form" in response.content


def test_CreateField_ValidInput_AppearsInFieldsList(client):
    client.post("/fields", data={"name": "River Plot", "size_hectares": "7.5", "soil_type": "Sandy"})
    response = client.get("/fields")
    assert b"River Plot" in response.content


def test_CreateField_ValidInput_RedirectsToFields(client):
    response = client.post(
        "/fields",
        data={"name": "River Plot", "size_hectares": "7.5", "soil_type": "Sandy"},
        follow_redirects=False
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/fields"


def test_CreateField_NegativeSizeHectares_AcceptedByServer(client):
    # BUG-01 / C_05: domain.py missing ge=0 on size_hectares — negative value is stored
    response = client.post(
        "/fields",
        data={"name": "Bad Field", "size_hectares": "-10.0", "soil_type": "Clay"},
        follow_redirects=False
    )
    assert response.status_code == 303
    list_response = client.get("/fields")
    assert b"Bad Field" in list_response.content


def test_EditField_ExistingId_Returns200WithPrefilledData(client):
    response = client.get("/fields/1/edit")
    assert response.status_code == 200
    assert b"North Plot" in response.content
    assert b"10.5" in response.content
    assert b"Clay Loam" in response.content


def test_EditField_NonExistentId_ShowsNewFieldForm(client):
    # Template uses {% if field %} guards — None renders as an empty create form (200).
    # UX defect: user navigating to a bad edit URL silently gets a create form instead of 404.
    response = client.get("/fields/9999/edit")
    assert response.status_code == 200
    assert b"Register New Field" in response.content


def test_UpdateField_ValidInput_ChangesAppearInList(client):
    client.post(
        "/fields/1/update",
        data={"name": "North Plot Updated", "size_hectares": "11.0", "soil_type": "Clay Loam"}
    )
    response = client.get("/fields")
    assert b"North Plot Updated" in response.content


def test_DeleteField_ExistingId_FieldRemovedFromList(client):
    client.post("/fields/1/delete")
    response = client.get("/fields")
    assert b"North Plot" not in response.content


def test_DeleteField_WithHarvests_CascadeDeletesHarvests(client):
    # Field 1 has harvests 1, 6, 11 in seeded data
    harvests_before = client.get("/harvests").content
    assert b"North Plot" in harvests_before
    client.post("/fields/1/delete")
    harvests_after = client.get("/harvests").content
    assert b"North Plot" not in harvests_after


# ─── CROPS ────────────────────────────────────────────────────────────────────

def test_ListCrops_SeededData_ShowsAllFourCrops(client):
    response = client.get("/crops")
    assert response.status_code == 200
    assert b"Wheat" in response.content
    assert b"Corn" in response.content
    assert b"Soybeans" in response.content
    assert b"Alfalfa" in response.content


def test_NewCropForm_Request_Returns200WithForm(client):
    response = client.get("/crops/new")
    assert response.status_code == 200
    assert b"<form" in response.content


def test_CreateCrop_ValidInput_AppearsInCropsList(client):
    client.post("/crops", data={"name": "Barley", "expected_yield_per_hectare": "4.2", "season": "Autumn"})
    response = client.get("/crops")
    assert b"Barley" in response.content


def test_DeleteCrop_WithHarvests_CascadeDeletesHarvests(client):
    # Crop 1 (Wheat) has harvests 1, 5, 7, 13 in seeded data
    harvests_before = client.get("/harvests").content
    assert b"Wheat" in harvests_before
    client.post("/crops/1/delete")
    harvests_after = client.get("/harvests").content
    assert b"Wheat" not in harvests_after


# ─── HARVESTS ─────────────────────────────────────────────────────────────────

def test_ListHarvests_SeededData_ShowsFieldAndCropNames(client):
    response = client.get("/harvests")
    assert response.status_code == 200
    assert b"North Plot" in response.content
    assert b"Wheat" in response.content
    assert b"Corn" in response.content


def test_NewHarvestForm_ShowsFieldAndCropDropdowns(client):
    response = client.get("/harvests/new")
    assert response.status_code == 200
    assert b"<select" in response.content
    assert b"North Plot" in response.content
    assert b"Wheat" in response.content


def test_CreateHarvest_ValidInput_AppearsInHarvestsList(client):
    client.post("/harvests", data={
        "field_id": "1", "crop_id": "1",
        "harvest_date": "2026-05-24",
        "actual_yield_tons": "10.0",
        "quality_rating": "3"
    })
    response = client.get("/harvests")
    assert b"North Plot" in response.content


def test_CreateHarvest_ValidInput_RedirectsToHarvests(client):
    response = client.post("/harvests", data={
        "field_id": "1", "crop_id": "1",
        "harvest_date": "2026-05-24",
        "actual_yield_tons": "10.0",
        "quality_rating": "3"
    }, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/harvests"


def test_CreateHarvest_NonExistentFieldId_SilentlyFails(client):
    # BUG-02 / C_01: ValueError is caught and discarded; harvest not created but user sees no error
    harvests_before = len(client.get("/harvests").content)
    client.post("/harvests", data={
        "field_id": "999", "crop_id": "1",
        "harvest_date": "2026-05-24",
        "actual_yield_tons": "5.0",
        "quality_rating": "2"
    })
    response = client.get("/harvests")
    # Harvest count unchanged — harvest was not added (silent failure)
    assert len(response.content) == harvests_before


def test_CreateHarvest_QualityRatingZero_SilentlyFails(client):
    # pydantic.ValidationError IS-A ValueError in Pydantic v2, so it is caught by
    # `except ValueError: pass` in web.py — same silent failure as BUG-02.
    # Correct behavior: 422 or re-render form with error.
    harvests_before = client.get("/harvests").content.count(b"<tr")
    client.post("/harvests", data={
        "field_id": "1", "crop_id": "1",
        "harvest_date": "2026-05-24",
        "actual_yield_tons": "10.0",
        "quality_rating": "0"
    })
    harvests_after = client.get("/harvests").content.count(b"<tr")
    assert harvests_after == harvests_before


def test_CreateHarvest_QualityRatingSix_SilentlyFails(client):
    # Same silent failure as quality_rating=0 — ValidationError swallowed.
    harvests_before = client.get("/harvests").content.count(b"<tr")
    client.post("/harvests", data={
        "field_id": "1", "crop_id": "1",
        "harvest_date": "2026-05-24",
        "actual_yield_tons": "10.0",
        "quality_rating": "6"
    })
    harvests_after = client.get("/harvests").content.count(b"<tr")
    assert harvests_after == harvests_before


def test_CreateHarvest_QualityRatingOne_IsAccepted(client):
    response = client.post("/harvests", data={
        "field_id": "1", "crop_id": "1",
        "harvest_date": "2026-05-24",
        "actual_yield_tons": "10.0",
        "quality_rating": "1"
    }, follow_redirects=False)
    assert response.status_code == 303


def test_CreateHarvest_QualityRatingFive_IsAccepted(client):
    response = client.post("/harvests", data={
        "field_id": "1", "crop_id": "1",
        "harvest_date": "2026-05-24",
        "actual_yield_tons": "10.0",
        "quality_rating": "5"
    }, follow_redirects=False)
    assert response.status_code == 303


def test_EditHarvest_ExistingId_Returns200WithForm(client):
    response = client.get("/harvests/1/edit")
    assert response.status_code == 200
    assert b"<form" in response.content


def test_EditHarvest_NonExistentId_ShowsNewHarvestForm(client):
    # Same as TC-FIELD-06: template guards on None, returns 200 with empty create form.
    response = client.get("/harvests/9999/edit")
    assert response.status_code == 200


def test_UpdateHarvest_NonExistentFieldId_AcceptsWithoutValidation(client):
    # BUG-03 / C_02: update_harvest bypasses register_harvest; no existence check on field_id
    response = client.post("/harvests/1/update", data={
        "field_id": "999", "crop_id": "1",
        "harvest_date": "2024-01-01",
        "actual_yield_tons": "5.0",
        "quality_rating": "3"
    }, follow_redirects=False)
    assert response.status_code == 303
    list_response = client.get("/harvests")
    assert b"Unknown" in list_response.content


def test_DeleteHarvest_ExistingId_RemovesFromList(client):
    count_before = client.get("/harvests").content.count(b"<tr")
    client.post("/harvests/1/delete")
    count_after = client.get("/harvests").content.count(b"<tr")
    assert count_after < count_before
