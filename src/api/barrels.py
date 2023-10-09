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
        add_red_ml = first_row.num_red_ml
        add_green_ml = first_row.num_green_ml
        add_blue_ml = first_row.num_blue_ml

        for barrel in barrels_delivered:
            if barrel.potion_type == [100, 0, 0, 0]:
                add_red_ml += (barrel.ml_per_barrel * barrel.quantity)
            if barrel.potion_type == [0, 100, 0, 0]:
                add_green_ml += (barrel.ml_per_barrel * barrel.quantity)
            if barrel.potion_type == [0, 0, 100, 0]:
                add_blue_ml += (barrel.ml_per_barrel * barrel.quantity)
            bank -= (barrel.price * barrel.quantity)

        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = %d" % (add_red_ml)))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = %d" % (add_green_ml)))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = %d" % (add_blue_ml)))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = %d" % (bank)))

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        first_row = result.first()
        bank = first_row.gold
        cur_red_potions = first_row.num_red_potions
        cur_green_potions = first_row.num_green_potions
        cur_blue_potions = first_row.num_blue_potions

        mini_red = "MINI_RED_BARREL"
        mini_red_num = 0
        small_red = "SMALL_RED_BARREL"
        small_red_num = 0

        mini_green = "MINI_GREEN_BARREL"
        mini_green_num = 0
        small_green = "SMALL_GREEN_BARREL"
        small_green_num = 0

        mini_blue = "MINI_BLUE_BARREL"
        mini_blue_num = 0
        small_blue = "SMALL_BLUE_BARREL"
        small_blue_num = 0

        for barrel in wholesale_catalog:
            if (barrel.potion_type == [100, 0 , 0, 0]) & (cur_red_potions < 10):
                if (bank >= barrel.price) & (barrel.sku == small_red):
                    small_red_num += 1
                    bank -= barrel.price
                elif (bank >= barrel.price) & (barrel.sku == mini_red):
                    mini_red_num += 1
                    bank -= barrel.price
            elif (barrel.potion_type == [0, 100, 0, 0]) & (cur_green_potions < 10):
                if (bank >= barrel.price) & (barrel.sku == small_green):
                    small_green_num += 1
                    bank -= barrel.price
                elif (bank >= barrel.price) & (barrel.sku == mini_green):
                    mini_green_num += 1
                    bank -= barrel.price
            elif (barrel.potion_type == [0, 0, 100, 0]) & (cur_blue_potions < 10):
                if (bank >= barrel.price) & (barrel.sku == small_blue):
                    small_blue_num += 1
                    bank -= barrel.price
                elif (bank >= barrel.price) & (barrel.sku == mini_blue):
                    mini_blue_num += 1
                    bank -= barrel.price
        
        plan = []
        if (mini_red_num > 0):
            plan.append({
            "sku": mini_red,
            "quantity": mini_red_num,
            })
        if (small_red_num > 0):
            plan.append({
            "sku": small_red,
            "quantity": small_red_num,
            })

        if (mini_green_num > 0):
            plan.append({
            "sku": mini_green,
            "quantity": mini_green_num,
            })
        if (small_green_num > 0):
            plan.append({
            "sku": small_green,
            "quantity": small_green_num,
            })

        if (mini_blue_num > 0):
            plan.append({
            "sku": mini_blue,
            "quantity": mini_blue_num,
            })
        if (small_blue_num > 0):
            plan.append({
            "sku": small_blue,
            "quantity": small_blue_num,
            })

        return plan
