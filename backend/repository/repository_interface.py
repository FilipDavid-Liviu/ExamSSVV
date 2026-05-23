from abc import ABC, abstractmethod
from typing import List, Optional
from backend.models import Field, Crop, Harvest

class IRepository(ABC):
    # Field
    @abstractmethod
    def get_field(self, field_id: int) -> Optional[Field]: pass
    
    @abstractmethod
    def list_fields(self) -> List[Field]: pass
    
    @abstractmethod
    def create_field(self, field: Field) -> Field: pass
    
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
    def create_crop(self, crop: Crop) -> Crop: pass
    
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
    def create_harvest(self, harvest: Harvest) -> Harvest: pass
    
    @abstractmethod
    def update_harvest(self, harvest_id: int, harvest: Harvest) -> Optional[Harvest]: pass
    
    @abstractmethod
    def delete_harvest(self, harvest_id: int) -> bool: pass
