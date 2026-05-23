from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import date
from backend.models import Field, Crop, Harvest

class IFarmService(ABC):
    # Field
    @abstractmethod
    def get_field(self, field_id: int) -> Optional[Field]: pass
    
    @abstractmethod
    def list_fields(self) -> List[Field]: pass
    
    @abstractmethod
    def create_field(self, name: str, size_hectares: float, soil_type: str) -> Field: pass
    
    @abstractmethod
    def update_field(self, field_id: int, field: Field) -> Optional[Field]: pass
    
    @abstractmethod
    def delete_field(self, field_id: int) -> bool: pass

    # Crop
    @abstractmethod
    def get_crop(self, crop_id: int) -> Optional[Crop]: pass
    
    @abstractmethod
    def list_crops(self) -> List[Crop]: pass
    
    @abstractmethod
    def create_crop(self, name: str, expected_yield_per_hectare: float, season: str) -> Crop: pass
    
    @abstractmethod
    def update_crop(self, crop_id: int, crop: Crop) -> Optional[Crop]: pass
    
    @abstractmethod
    def delete_crop(self, crop_id: int) -> bool: pass

    # Harvest
    @abstractmethod
    def get_harvest(self, harvest_id: int) -> Optional[Harvest]: pass
    
    @abstractmethod
    def list_harvests(self) -> List[Harvest]: pass
    
    @abstractmethod
    def update_harvest(self, harvest_id: int, harvest: Harvest) -> Optional[Harvest]: pass
    
    @abstractmethod
    def delete_harvest(self, harvest_id: int) -> bool: pass
    
    @abstractmethod
    def register_harvest(self, field_id: int, crop_id: int, harvest_date: date, actual_yield_tons: float, quality_rating: int) -> Harvest: pass

    # Report
    @abstractmethod
    def generate_yield_report(self) -> List[Dict[str, Any]]: pass
