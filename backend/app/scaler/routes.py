"""Recipe scaling + unit conversion endpoints."""
from fastapi import APIRouter, HTTPException

from app.scaler import service
from app.scaler.schemas import (
    ScaleRecipeRequest,
    ScaleRecipeResponse,
    ConvertUnitRequest,
    ConvertUnitResponse,
)

router = APIRouter(prefix="/api/scaler", tags=["scaler"])


@router.post("/scale-recipe", response_model=ScaleRecipeResponse)
def scale_recipe(payload: ScaleRecipeRequest):
    ingredient_dicts = [ing.model_dump() for ing in payload.ingredients]
    scaled = service.scale_recipe_ingredients(
        ingredient_dicts, payload.original_servings, payload.target_servings
    )
    return ScaleRecipeResponse(ingredients=scaled)


@router.post("/convert-unit", response_model=ConvertUnitResponse)
def convert_unit(payload: ConvertUnitRequest):
    try:
        result = service.convert_unit(payload.quantity, payload.from_unit, payload.to_unit)
    except service.IncompatibleUnitsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ConvertUnitResponse(quantity=result, unit=payload.to_unit)
