from pydantic import BaseModel, Field as PydanticField
from datetime import date

class Field(BaseModel):
    id: int
    name: str
    size_hectares: float
    soil_type: str

class Crop(BaseModel):
    id: int
    name: str
    expected_yield_per_hectare: float
    season: str

class Harvest(BaseModel):
    id: int
    field_id: int
    crop_id: int
    harvest_date: date
    actual_yield_tons: float = PydanticField(ge=0.0)
    quality_rating: int = PydanticField(ge=1, le=5)
