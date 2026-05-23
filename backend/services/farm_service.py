from typing import List, Dict, Any, Optional
from datetime import date
from backend.models import Field, Crop, Harvest
from backend.repository import InMemoryRepository

class FarmService:
    def __init__(self, repo: InMemoryRepository):
        self.repo = repo

    # Field CRUD
    def get_field(self, field_id: int) -> Optional[Field]:
        return self.repo.get_field(field_id)

    def list_fields(self) -> List[Field]:
        return self.repo.list_fields()

    def create_field(self, name: str, size_hectares: float, soil_type: str) -> Field:
        existing = self.repo.list_fields()
        new_id = max((f.id for f in existing), default=0) + 1
        field = Field(id=new_id, name=name, size_hectares=size_hectares, soil_type=soil_type)
        return self.repo.create_field(field)

    def update_field(self, field_id: int, field: Field) -> Optional[Field]:
        return self.repo.update_field(field_id, field)

    def delete_field(self, field_id: int) -> bool:
        # Cascade delete associated harvests
        harvests_to_delete = [h for h in self.list_harvests() if h.field_id == field_id]
        for h in harvests_to_delete:
            self.delete_harvest(h.id)
        
        return self.repo.delete_field(field_id)

    # Crop CRUD
    def get_crop(self, crop_id: int) -> Optional[Crop]:
        return self.repo.get_crop(crop_id)

    def list_crops(self) -> List[Crop]:
        return self.repo.list_crops()

    def create_crop(self, name: str, expected_yield_per_hectare: float, season: str) -> Crop:
        existing = self.repo.list_crops()
        new_id = max((c.id for c in existing), default=0) + 1
        crop = Crop(id=new_id, name=name, expected_yield_per_hectare=expected_yield_per_hectare, season=season)
        return self.repo.create_crop(crop)

    def update_crop(self, crop_id: int, crop: Crop) -> Optional[Crop]:
        return self.repo.update_crop(crop_id, crop)

    def delete_crop(self, crop_id: int) -> bool:
        # Cascade delete associated harvests
        harvests_to_delete = [h for h in self.list_harvests() if h.crop_id == crop_id]
        for h in harvests_to_delete:
            self.delete_harvest(h.id)
            
        return self.repo.delete_crop(crop_id)

    # Harvest CRUD (Basic)
    def get_harvest(self, harvest_id: int) -> Optional[Harvest]:
        return self.repo.get_harvest(harvest_id)

    def list_harvests(self) -> List[Harvest]:
        return self.repo.list_harvests()

    def update_harvest(self, harvest_id: int, harvest: Harvest) -> Optional[Harvest]:
        return self.repo.update_harvest(harvest_id, harvest)

    def delete_harvest(self, harvest_id: int) -> bool:
        return self.repo.delete_harvest(harvest_id)

    # Core Functionality
    def register_harvest(self, field_id: int, crop_id: int, harvest_date: date, actual_yield_tons: float, quality_rating: int) -> Harvest:
        if not self.repo.get_field(field_id):
            raise ValueError(f"Field with ID {field_id} does not exist.")
        if not self.repo.get_crop(crop_id):
            raise ValueError(f"Crop with ID {crop_id} does not exist.")
        
        existing = self.repo.list_harvests()
        new_id = max((h.id for h in existing), default=0) + 1
        
        harvest = Harvest(
            id=new_id,
            field_id=field_id,
            crop_id=crop_id,
            harvest_date=harvest_date,
            actual_yield_tons=actual_yield_tons,
            quality_rating=quality_rating
        )
        return self.repo.create_harvest(harvest)

    # Report Functionality
    def generate_yield_report(self) -> List[Dict[str, Any]]:
        crops = self.repo.list_crops()
        harvests = self.repo.list_harvests()

        # Initialize dictionary to keep track of yields per crop
        report_data = {crop.id: {"crop_name": crop.name, "total_yield": 0.0} for crop in crops}

        for harvest in harvests:
            if harvest.crop_id in report_data:
                report_data[harvest.crop_id]["total_yield"] += harvest.actual_yield_tons

        return list(report_data.values())
