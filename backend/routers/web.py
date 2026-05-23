from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import date
from backend.services import IFarmService

router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")

def get_farm_service(request: Request) -> IFarmService:
    return request.app.state.farm_service

@router.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request, service: IFarmService = Depends(get_farm_service)):
    report = service.generate_yield_report()
    return templates.TemplateResponse(request=request, name="dashboard.html", context={"report": report})

# --- FIELDS ---
@router.get("/fields", response_class=HTMLResponse)
async def list_fields(request: Request, service: IFarmService = Depends(get_farm_service)):
    fields = service.list_fields()
    return templates.TemplateResponse(request=request, name="fields.html", context={"fields": fields})

@router.get("/fields/new", response_class=HTMLResponse)
async def new_field_form(request: Request):
    return templates.TemplateResponse(request=request, name="field_form.html", context={"field": None})

@router.post("/fields")
async def create_field(
    request: Request,
    name: str = Form(...),
    size_hectares: float = Form(...),
    soil_type: str = Form(...),
    service: IFarmService = Depends(get_farm_service)
):
    service.create_field(name, size_hectares, soil_type)
    return RedirectResponse(url="/fields", status_code=303)

@router.get("/fields/{id}/edit", response_class=HTMLResponse)
async def edit_field_form(request: Request, id: int, service: IFarmService = Depends(get_farm_service)):
    field = service.get_field(id)
    return templates.TemplateResponse(request=request, name="field_form.html", context={"field": field})

@router.post("/fields/{id}/update")
async def update_field(
    request: Request,
    id: int,
    name: str = Form(...),
    size_hectares: float = Form(...),
    soil_type: str = Form(...),
    service: IFarmService = Depends(get_farm_service)
):
    from backend.models import Field
    field = Field(id=id, name=name, size_hectares=size_hectares, soil_type=soil_type)
    service.update_field(id, field)
    return RedirectResponse(url="/fields", status_code=303)

@router.post("/fields/{id}/delete")
async def delete_field(request: Request, id: int, service: IFarmService = Depends(get_farm_service)):
    service.delete_field(id)
    return RedirectResponse(url="/fields", status_code=303)


# --- CROPS ---
@router.get("/crops", response_class=HTMLResponse)
async def list_crops(request: Request, service: IFarmService = Depends(get_farm_service)):
    crops = service.list_crops()
    return templates.TemplateResponse(request=request, name="crops.html", context={"crops": crops})

@router.get("/crops/new", response_class=HTMLResponse)
async def new_crop_form(request: Request):
    return templates.TemplateResponse(request=request, name="crop_form.html", context={"crop": None})

@router.post("/crops")
async def create_crop(
    request: Request,
    name: str = Form(...),
    expected_yield_per_hectare: float = Form(...),
    season: str = Form(...),
    service: IFarmService = Depends(get_farm_service)
):
    service.create_crop(name, expected_yield_per_hectare, season)
    return RedirectResponse(url="/crops", status_code=303)

@router.get("/crops/{id}/edit", response_class=HTMLResponse)
async def edit_crop_form(request: Request, id: int, service: IFarmService = Depends(get_farm_service)):
    crop = service.get_crop(id)
    return templates.TemplateResponse(request=request, name="crop_form.html", context={"crop": crop})

@router.post("/crops/{id}/update")
async def update_crop(
    request: Request,
    id: int,
    name: str = Form(...),
    expected_yield_per_hectare: float = Form(...),
    season: str = Form(...),
    service: IFarmService = Depends(get_farm_service)
):
    from backend.models import Crop
    crop = Crop(id=id, name=name, expected_yield_per_hectare=expected_yield_per_hectare, season=season)
    service.update_crop(id, crop)
    return RedirectResponse(url="/crops", status_code=303)

@router.post("/crops/{id}/delete")
async def delete_crop(request: Request, id: int, service: IFarmService = Depends(get_farm_service)):
    service.delete_crop(id)
    return RedirectResponse(url="/crops", status_code=303)


# --- HARVESTS ---
@router.get("/harvests", response_class=HTMLResponse)
async def list_harvests(request: Request, service: IFarmService = Depends(get_farm_service)):
    harvests = service.list_harvests()
    
    # Join with fields and crops
    harvest_data = []
    for h in harvests:
        field = service.get_field(h.field_id)
        crop = service.get_crop(h.crop_id)
        harvest_data.append({
            "id": h.id,
            "field_name": field.name if field else "Unknown",
            "crop_name": crop.name if crop else "Unknown",
            "harvest_date": h.harvest_date,
            "actual_yield_tons": h.actual_yield_tons,
            "quality_rating": h.quality_rating,
            "field_id": h.field_id,
            "crop_id": h.crop_id
        })
        
    return templates.TemplateResponse(request=request, name="harvests.html", context={"harvests": harvest_data})

@router.get("/harvests/new", response_class=HTMLResponse)
async def new_harvest_form(request: Request, service: IFarmService = Depends(get_farm_service)):
    fields = service.list_fields()
    crops = service.list_crops()
    return templates.TemplateResponse(request=request, name="new_harvest.html", context={"fields": fields, "crops": crops})

@router.post("/harvests")
async def create_harvest(
    request: Request,
    field_id: int = Form(...),
    crop_id: int = Form(...),
    harvest_date: date = Form(...),
    actual_yield_tons: float = Form(...),
    quality_rating: int = Form(...),
    service: IFarmService = Depends(get_farm_service)
):
    try:
        service.register_harvest(
            field_id=field_id,
            crop_id=crop_id,
            harvest_date=harvest_date,
            actual_yield_tons=actual_yield_tons,
            quality_rating=quality_rating
        )
    except ValueError as e:
        pass
    
    return RedirectResponse(url="/harvests", status_code=303)

@router.get("/harvests/{id}/edit", response_class=HTMLResponse)
async def edit_harvest_form(request: Request, id: int, service: IFarmService = Depends(get_farm_service)):
    harvest = service.get_harvest(id)
    fields = service.list_fields()
    crops = service.list_crops()
    return templates.TemplateResponse(request=request, name="edit_harvest.html", context={"harvest": harvest, "fields": fields, "crops": crops})

@router.post("/harvests/{id}/update")
async def update_harvest(
    request: Request,
    id: int,
    field_id: int = Form(...),
    crop_id: int = Form(...),
    harvest_date: date = Form(...),
    actual_yield_tons: float = Form(...),
    quality_rating: int = Form(...),
    service: IFarmService = Depends(get_farm_service)
):
    from backend.models import Harvest
    harvest = Harvest(
        id=id, field_id=field_id, crop_id=crop_id, 
        harvest_date=harvest_date, actual_yield_tons=actual_yield_tons, quality_rating=quality_rating
    )
    service.update_harvest(id, harvest)
    return RedirectResponse(url="/harvests", status_code=303)

@router.post("/harvests/{id}/delete")
async def delete_harvest(request: Request, id: int, service: IFarmService = Depends(get_farm_service)):
    service.delete_harvest(id)
    return RedirectResponse(url="/harvests", status_code=303)
