from fastapi import APIRouter, HTTPException
from typing import List, Optional
from services.product_service import ProductService
from models.schemas import ProductResponse, ClosestProductRequest

router = APIRouter(prefix="/products", tags=["Products"])
service = ProductService()

@router.get("/closest", response_model=List[ProductResponse])
def get_closest_products_by_query(query: str, limit: int = 10, category_id: Optional[int] = None):
    try:
        return service.get_closest_products(query=query, limit=limit, category_id=category_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/closest", response_model=List[ProductResponse])
def get_closest_products(request: ClosestProductRequest):
    try:
        if request.query is not None:
            return service.get_closest_products(query=request.query, limit=request.limit, category_id=request.category_id)
        elif request.vector is not None:
            return service.get_closest_products(query=request.vector, limit=request.limit, category_id=request.category_id)
        else:
            raise HTTPException(status_code=400, detail="Either 'query' or 'vector' must be provided.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[ProductResponse])
def get_products(limit: int = 100):
    try:
        return service.get_products(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int):
    try:
        product = service.get_product(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/category/{category_id}", response_model=List[ProductResponse])
def get_products_by_category(category_id: int, limit: int = 100):
    try:
        return service.get_products_by_category(category_id, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/main-category/{category_id}", response_model=List[ProductResponse])
def get_products_by_main_category(category_id: int, limit: int = 100):
    try:
        return service.get_products_by_main_category(category_id, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
