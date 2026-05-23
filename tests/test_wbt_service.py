import pytest
from datetime import date

from backend.models import Field, Crop, Harvest
from backend.repository import InMemoryRepository
from backend.services.farm_service import FarmService

def setup_service() -> FarmService:
    repo = InMemoryRepository()
    return FarmService(repo)

# --- White Box Testing (WBT) ---

# register_harvest logic
def test_RegisterHarvest_FieldDoesNotExist_ThrowsValueError():
    service = setup_service()
    with pytest.raises(ValueError) as excinfo:
        service.register_harvest(field_id=99, crop_id=1, harvest_date=date(2023, 10, 1), actual_yield_tons=20.5, quality_rating=3)
    assert "Field with ID 99 does not exist." in str(excinfo.value)

def test_RegisterHarvest_CropDoesNotExist_ThrowsValueError():
    service = setup_service()
    field = Field(id=1, name="Test Field", size_hectares=10.0, soil_type="Loam")
    service.repo.create_field(field)
    with pytest.raises(ValueError) as excinfo:
        service.register_harvest(field_id=1, crop_id=99, harvest_date=date(2023, 10, 1), actual_yield_tons=20.5, quality_rating=3)
    assert "Crop with ID 99 does not exist." in str(excinfo.value)

def test_RegisterHarvest_ValidEntities_CreatesAndReturnsHarvest():
    service = setup_service()
    field = Field(id=1, name="Test Field", size_hectares=10.0, soil_type="Loam")
    crop = Crop(id=1, name="Test Crop", expected_yield_per_hectare=5.0, season="Spring")
    service.repo.create_field(field)
    service.repo.create_crop(crop)
    harvest = service.register_harvest(field_id=1, crop_id=1, harvest_date=date(2023, 10, 1), actual_yield_tons=20.5, quality_rating=3)
    assert harvest is not None
    assert harvest.id == 1
    assert len(service.repo.list_harvests()) == 1


# Field CRUD
def test_FieldCRUD_Service():
    service = setup_service()
    
    # Create Field
    f1 = service.create_field("F1", 10.0, "A")
    assert f1.id == 1
    
    # Create Field with existing ID
    f2 = service.create_field("F2", 20.0, "B")
    assert f2.id == 2
    
    # List and Get
    assert len(service.list_fields()) == 2
    assert service.get_field(1).name == "F1"
    
    # Update
    updated = Field(id=1, name="F1 Updated", size_hectares=10.0, soil_type="A")
    service.update_field(1, updated)
    assert service.get_field(1).name == "F1 Updated"
    
    # Delete (without cascades first)
    assert service.delete_field(2) is True
    assert service.get_field(2) is None


def test_DeleteField_CascadesHarvests():
    service = setup_service()
    service.create_field("F1", 10.0, "A")
    service.repo.create_crop(Crop(id=1, name="C1", expected_yield_per_hectare=5.0, season="S"))
    service.register_harvest(1, 1, date.today(), 10.0, 3)
    
    # Assure harvest exists
    assert len(service.list_harvests()) == 1
    
    # Delete Field
    service.delete_field(1)
    
    # Harvest should be gone
    assert len(service.list_harvests()) == 0


# Crop CRUD
def test_CropCRUD_Service():
    service = setup_service()
    
    # Create
    c1 = service.create_crop("C1", 10.0, "A")
    assert c1.id == 1
    c2 = service.create_crop("C2", 20.0, "B")
    assert c2.id == 2
    
    # List and Get
    assert len(service.list_crops()) == 2
    assert service.get_crop(1).name == "C1"
    
    # Update
    updated = Crop(id=1, name="C1 Updated", expected_yield_per_hectare=10.0, season="A")
    service.update_crop(1, updated)
    assert service.get_crop(1).name == "C1 Updated"
    
    # Delete
    assert service.delete_crop(2) is True
    assert service.get_crop(2) is None


def test_DeleteCrop_CascadesHarvests():
    service = setup_service()
    service.repo.create_field(Field(id=1, name="F1", size_hectares=10.0, soil_type="A"))
    service.create_crop("C1", 10.0, "A")
    service.register_harvest(1, 1, date.today(), 10.0, 3)
    
    # Delete Crop
    service.delete_crop(1)
    
    # Harvest should be gone
    assert len(service.list_harvests()) == 0


# Harvest CRUD (Basic)
def test_HarvestCRUD_Service():
    service = setup_service()
    service.repo.create_field(Field(id=1, name="F1", size_hectares=10.0, soil_type="A"))
    service.repo.create_crop(Crop(id=1, name="C1", expected_yield_per_hectare=5.0, season="S"))
    
    h1 = service.register_harvest(1, 1, date.today(), 10.0, 3)
    
    assert service.get_harvest(h1.id) == h1
    assert len(service.list_harvests()) == 1
    
    updated = Harvest(id=1, field_id=1, crop_id=1, harvest_date=date.today(), actual_yield_tons=99.0, quality_rating=5)
    service.update_harvest(1, updated)
    assert service.get_harvest(1).actual_yield_tons == 99.0
    
    service.delete_harvest(1)
    assert len(service.list_harvests()) == 0


# Generate Yield Report
def test_GenerateYieldReport():
    service = setup_service()
    
    # No crops
    assert service.generate_yield_report() == []
    
    # Crops but no harvests
    service.repo.create_crop(Crop(id=1, name="Corn", expected_yield_per_hectare=5.0, season="S"))
    service.repo.create_crop(Crop(id=2, name="Wheat", expected_yield_per_hectare=5.0, season="S"))
    
    report = service.generate_yield_report()
    assert len(report) == 2
    assert report[0]["total_yield"] == 0.0
    assert report[1]["total_yield"] == 0.0
    
    # Harvests present
    service.repo.create_field(Field(id=1, name="F1", size_hectares=10.0, soil_type="A"))
    service.register_harvest(1, 1, date.today(), 10.0, 3)
    service.register_harvest(1, 1, date.today(), 15.0, 3)
    service.register_harvest(1, 2, date.today(), 20.0, 3)
    
    report = service.generate_yield_report()
    assert report[0]["total_yield"] == 25.0
    assert report[1]["total_yield"] == 20.0
