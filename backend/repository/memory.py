from typing import List, Optional
from backend.models import Field, Crop, Harvest
from backend.repository.repository_interface import IRepository

class InMemoryRepository(IRepository):
    def __init__(self):
        self.fields: dict[int, Field] = {}
        self.crops: dict[int, Crop] = {}
        self.harvests: dict[int, Harvest] = {}

    # Field CRUD
    def get_field(self, field_id: int) -> Optional[Field]:
        return self.fields.get(field_id)

    def list_fields(self) -> List[Field]:
        return list(self.fields.values())

    def create_field(self, field: Field) -> Field:
        self.fields[field.id] = field
        return field

    def update_field(self, field_id: int, field: Field) -> Optional[Field]:
        if field_id in self.fields:
            self.fields[field_id] = field
            return field
        return None

    def delete_field(self, field_id: int) -> bool:
        if field_id in self.fields:
            del self.fields[field_id]
            return True
        return False

    # Crop CRUD
    def get_crop(self, crop_id: int) -> Optional[Crop]:
        return self.crops.get(crop_id)

    def list_crops(self) -> List[Crop]:
        return list(self.crops.values())

    def create_crop(self, crop: Crop) -> Crop:
        self.crops[crop.id] = crop
        return crop

    def update_crop(self, crop_id: int, crop: Crop) -> Optional[Crop]:
        if crop_id in self.crops:
            self.crops[crop_id] = crop
            return crop
        return None

    def delete_crop(self, crop_id: int) -> bool:
        if crop_id in self.crops:
            del self.crops[crop_id]
            return True
        return False

    # Harvest CRUD
    def get_harvest(self, harvest_id: int) -> Optional[Harvest]:
        return self.harvests.get(harvest_id)

    def list_harvests(self) -> List[Harvest]:
        return list(self.harvests.values())

    def create_harvest(self, harvest: Harvest) -> Harvest:
        self.harvests[harvest.id] = harvest
        return harvest

    def update_harvest(self, harvest_id: int, harvest: Harvest) -> Optional[Harvest]:
        if harvest_id in self.harvests:
            self.harvests[harvest_id] = harvest
            return harvest
        return None

    def delete_harvest(self, harvest_id: int) -> bool:
        if harvest_id in self.harvests:
            del self.harvests[harvest_id]
            return True
        return False
