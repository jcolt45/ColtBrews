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
    for potion in potions_delivered:
        if potion.potion_type == [100, 0, 0, 0]:
            new_red_bots = potion.quantity

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        for row in result:
            cur_red_potions = row.num_red_potions + new_red_bots
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = %d" % (cur_red_potions)))

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

    cur_red_ml = 0
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        for row in result:
            cur_red_ml += row.num_red_ml
        new_red_bots = 0
        while (cur_red_ml >= 100):
            new_red_bots += 1
            cur_red_ml -= 100
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = %d" % (cur_red_ml)))

    return [
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": new_red_bots,
            }
        ]
