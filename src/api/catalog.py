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
            num_pots = connection.execute(
                sqlalchemy.text("""
                                SELECT SUM(potion_change)
                                as num_pots
                                FROM potion_ledger
                                WHERE potion_id = :potion_id
                                """),
                                [{"potion_id": potion.potion_id}]).first().num_pots
            if (num_pots > 0):
                plan.append({
                "sku": potion.sku, 
                "name": potion.name,
                "quantity": potion.num,
                "price": potion.cost,
                "potion_type": potion.type,
                })
    return plan
        
    