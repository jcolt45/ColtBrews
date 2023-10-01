from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth

import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
    """ """
    print(barrels_delivered)

    add_red_ml = 0
    for barrel in barrels_delivered:
        if barrel.sku == "SMALL_RED_BARREL":
            add_red_ml += barrel.ml_per_barrel
    
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        add_red_ml += result.num_red_ml
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = %d" (add_red_ml)))


    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    cur_red_potions = 0
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        for row in result:
            cur_red_potions += row.num_red_potions
            bank = row.gold

        barrels = []
        for barrel in wholesale_catalog:
            if (barrel.sku == "SMALL_RED_BARREL") & (cur_red_potions < 10):
                if bank > barrel.price:
                    bank -= barrel.price
                    barrels.append(barrel)
        
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = %d" (bank)))
        return barrels

