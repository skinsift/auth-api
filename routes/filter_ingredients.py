from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Ingredient

# Router Initialization
router = APIRouter()

# API Route
@router.get("/filter-ingredients")
def get_filtered_ingredients(
    db: Session = Depends(get_db),
):
    # Fetch distinct values for each column
    ratings = db.query(Ingredient.rating).distinct().all()
    raw_benefits = db.query(Ingredient.benefitidn).distinct().all()
    raw_categories = db.query(Ingredient.kategoriidn).distinct().all()

    # Process multivalued fields for benefits and categories
    benefits = set()
    for benefit in raw_benefits:
        if benefit[0]:  # Check if value is not None
            benefits.update(map(str.strip, benefit[0].split(",")))

    categories = set()
    for category in raw_categories:
        if category[0]:  # Check if value is not None
            categories.update(map(str.strip, category[0].split(",")))

    # Format the results into the desired response structure
    response = [
        {"rating": [r[0] for r in ratings if r[0]]},  # Ensure no None values
        {"benefitidn": list(benefits)},
        {"kategoriidn": list(categories)},
    ]

    return response
