import pytest
from datetime import date
from pydantic import ValidationError

from backend.models import Field, Crop
from backend.repository import InMemoryRepository
from backend.services.farm_service import FarmService

def setup_service() -> FarmService:
    repo = InMemoryRepository()
    field = Field(id=1, name="Test Field", size_hectares=10.0, soil_type="Loam")
    crop = Crop(id=1, name="Test Crop", expected_yield_per_hectare=5.0, season="Spring")
    repo.create_field(field)
    repo.create_crop(crop)
    return FarmService(repo)

# --- Equivalence Class Partitioning (ECP) & Boundary Value Analysis (BVA) ---
# Target 1: `quality_rating` parameter of Harvest (valid range: 1 to 5)
# Classes: <1 (Invalid), 1-5 (Valid), >5 (Invalid), Non-Int (Invalid)
# Boundaries: 0, 1, 5, 6

def test_RegisterHarvest_QualityRatingIs0_ThrowsValidationError():
    # Arrange
    service = setup_service()
    # Act & Assert
    with pytest.raises(ValidationError):
        service.register_harvest(1, 1, date(2023, 10, 1), 20.5, 0)

def test_RegisterHarvest_QualityRatingIs1_ReturnsHarvest():
    service = setup_service()
    harvest = service.register_harvest(1, 1, date(2023, 10, 1), 20.5, 1)
    assert harvest.quality_rating == 1

def test_RegisterHarvest_QualityRatingIs3_ReturnsHarvest():
    service = setup_service()
    harvest = service.register_harvest(1, 1, date(2023, 10, 1), 20.5, 3)
    assert harvest.quality_rating == 3

def test_RegisterHarvest_QualityRatingIs5_ReturnsHarvest():
    service = setup_service()
    harvest = service.register_harvest(1, 1, date(2023, 10, 1), 20.5, 5)
    assert harvest.quality_rating == 5

def test_RegisterHarvest_QualityRatingIs6_ThrowsValidationError():
    service = setup_service()
    with pytest.raises(ValidationError):
        service.register_harvest(1, 1, date(2023, 10, 1), 20.5, 6)

def test_RegisterHarvest_QualityRatingIsString_ThrowsValidationError():
    service = setup_service()
    with pytest.raises(ValidationError):
        service.register_harvest(1, 1, date(2023, 10, 1), 20.5, "excellent")

# Target 2: `actual_yield_tons` parameter
# Classes: Float, Int (valid), String (invalid)
# Boundaries: -0.1, 0.0, 0.1

def test_RegisterHarvest_ActualYieldTonsIsFloat_ReturnsHarvest():
    service = setup_service()
    harvest = service.register_harvest(1, 1, date(2023, 10, 1), 20.5, 3)
    assert harvest.actual_yield_tons == 20.5

def test_RegisterHarvest_ActualYieldTonsIsInt_ReturnsHarvest():
    service = setup_service()
    harvest = service.register_harvest(1, 1, date(2023, 10, 1), 20, 3)
    assert harvest.actual_yield_tons == 20.0

def test_RegisterHarvest_ActualYieldTonsIsString_ThrowsValidationError():
    service = setup_service()
    with pytest.raises(ValidationError):
        service.register_harvest(1, 1, date(2023, 10, 1), "twenty", 3)

def test_RegisterHarvest_ActualYieldTonsIsNegative_ThrowsValidationError():
    service = setup_service()
    with pytest.raises(ValidationError):
        service.register_harvest(1, 1, date(2023, 10, 1), -0.1, 3)

def test_RegisterHarvest_ActualYieldTonsIsZero_ReturnsHarvest():
    service = setup_service()
    harvest = service.register_harvest(1, 1, date(2023, 10, 1), 0.0, 3)
    assert harvest.actual_yield_tons == 0.0

def test_RegisterHarvest_ActualYieldTonsIsJustAboveZero_ReturnsHarvest():
    service = setup_service()
    harvest = service.register_harvest(1, 1, date(2023, 10, 1), 0.1, 3)
    assert harvest.actual_yield_tons == 0.1

