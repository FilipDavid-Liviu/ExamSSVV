from typing import List, Optional, Dict, Any
from datetime import date
from backend.models import Field, Crop, Harvest
from backend.repository import IRepository
from backend.services import IFarmService

class MockRepository(IRepository):
    def __init__(self):
        self.fields = [Field(id=1, name="Mock Field", size_hectares=10.0, soil_type="Sand")]
        self.crops = [Crop(id=1, name="Mock Crop", expected_yield_per_hectare=5.0, season="Summer")]
        self.harvests = []
        self.create_harvest_called = False

    def get_field(self, field_id: int) -> Optional[Field]:
        return next((f for f in self.fields if f.id == field_id), None)
    
    def list_fields(self) -> List[Field]: return self.fields
    def create_field(self, field: Field) -> Field: return field
    def update_field(self, field_id: int, field: Field) -> Optional[Field]: return field
    def delete_field(self, field_id: int) -> bool: return True

    def get_crop(self, crop_id: int) -> Optional[Crop]:
        return next((c for c in self.crops if c.id == crop_id), None)
        
    def list_crops(self) -> List[Crop]: return self.crops
    def create_crop(self, crop: Crop) -> Crop: return crop
    def update_crop(self, crop_id: int, crop: Crop) -> Optional[Crop]: return crop
    def delete_crop(self, crop_id: int) -> bool: return True

    def get_harvest(self, harvest_id: int) -> Optional[Harvest]: return None
    def list_harvests(self) -> List[Harvest]: return self.harvests
    def create_harvest(self, harvest: Harvest) -> Harvest:
        self.create_harvest_called = True
        self.harvests.append(harvest)
        return harvest
    def update_harvest(self, harvest_id: int, harvest: Harvest) -> Optional[Harvest]: return harvest
    def delete_harvest(self, harvest_id: int) -> bool: return True


class MockFarmService(IFarmService):
    def __init__(self):
        self.generate_yield_report_called = False
        self.list_fields_called = False

    def get_field(self, field_id: int) -> Optional[Field]: return None
    def list_fields(self) -> List[Field]:
        self.list_fields_called = True
        return [Field(id=99, name="ServiceMockField", size_hectares=5.0, soil_type="Clay")]
    def create_field(self, name: str, size_hectares: float, soil_type: str) -> Field: 
        return Field(id=1, name=name, size_hectares=size_hectares, soil_type=soil_type)
    def update_field(self, field_id: int, field: Field) -> Optional[Field]: return field
    def delete_field(self, field_id: int) -> bool: return True

    def get_crop(self, crop_id: int) -> Optional[Crop]: return None
    def list_crops(self) -> List[Crop]: return []
    def create_crop(self, name: str, expected_yield_per_hectare: float, season: str) -> Crop:
        return Crop(id=1, name=name, expected_yield_per_hectare=expected_yield_per_hectare, season=season)
    def update_crop(self, crop_id: int, crop: Crop) -> Optional[Crop]: return crop
    def delete_crop(self, crop_id: int) -> bool: return True

    def get_harvest(self, harvest_id: int) -> Optional[Harvest]: return None
    def list_harvests(self) -> List[Harvest]: return []
    def update_harvest(self, harvest_id: int, harvest: Harvest) -> Optional[Harvest]: return harvest
    def delete_harvest(self, harvest_id: int) -> bool: return True
    def register_harvest(self, field_id: int, crop_id: int, harvest_date: date, actual_yield_tons: float, quality_rating: int) -> Harvest:
        return Harvest(id=1, field_id=field_id, crop_id=crop_id, harvest_date=harvest_date, actual_yield_tons=actual_yield_tons, quality_rating=quality_rating)

    def generate_yield_report(self) -> List[Dict[str, Any]]:
        self.generate_yield_report_called = True
        return [{"crop_name": "Mock Crop", "total_yield": 100.0}]
