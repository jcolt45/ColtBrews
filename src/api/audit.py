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
        result = connection.execute(
                sqlalchemy.text("""
                                SELECT 
                                SUM(gold) as gold,
                                SUM(red_ml) as red_ml,
                                SUM(green_ml) as green_ml
                                SUM(blue_ml) as blue_ml,
                                SUM(dark_ml) as dark_ml
                                FROM inventory_ledger
                                """)).first()
        total_ml = result.red_ml + result.green_ml + result.blue_ml + result.dark_ml
        total_potions = connection.execute(
                sqlalchemy.text("""
                                SELECT SUM(potion_change) as potions,
                                FROM potion_ledger
                                """)).first().potions
        return {"number_of_potions": total_potions, "ml_in_barrels": total_ml, "gold": result.gold}

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
