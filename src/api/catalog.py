from fastapi import APIRouter

import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    # Can return a max of 20 items.
    plan = []
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM potion_inventory"))
        for potion in result:
            if (potion.num > 0):
                plan.append({
                "sku": potion.sku, 
                "name": potion.name,
                "quantity": potion.num,
                "price": potion.cost,
                "potion_type": potion.type,
                })
    return plan
        
    