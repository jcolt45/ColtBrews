from typing import List
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth

import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class Cart(BaseModel):
    items : List[str]
    quantity : List[int]

class NewCart(BaseModel):
    customer: str

c_id = 0
carts:List[Cart] = []

@router.post("/")
def create_cart(new_cart: NewCart):
    """ """
    global c_id, carts
    new_id = c_id
    c_id += 1
    new_c = Cart
    new_c.items = []
    new_c.quantity = []
    carts.append(new_c)
    return {"cart_id": new_id}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """
    cur_cart = carts[cart_id]
    return {"items": cur_cart.items, "quantity": cur_cart.quantity}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    cur_cart = carts[cart_id]
    cur_cart.items.append(item_sku)
    cur_cart.quantity.append(cart_item.quantity)
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    cur_cart = carts[cart_id]
    index = 0
    cost = 0
    cart_red_potions = 0
    cart_green_potions = 0
    cart_blue_potions = 0
    for item in cur_cart.items:
        if item == "RED_POTION_0":
            cart_red_potions = cur_cart.quantity[index]
            cost += (50 * cart_red_potions)
        elif item == "GREEN_POTION_0":
            cart_green_potions = cur_cart.quantity[index]
            cost += (50 * cart_green_potions)
        elif item == "BLUE_POTION_0":
            cart_blue_potions = cur_cart.quantity[index]
            cost += (50 * cart_blue_potions)
        index += 1
    total_potions = cart_red_potions + cart_blue_potions + cart_green_potions

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        first_row = result.first()
        cur_red_potions = first_row.num_red_potions - cart_red_potions
        cur_green_potions = first_row.num_green_potions - cart_green_potions
        cur_blue_potions = first_row.num_blue_potions - cart_blue_potions
        bank = first_row.gold + cost

        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = %d" % (bank)))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = %d" % (cur_red_potions)))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = %d" % (cur_green_potions)))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_potions = %d" % (cur_blue_potions)))

    return {"total_potions_bought": total_potions, "total_gold_paid": cost}
