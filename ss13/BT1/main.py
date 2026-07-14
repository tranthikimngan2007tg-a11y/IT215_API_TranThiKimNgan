from fastapi import FastAPI, Depends, Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from database import Base, engine, get_db
from response import APIResponse
from schemas import (
    MenuItemRequestDTO,
    MenuItemUpdateDTO,
    MenuItemResponseDTO
)
import menu_item_services

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Catering Menu Management"
)


@app.post("/menu-items")
def create_menu_item(
    menu_item: MenuItemRequestDTO,
    request: Request,
    db: Session = Depends(get_db)
):
    item = menu_item_services.create_menu_item(menu_item, db)

    if item is None:
        return APIResponse(
            statusCode=400,
            message="Dish code already exists",
            error="Bad Request",
            data=None,
            path=request.url.path,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    return APIResponse(
        statusCode=201,
        message="Create menu item successfully",
        error=None,
        data=MenuItemResponseDTO.model_validate(item),
        path=request.url.path,
        timestamp=datetime.now(timezone.utc).isoformat()
    )


@app.get("/menu-items")
def get_all_menu_items(
    request: Request,
    db: Session = Depends(get_db)
):
    items = menu_item_services.get_all_menu_items(db)

    return APIResponse(
        statusCode=200,
        message="Get all menu items successfully",
        error=None,
        data=[
            MenuItemResponseDTO.model_validate(item)
            for item in items
        ],
        path=request.url.path,
        timestamp=datetime.now(timezone.utc).isoformat()
    )


@app.get("/menu-items/{item_id}")
def get_menu_item(
    item_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    item = menu_item_services.get_menu_item_by_id(item_id, db)

    if not item:
        return APIResponse(
            statusCode=404,
            message="Menu item not found",
            error="Not Found",
            data=None,
            path=request.url.path,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    return APIResponse(
        statusCode=200,
        message="Get menu item successfully",
        error=None,
        data=MenuItemResponseDTO.model_validate(item),
        path=request.url.path,
        timestamp=datetime.now(timezone.utc).isoformat()
    )


@app.put("/menu-items/{item_id}")
def update_menu_item(
    item_id: int,
    menu_item: MenuItemUpdateDTO,
    request: Request,
    db: Session = Depends(get_db)
):
    item = menu_item_services.update_menu_item(
        item_id,
        menu_item,
        db
    )

    if item is None:
        return APIResponse(
            statusCode=404,
            message="Menu item not found",
            error="Not Found",
            data=None,
            path=request.url.path,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    if item is False:
        return APIResponse(
            statusCode=400,
            message="Dish code already exists",
            error="Bad Request",
            data=None,
            path=request.url.path,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    return APIResponse(
        statusCode=200,
        message="Update menu item successfully",
        error=None,
        data=MenuItemResponseDTO.model_validate(item),
        path=request.url.path,
        timestamp=datetime.now(timezone.utc).isoformat()
    )


@app.delete("/menu-items/{item_id}")
def delete_menu_item(
    item_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    item = menu_item_services.delete_menu_item(
        item_id,
        db
    )

    if not item:
        return APIResponse(
            statusCode=404,
            message="Menu item not found",
            error="Not Found",
            data=None,
            path=request.url.path,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    return APIResponse(
        statusCode=200,
        message="Delete menu item successfully",
        error=None,
        data=None,
        path=request.url.path,
        timestamp=datetime.now(timezone.utc).isoformat()
    )