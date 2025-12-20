from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from . import models, schemas
from .database import Base, engine, get_session

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Grocery List API", version="1.0.0")


def get_db():
    with get_session() as session:
        yield session


@app.get("/health", tags=["Health"])
def healthcheck():
    return {"status": "ok"}


@app.get("/items", response_model=List[schemas.Grocery], tags=["Items"])
def list_items(db: Session = Depends(get_db)):
    return db.query(models.GroceryItem).order_by(models.GroceryItem.created_at.desc()).all()


@app.post("/items", response_model=schemas.Grocery, status_code=status.HTTP_201_CREATED, tags=["Items"])
def create_item(item: schemas.GroceryCreate, db: Session = Depends(get_db)):
    db_item = models.GroceryItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.get("/items/{item_id}", response_model=schemas.Grocery, tags=["Items"])
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(models.GroceryItem, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


@app.put("/items/{item_id}", response_model=schemas.Grocery, tags=["Items"])
def update_item(item_id: int, payload: schemas.GroceryUpdate, db: Session = Depends(get_db)):
    item = db.get(models.GroceryItem, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)

    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.patch("/items/{item_id}/toggle", response_model=schemas.Grocery, tags=["Items"])
def toggle_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(models.GroceryItem, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    item.purchased = not item.purchased
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Items"])
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(models.GroceryItem, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    db.delete(item)
    db.commit()
    return None