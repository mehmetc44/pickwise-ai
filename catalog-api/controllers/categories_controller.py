from fastapi import APIRouter, HTTPException
from typing import List
from services.category_service import CategoryService
from models.schemas import CategoryResponse, VectorSearchRequest, ClosestCategoryRequest, CategorySearchRequest

router = APIRouter(prefix="/categories", tags=["Categories"])
service = CategoryService()

@router.get("/closest", response_model=List[CategoryResponse])
def get_closest_categories_by_query(query: str, limit: int = 10):
    try:
        return service.get_closest_categories(query, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/closest", response_model=List[CategoryResponse])
def get_closest_categories(request: ClosestCategoryRequest):
    try:
        if request.query is not None:
            return service.get_closest_categories(request.query, request.limit)
        elif request.vector is not None:
            return service.get_closest_categories(request.vector, request.limit)
        else:
            raise HTTPException(status_code=400, detail="Either 'query' or 'vector' must be provided.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search-by-vector", response_model=List[CategoryResponse])
def search_categories_by_vector(request: VectorSearchRequest):
    try:
        return service.get_closest_categories(request.vector, request.limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[CategoryResponse])
def get_categories(limit: int = 100):
    try:
        return service.get_categories(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/main", response_model=List[CategoryResponse])
def get_main_categories(limit: int = 100):
    try:
        return service.get_main_categories(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int):
    try:
        category = service.get_category(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
