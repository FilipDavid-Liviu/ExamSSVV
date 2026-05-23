from backend.models import Field, Crop, Harvest
from backend.repository import InMemoryRepository
from datetime import date

def test_Repository_Field_CRUD():
    repo = InMemoryRepository()
    
    # Empty List
    assert repo.list_fields() == []
    
    # Create
    field = Field(id=1, name="F1", size_hectares=10.0, soil_type="A")
    assert repo.create_field(field) == field
    assert len(repo.list_fields()) == 1
    
    # Get
    assert repo.get_field(1) == field
    assert repo.get_field(99) is None
    
    # Update
    updated_field = Field(id=1, name="F1 Updated", size_hectares=10.0, soil_type="A")
    assert repo.update_field(1, updated_field) == updated_field
    assert repo.get_field(1).name == "F1 Updated"
    assert repo.update_field(99, updated_field) is None
    
    # Delete
    assert repo.delete_field(1) is True
    assert repo.delete_field(99) is False
    assert len(repo.list_fields()) == 0


def test_Repository_Crop_CRUD():
    repo = InMemoryRepository()
    
    # Empty List
    assert repo.list_crops() == []
    
    # Create
    crop = Crop(id=1, name="C1", expected_yield_per_hectare=5.0, season="Spring")
    assert repo.create_crop(crop) == crop
    assert len(repo.list_crops()) == 1
    
    # Get
    assert repo.get_crop(1) == crop
    assert repo.get_crop(99) is None
    
    # Update
    updated_crop = Crop(id=1, name="C1 Updated", expected_yield_per_hectare=5.0, season="Spring")
    assert repo.update_crop(1, updated_crop) == updated_crop
    assert repo.get_crop(1).name == "C1 Updated"
    assert repo.update_crop(99, updated_crop) is None
    
    # Delete
    assert repo.delete_crop(1) is True
    assert repo.delete_crop(99) is False
    assert len(repo.list_crops()) == 0


def test_Repository_Harvest_CRUD():
    repo = InMemoryRepository()
    
    # Empty List
    assert repo.list_harvests() == []
    
    # Create
    harvest = Harvest(id=1, field_id=1, crop_id=1, harvest_date=date(2023, 1, 1), actual_yield_tons=10.0, quality_rating=3)
    assert repo.create_harvest(harvest) == harvest
    assert len(repo.list_harvests()) == 1
    
    # Get
    assert repo.get_harvest(1) == harvest
    assert repo.get_harvest(99) is None
    
    # Update
    updated_harvest = Harvest(id=1, field_id=1, crop_id=1, harvest_date=date(2023, 1, 1), actual_yield_tons=20.0, quality_rating=3)
    assert repo.update_harvest(1, updated_harvest) == updated_harvest
    assert repo.get_harvest(1).actual_yield_tons == 20.0
    assert repo.update_harvest(99, updated_harvest) is None
    
    # Delete
    assert repo.delete_harvest(1) is True
    assert repo.delete_harvest(99) is False
    assert len(repo.list_harvests()) == 0
