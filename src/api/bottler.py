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
        for potion in potions_delivered:
            connection.execute(
                sqlalchemy.text("""
                                UPDATE potion_inventory 
                                SET num = num + :pots
                                WHERE type = :type
                                """),
                                [{"pots": potion.quantity, "type": potion.potion_type}])
            red_ml = potion.potion_type[0] * potion.quantity
            green_ml = potion.potion_type[1] * potion.quantity
            blue_ml = potion.potion_type[2] * potion.quantity
            dark_ml = potion.potion_type[3] * potion.quantity
            connection.execute(
                sqlalchemy.text("""
                                UPDATE shop_inventory SET 
                                red_ml = red_ml - :red_ml,
                                green_ml = green_ml - :green_ml,
                                blue_ml = blue_ml - :blue_ml,
                                dark_ml = dark_ml - :dark_ml
                                """),
                                [{"red_ml": red_ml, "green_ml": green_ml, "blue_ml": blue_ml, "dark_ml": dark_ml}])

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
    plan = []
    min_pots = 5
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM shop_inventory"))
        first_row = result.first()
        red_ml = first_row.red_ml
        green_ml = first_row.green_ml
        blue_ml = first_row.blue_ml
        dark_ml = first_row.dark_ml
        result = connection.execute(sqlalchemy.text("SELECT * FROM potion_inventory"))
        for potion in result:
            cur_pots = potion.num
            new_pots = 0
            if (cur_pots < min_pots):
                red = potion.type[0]
                green = potion.type[1]
                blue = potion.type[2]
                dark = potion.type[3]
                while (red <= red_ml) & (green <= green_ml) & (blue <= blue_ml) & (dark <= dark_ml) & (cur_pots < min_pots):
                    cur_pots += 1
                    red_ml -= red
                    green_ml -= green
                    blue_ml -= blue
                    dark_ml -= dark
                    new_pots += 1
            if (new_pots > 0):
                plan.append({
                "potion_type": potion.type,
                "quantity": new_pots,
                })
    return plan

