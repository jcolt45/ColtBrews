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

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        first_row = result.first()
        plan = []

        cur_red_potions = first_row.num_red_potions
        if cur_red_potions > 0:
            plan.append({
                "sku": "RED_POTION_0", 
                "name": "red potion",
                "quantity": cur_red_potions,
                "price": 50,
                "potion_type": [100, 0, 0, 0],
            })
        
        cur_green_potions = first_row.num_green_potions
        if cur_green_potions > 0:
            plan.append[{
                "sku": "GREEN_POTION_0", 
                "name": "green potion",
                "quantity": cur_green_potions,
                "price": 50,
                "potion_type": [0, 100, 0, 0],
            }]

        cur_blue_potions = first_row.num_blue_potions
        if cur_blue_potions > 0:
            plan.append[{
                "sku": "BLUE_POTION_0", 
                "name": "blue potion",
                "quantity": cur_blue_potions,
                "price": 50,
                "potion_type": [0, 0, 100, 0],
            }]
        
        return plan
        
    
