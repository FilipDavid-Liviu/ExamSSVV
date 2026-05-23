from fastapi.testclient import TestClient
from datetime import date
from backend.main import app
from backend.routers.web import get_farm_service
from backend.services.farm_service import FarmService
from backend.repository.memory import InMemoryRepository
from tests.mocks import MockRepository

client = TestClient(app)

# --- Bottom-Up Integration Testing ---

def test_Integration_BottomUp_Service_With_MockRepository():
    """
    Step 1: Test Service Layer (Driver) + Mock Repository (Stub)
    We instantiate the real FarmService but inject a MockRepository.
    """
    mock_repo = MockRepository()
    real_service = FarmService(mock_repo)
    
    # Act
    harvest = real_service.register_harvest(
        field_id=1, 
        crop_id=1, 
        harvest_date=date(2023, 10, 1), 
        actual_yield_tons=15.0, 
        quality_rating=4
    )
    
    # Assert
    assert harvest.id == 1
    assert mock_repo.create_harvest_called == True


def test_Integration_BottomUp_Service_With_RealRepository():
    """
    Step 2: Test Service Layer (Driver) + Real Repository
    We integrate the real InMemoryRepository into the real FarmService.
    """
    real_repo = InMemoryRepository()
    real_service = FarmService(real_repo)
    
    # Arrange (Need to seed data because it's a real empty repo)
    real_service.create_field("Real Repo Field", 10.0, "Loam")
    real_service.create_crop("Real Repo Crop", 5.0, "Spring")
    
    # Act
    harvest = real_service.register_harvest(
        field_id=1, 
        crop_id=1, 
        harvest_date=date(2023, 10, 1), 
        actual_yield_tons=20.0, 
        quality_rating=5
    )
    
    # Assert
    assert harvest.id == 1
    assert len(real_repo.list_harvests()) == 1


def test_Integration_BottomUp_Router_With_Service_And_RealRepository():
    """
    Step 3: Test Full Stack (Router -> Real Service -> Real Repository)
    Finally, we plug our integrated Service/Repository into the Router layer.
    """
    real_repo = InMemoryRepository()
    real_service = FarmService(real_repo)
    
    # Pre-seed some data via the service to be consumed by the router
    real_service.create_field("Bottom Up Field", 15.0, "Clay")
    app.dependency_overrides[get_farm_service] = lambda: real_service
    
    # Act (Hit the router)
    response = client.get("/fields")
    
    # Assert
    assert response.status_code == 200
    assert b"Bottom Up Field" in response.content
    
    # Clean up overrides
    app.dependency_overrides.clear()


def test_Integration_BottomUp_FullStack_CascadeDeletion():
    """
    Step 3 (Extended): Test Full Stack Cascade Deletion Logic
    Router Delete Command -> Service deletes Field -> Service iterates and deletes Harvests -> Repo clears them all.
    """
    real_repo = InMemoryRepository()
    real_service = FarmService(real_repo)
    app.dependency_overrides[get_farm_service] = lambda: real_service
    
    # Arrange
    client.post("/fields", data={"name": "Cascade Field", "size_hectares": 10.0, "soil_type": "Loam"})
    client.post("/crops", data={"name": "Cascade Crop", "expected_yield_per_hectare": 5.0, "season": "Spring"})
    client.post("/harvests", data={
        "field_id": 1,
        "crop_id": 1,
        "harvest_date": "2023-10-01",
        "actual_yield_tons": 50.0,
        "quality_rating": 4
    })
    
    # Verify harvest exists
    harvests_before = client.get("/harvests")
    assert b"Cascade Field" in harvests_before.content
    
    # Act: Delete the field via API
    delete_response = client.post("/fields/1/delete", follow_redirects=False)
    assert delete_response.status_code == 303
    
    # Assert: Harvest should be cascaded away
    harvests_after = client.get("/harvests")
    assert b"Cascade Field" not in harvests_after.content
    
    app.dependency_overrides.clear()
