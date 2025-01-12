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
    cost = 0
    red_ml = 0
    green_ml = 0
    blue_ml = 0
    dark_ml = 0

    for barrel in barrels_delivered:
        if barrel.potion_type == [1, 0, 0, 0]:
            red_ml += (barrel.ml_per_barrel * barrel.quantity)
        elif barrel.potion_type == [0, 1, 0, 0]:
            green_ml += (barrel.ml_per_barrel * barrel.quantity)
        elif barrel.potion_type == [0, 0, 1, 0]:
            blue_ml += (barrel.ml_per_barrel * barrel.quantity)
        elif barrel.potion_type == [0, 0, 0, 1]:
            dark_ml += (barrel.ml_per_barrel * barrel.quantity)
        cost -= (barrel.price * barrel.quantity)
    
    with db.engine.begin() as connection:
        new_id = connection.execute(
            sqlalchemy.text("""
                            INSERT INTO transactions
                            (description)
                            VALUES ('Delivered Barels') 
                            RETURNING transaction_id
                            """)).first().transaction_id
        connection.execute(
            sqlalchemy.text("""
                            INSERT INTO inventory_ledger 
                            (gold, red_ml, green_ml, blue_ml, dark_ml, transaction_id)
                            VALUES (:gold, :red_ml, :green_ml, :blue_ml, :dark_ml, :t_id)
                            """),
                            [{"gold": cost, "red_ml": red_ml, "green_ml": green_ml, "blue_ml": blue_ml, "dark_ml": dark_ml, "t_id": new_id}])
    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        result = connection.execute(
                sqlalchemy.text("""
                                SELECT 
                                SUM(gold) as gold,
                                SUM(red_ml) as red_ml,
                                SUM(green_ml) as green_ml,
                                SUM(blue_ml) as blue_ml,
                                SUM(dark_ml) as dark_ml
                                FROM inventory_ledger
                                """)).first()
        bank = result.gold
        print(bank)
        red_ml = result.red_ml
        green_ml = result.green_ml
        blue_ml = result.blue_ml
        dark_ml = result.dark_ml

        mini_red = "MINI_RED_BARREL"
        mini_red_num = 0
        small_red = "SMALL_RED_BARREL"
        small_red_num = 0
        med_red = "MEDIUM_RED_BARREL"
        med_red_num = 0
        large_red = "LARGE_RED_BARREL"
        large_red_num = 0

        mini_green = "MINI_GREEN_BARREL"
        mini_green_num = 0
        small_green = "SMALL_GREEN_BARREL"
        small_green_num = 0
        med_green = "MEDIUM_GREEN_BARREL"
        med_green_num = 0
        large_green = "LARGE_GREEN_BARREL"
        large_green_num = 0

        mini_blue = "MINI_BLUE_BARREL"
        mini_blue_num = 0
        small_blue = "SMALL_BLUE_BARREL"
        small_blue_num = 0
        med_blue = "MEDIUM_BLUE_BARREL"
        med_blue_num = 0
        large_blue = "LARGE_BLUE_BARREL"
        large_blue_num = 0

        mini_dark = "MINI_DARK_BARREL"
        mini_dark_num = 0
        small_dark = "SMALL_DARK_BARREL"
        small_dark_num = 0
        med_dark = "MEDIUM_DARK_BARREL"
        med_dark_num = 0
        large_dark = "LARGE_DARK_BARREL"
        large_dark_num = 0

        min_ml = 500
        for barrel in wholesale_catalog:
            if (barrel.potion_type == [1, 0 , 0, 0]) & (red_ml < min_ml):
                #red barrels
                if (bank >= barrel.price):
                    if (barrel.sku == large_red):
                        large_red_num += 1
                    elif (barrel.sku == med_red):
                        med_red_num += 1
                    elif (barrel.sku == small_red):
                        small_red_num += 1
                    elif (barrel.sku == mini_red):
                        mini_red_num += 1
                    red_ml += barrel.ml_per_barrel
                    bank -= barrel.price
            elif (barrel.potion_type == [0, 1, 0, 0]) & (green_ml < min_ml):
                #green barrels
                if (bank >= barrel.price):
                    if (barrel.sku == large_green):
                        large_green_num += 1
                    elif (barrel.sku == med_green):
                        med_green_num += 1
                    elif (barrel.sku == small_green):
                        small_green_num += 1
                    elif (barrel.sku == mini_green):
                        mini_green_num += 1
                    green_ml += barrel.ml_per_barrel
                    bank -= barrel.price
            elif (barrel.potion_type == [0, 0, 1, 0]) & (blue_ml < min_ml):
                #blue barrels
                if (bank >= barrel.price):
                    if (barrel.sku == large_blue):
                        large_blue_num += 1
                    elif (barrel.sku == med_blue):
                        med_blue_num += 1
                    elif (barrel.sku == small_blue):
                        small_blue_num += 1
                    elif (barrel.sku == mini_blue):
                        mini_blue_num += 1
                    blue_ml += barrel.ml_per_barrel
                    bank -= barrel.price
            elif (barrel.potion_type == [0, 0, 0, 1]) & (dark_ml < min_ml):
                #dark barrels
                if (bank >= barrel.price):
                    if (barrel.sku == large_dark):
                        large_dark_num += 1
                    elif (barrel.sku == med_dark):
                        med_dark_num += 1
                    elif (barrel.sku == small_dark):
                        small_dark_num += 1
                    elif (barrel.sku == mini_dark):
                        mini_dark_num += 1
                    dark_ml += barrel.ml_per_barrel
                    bank -= barrel.price
        
        plan = []
        #add red barrels to plan
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
        if (med_red_num > 0):
            plan.append({
            "sku": med_red,
            "quantity": med_red_num,
            })
        if (large_red_num > 0):
            plan.append({
            "sku": large_red,
            "quantity": large_red_num,
            })
        #add green barrels to plan
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
        if (med_green_num > 0):
            plan.append({
            "sku": med_green,
            "quantity": med_green_num,
            })
        if (large_green_num > 0):
            plan.append({
            "sku": large_green,
            "quantity": large_green_num,
            })
        #add blue barrels to plan
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
        if (med_blue_num > 0):
            plan.append({
            "sku": med_blue,
            "quantity": med_blue_num,
            })
        if (large_blue_num > 0):
            plan.append({
            "sku": large_blue,
            "quantity": large_blue_num,
            })
        #add dark barrels to plan
        if (mini_dark_num > 0):
            plan.append({
            "sku": mini_dark,
            "quantity": mini_dark_num,
            })
        if (small_dark_num > 0):
            plan.append({
            "sku": small_dark,
            "quantity": small_dark_num,
            })
        if (med_dark_num > 0):
            plan.append({
            "sku": med_dark,
            "quantity": med_dark_num,
            })
        if (large_dark_num > 0):
            plan.append({
            "sku": large_dark,
            "quantity": large_dark_num,
            })
        return plan



#[Barrel(sku='LARGE_RED_BARREL', ml_per_barrel=10000, potion_type=[1, 0, 0, 0], price=500, quantity=30),
#Barrel(sku='MEDIUM_RED_BARREL', ml_per_barrel=2500, potion_type=[1, 0, 0, 0], price=250, quantity=10),
#Barrel(sku='SMALL_RED_BARREL', ml_per_barrel=500, potion_type=[1, 0, 0, 0], price=100, quantity=10),
#Barrel(sku='MINI_RED_BARREL', ml_per_barrel=200, potion_type=[1, 0, 0, 0], price=60, quantity=1)]