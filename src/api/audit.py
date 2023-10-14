from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math

import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/inventory")
def get_inventory():
    """ """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM shop_inventory"))
        first_row = result.first()
        total_ml = first_row.red_ml + first_row.green_ml + first_row.blue_ml + first_row.dark_ml
        result = connection.execute(sqlalchemy.text("SELECT * FROM potion_inventory"))
        total_potions = 0
        for potion in result:
            total_potions += potion.num
        return {"number_of_potions": total_potions, "ml_in_barrels": total_ml, "gold": first_row.gold}

class Result(BaseModel):
    gold_match: bool
    barrels_match: bool
    potions_match: bool

# Gets called once a day
@router.post("/results")
def post_audit_results(audit_explanation: Result):
    """ """
    print(audit_explanation)

    return "OK"
