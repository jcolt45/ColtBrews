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
            pot_id = connection.execute(
            sqlalchemy.text("""
                            SELECT potion_id
                            FROM potion_inventory
                            WHERE potion_type = :potion_type
                            """),
                            [{"potion_type": potion.potion_type}]).first().potion_id
    
            connection.execute(
            sqlalchemy.text("""
                            INSERT INTO potion_ledger 
                            (potion_id, potion_change)
                            VALUES (:potion_id, :potions_change)
                            """),
                            [{"potion_id": pot_id, "potion_change": potion.quantity}])
    
            red_ml = -1 * (potion.potion_type[0] * potion.quantity)
            green_ml = -1 * (potion.potion_type[1] * potion.quantity)
            blue_ml = -1 * (potion.potion_type[2] * potion.quantity)
            dark_ml = -1 * (potion.potion_type[3] * potion.quantity)
            connection.execute(
            sqlalchemy.text("""
                            INSERT INTO inventory_ledger 
                            (red_ml, green_ml, blue_ml, dark_ml)
                            VALUES (:red_ml, :green_ml, :blue_ml, ;dark_ml)
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
        result = connection.execute(
                sqlalchemy.text("""
                                SELECT 
                                SUM(red_ml) as red_ml,
                                SUM(green_ml) as green_ml
                                SUM(blue_ml) as blue_ml,
                                SUM(dark_ml) as dark_ml
                                FROM inventory_ledger
                                """)).first()
        red_ml = result.red_ml
        green_ml = result.green_ml
        blue_ml = result.blue_ml
        dark_ml = result.dark_ml
        result = connection.execute(sqlalchemy.text("SELECT * FROM potion_inventory"))
        for potion in result:
            cur_pots = connection.execute(
                sqlalchemy.text("""
                                SELECT SUM(potion_change) as potion_change
                                FROM potion_ledger
                                WHERE potion_id = :potion_id
                                """),
                                [{"potion_id": potion.potion_id}]).first().potion_change
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

