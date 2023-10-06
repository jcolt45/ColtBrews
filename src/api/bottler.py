from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth

import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver")
def post_deliver_bottles(potions_delivered: list[PotionInventory]):
    """ """
    print(potions_delivered)

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        first_row = result.first()
        cur_red_ml = first_row.num_red_ml
        cur_red_potions = first_row.num_red_potions
        cur_green_ml = first_row.num_green_ml
        cur_green_potions = first_row.num_green_potions
        cur_blue_ml = first_row.num_blue_ml
        cur_blue_potions = first_row.num_blue_potions
        for potion in potions_delivered:
            if potion.potion_type == [100, 0, 0, 0]:
                cur_red_potions += potion.quantity
                cur_red_ml -= (100 * potion.quantity)
            elif potion.potion_type == [0, 100, 0, 0]:
                cur_green_potions += potion.quantity
                cur_green_ml -= (100 * potion.quantity)
            elif potion.potion_type == [0, 0, 100, 0]:
                cur_blue_potions += potion.quantity
                cur_blue_ml -= (100 * potion.quantity)
                
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = %d" % (cur_red_ml)))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = %d" % (cur_red_potions)))

        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = %d" % (cur_green_ml)))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = %d" % (cur_green_potions)))

        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = %d" % (cur_blue_ml)))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_potions = %d" % (cur_blue_potions)))

    return "OK"

# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        first_row = result.first()
        plan = []
        
        #bottle red ml
        cur_red_ml = first_row.num_red_ml
        new_red_bots = 0
        while (cur_red_ml >= 100):
            new_red_bots += 1
            cur_red_ml -= 100
        if new_red_bots > 0:
            plan.append({
            "potion_type": [100, 0, 0, 0],
            "quantity": new_red_bots,
            })
        #bottle green ml
        cur_green_ml = first_row.num_green_ml
        new_green_bots = 0
        while (cur_green_ml >= 100):
            new_green_bots += 1
            cur_green_ml -= 100
        if new_green_bots > 0:
            plan.append({
            "potion_type": [0, 100, 0, 0],
            "quantity": new_green_bots,
            })
        #bottle blue ml
        cur_blue_ml = first_row.num_blue_ml
        new_blue_bots = 0
        while (cur_red_ml >= 100):
            new_blue_bots += 1
            cur_blue_ml -= 100
        if new_blue_bots > 0:
            plan.append({
            "potion_type": [0, 0, 100, 0],
            "quantity": new_blue_bots,
            })

    return plan
