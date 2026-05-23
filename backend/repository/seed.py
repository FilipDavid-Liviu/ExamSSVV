from datetime import date
from backend.models import Field, Crop, Harvest
from backend.repository import InMemoryRepository

def seed_data(repo: InMemoryRepository):
    # 4 Crops
    crops = [
        Crop(id=1, name="Wheat", expected_yield_per_hectare=3.5, season="Winter"),
        Crop(id=2, name="Corn", expected_yield_per_hectare=8.0, season="Summer"),
        Crop(id=3, name="Soybeans", expected_yield_per_hectare=2.8, season="Summer"),
        Crop(id=4, name="Alfalfa", expected_yield_per_hectare=12.0, season="Spring"),
    ]
    for crop in crops:
        repo.create_crop(crop)

    # 5 Fields
    fields = [
        Field(id=1, name="North Plot", size_hectares=10.5, soil_type="Clay Loam"),
        Field(id=2, name="South Plot", size_hectares=15.0, soil_type="Sandy Loam"),
        Field(id=3, name="East Meadow", size_hectares=8.2, soil_type="Silt"),
        Field(id=4, name="West Acre", size_hectares=20.0, soil_type="Peaty"),
        Field(id=5, name="Central Basin", size_hectares=12.5, soil_type="Chalky"),
    ]
    for field in fields:
        repo.create_field(field)

    # 15 Harvests
    harvests = [
        Harvest(id=1, field_id=1, crop_id=1, harvest_date=date(2021, 7, 15), actual_yield_tons=35.0, quality_rating=4),
        Harvest(id=2, field_id=2, crop_id=2, harvest_date=date(2021, 10, 5), actual_yield_tons=110.0, quality_rating=5),
        Harvest(id=3, field_id=3, crop_id=3, harvest_date=date(2021, 9, 20), actual_yield_tons=22.0, quality_rating=3),
        Harvest(id=4, field_id=4, crop_id=4, harvest_date=date(2021, 6, 10), actual_yield_tons=230.0, quality_rating=4),
        Harvest(id=5, field_id=5, crop_id=1, harvest_date=date(2021, 7, 20), actual_yield_tons=40.0, quality_rating=5),

        Harvest(id=6, field_id=1, crop_id=3, harvest_date=date(2022, 9, 25), actual_yield_tons=28.5, quality_rating=4),
        Harvest(id=7, field_id=2, crop_id=1, harvest_date=date(2022, 7, 10), actual_yield_tons=50.0, quality_rating=3),
        Harvest(id=8, field_id=3, crop_id=4, harvest_date=date(2022, 6, 15), actual_yield_tons=95.0, quality_rating=5),
        Harvest(id=9, field_id=4, crop_id=2, harvest_date=date(2022, 10, 12), actual_yield_tons=155.0, quality_rating=4),
        Harvest(id=10, field_id=5, crop_id=3, harvest_date=date(2022, 9, 22), actual_yield_tons=32.0, quality_rating=4),

        Harvest(id=11, field_id=1, crop_id=2, harvest_date=date(2023, 10, 8), actual_yield_tons=82.0, quality_rating=4),
        Harvest(id=12, field_id=2, crop_id=3, harvest_date=date(2023, 9, 30), actual_yield_tons=40.5, quality_rating=5),
        Harvest(id=13, field_id=3, crop_id=1, harvest_date=date(2023, 7, 18), actual_yield_tons=27.0, quality_rating=3),
        Harvest(id=14, field_id=4, crop_id=4, harvest_date=date(2023, 6, 20), actual_yield_tons=245.0, quality_rating=5),
        Harvest(id=15, field_id=5, crop_id=2, harvest_date=date(2023, 10, 15), actual_yield_tons=95.0, quality_rating=4),
    ]
    for harvest in harvests:
        repo.create_harvest(harvest)
