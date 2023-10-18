from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth

import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """
    with db.engine.begin() as connection:
        connection.execute(
                sqlalchemy.text("DELETE FROM inventory_ledger"))
        connection.execute(
            sqlalchemy.text("""
                            INSERT INTO inventory_ledger 
                            (gold)
                            VALUES (100)
                            """))
        connection.execute(
                sqlalchemy.text("DELETE FROM potion_ledger"))
        result = connection.execute(
                sqlalchemy.text("SELECT * FROM potion_inventory"))
        for potion in result:
            connection.execute(
            sqlalchemy.text("""
                            INSERT INTO potion_ledger 
                            (potion_id, potion_change)
                            VALUES (:potion_id, 0)
                            """),
                            [{"potion_id": potion.potion_id}])
        connection.execute(
                sqlalchemy.text("DELETE FROM carts"))
        connection.execute(
                sqlalchemy.text("DELETE FROM cart_items"))
    return "OK"


@router.get("/shop_info/")
def get_shop_info():
    """ """

    # TODO: Change me!
    return {
        "shop_name": "ColtBrews",
        "shop_owner": "Jack Colt",
    }

