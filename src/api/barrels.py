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
    
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        first_row = result.first()
        bank = first_row.gold
        add_red_ml = 0
        for barrel in barrels_delivered:
            if barrel.sku == "SMALL_RED_BARREL":
                add_red_ml += (barrel.ml_per_barrel * barrel.quantity)
            bank -= (barrel.price * barrel.quantity)
        add_red_ml += first_row.num_red_ml
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = %d" % (add_red_ml)))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = %d" % (bank)))
        
    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    cur_red_potions = 0
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        first_row = result.first()
        cur_red_potions += first_row.num_red_potions
        bank = first_row.gold

        small_red = "SMALL_RED_BARREL"
        small_red_num = 0
        for barrel in wholesale_catalog:
            if (barrel.sku == small_red) & (cur_red_potions < 10):
                if (bank > barrel.price) & (barrel.quantity > 0):
                    small_red_num += 1
        
        return [
        {
            "sku": small_red,
            "quantity": small_red_num,
        }
    ]

