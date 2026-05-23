from fastapi.testclient import TestClient
from backend.main import app
from backend.routers.web import get_farm_service
from backend.services.farm_service import FarmService
from backend.repository.memory import InMemoryRepository
from tests.mocks import MockFarmService, MockRepository

client = TestClient(app)


def test_Integration_TopDown_Router_With_MockService():
    """
    Step 1: Test Router Layer, Mock Service Layer
    We override the FastAPI dependency to return our MockFarmService.
    """
    mock_service = MockFarmService()
    app.dependency_overrides[get_farm_service] = lambda: mock_service
    
    # Act
    response = client.get("/fields")
    report_response = client.get("/")
    
    # Assert
    assert response.status_code == 200
    assert mock_service.list_fields_called == True
    assert b"ServiceMockField" in response.content

    assert report_response.status_code == 200
    assert mock_service.generate_yield_report_called == True
    assert b"Mock Crop" in report_response.content
    
    # Clean up overrides
    app.dependency_overrides.clear()


def test_Integration_TopDown_Router_With_RealService_And_MockRepository():
    """
    Step 2: Test Router Layer + Real Service Layer, Mock Repository Layer
    """
    mock_repo = MockRepository()
    real_service = FarmService(mock_repo)
    app.dependency_overrides[get_farm_service] = lambda: real_service
    
    # Act
    response = client.get("/fields")
    crops_response = client.get("/crops")
    
    # Assert
    assert response.status_code == 200
    assert crops_response.status_code == 200
    # "Mock Field" comes from MockRepository.fields
    assert b"Mock Field" in response.content
    assert b"Mock Crop" in crops_response.content
    
    # Clean up overrides
    app.dependency_overrides.clear()


def test_Integration_TopDown_Router_With_RealService_And_RealRepository():
    """
    Step 3: Test Full Stack (Router -> Real Service -> Real Repository)
    """
    real_repo = InMemoryRepository()
    real_service = FarmService(real_repo)
    app.dependency_overrides[get_farm_service] = lambda: real_service
    
    # Arrange: Add data through the entire stack via API
    create_response = client.post("/fields", data={
        "name": "Full Stack Field",
        "size_hectares": 12.5,
        "soil_type": "Peat"
    })
    assert create_response.status_code == 200 or create_response.status_code == 303 # Redirects to /fields
    
    # Act: Retrieve the data
    list_response = client.get("/fields")
    
    # Assert
    assert list_response.status_code == 200
    assert b"Full Stack Field" in list_response.content
    
    # Clean up overrides
    app.dependency_overrides.clear()


def test_Integration_TopDown_FullStack_ReportGeneration():
    """
    Step 3 (Extended): Test Full Stack Report Generation Logic
    """
    real_repo = InMemoryRepository()
    real_service = FarmService(real_repo)
    app.dependency_overrides[get_farm_service] = lambda: real_service
    
    # Arrange: Setup Entities
    client.post("/fields", data={"name": "Report Field", "size_hectares": 10.0, "soil_type": "Loam"})
    client.post("/crops", data={"name": "Report Crop", "expected_yield_per_hectare": 5.0, "season": "Spring"})
    client.post("/harvests", data={
        "field_id": 1,
        "crop_id": 1,
        "harvest_date": "2023-10-01",
        "actual_yield_tons": 50.0,
        "quality_rating": 4
    })
    
    # Act: Request Dashboard
    dashboard_response = client.get("/")
    
    # Assert
    assert dashboard_response.status_code == 200
    assert b"Report Crop" in dashboard_response.content
    # The total yield should be aggregated and displayed
    assert b"50.0" in dashboard_response.content
    
    app.dependency_overrides.clear()
