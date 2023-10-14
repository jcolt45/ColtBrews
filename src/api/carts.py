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

class NewCart(BaseModel):
    customer: str

@router.post("/")
def create_cart(new_cart: NewCart):
    """ """
    with db.engine.begin() as connection:
        new_id = connection.execute(
            sqlalchemy.text("""
                            INSERT INTO carts
                            (name, cost)
                            VALUES (:name, 0) 
                            RETURNING cart_id
                            """),
                            [{"name": new_cart.customer}])
    return {"cart_id": new_id.first().cart_id}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """
    items = []
    quantity = []
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("""
                            SELECT * FROM carts_items 
                            WHERE cart_id = :cart_id
                            """),
                            [{"cart_id": cart_id}])
        for row in result:
            items.append(row.sku)
            quantity.append(row.quantity)
    return {"items": items, "quantity": quantity}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    with db.engine.begin() as connection:
        potion_id = connection.execute(
            sqlalchemy.text("""
                            SELECT potion_id 
                            FROM potion_inventory
                            WHERE sku = :item_sku
                            """),
                            [{"item_sku": item_sku}])
        connection.execute(
            sqlalchemy.text("""
                            INSERT INTO cart_items 
                            (cart_id, potion_id, sku, quantity)
                            VALUES (:cart_id, :potion_id, :sku, :quantity)
                            """),
                            [{"cart_id": cart_id, "potion_id": potion_id, "sku": item_sku, "quantity": cart_item.quantity}])
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("""
                            SELECT * FROM carts_items 
                            WHERE cart_id = :cart_id
                            """),
                            [{"cart_id": cart_id}])
        total_potions = 0
        total_cost = 0
        for row in result:
            total_potions += row.quantity
            connection.execute(
                sqlalchemy.text("""
                                UPDATE potion_inventory 
                                SET num = num - :pots
                                WHERE potion_id = :pot_id
                                """),
                                [{"pots": row.quantity, "pot_id": row.potion_id}])
            cost = connection.execute(
                sqlalchemy.text("""
                                SELECT cost FROM potion_inventory 
                                WHERE potion_id = :pot_id
                                """),
                                [{"pot_id": row.potion_id}])
            total_cost += cost * row.quantity
        connection.execute(
            sqlalchemy.text("""
                            UPDATE shop_inventory 
                            SET gold = gold - :cost
                            """),
                            [{"cost": total_cost}])
        return {"total_potions_bought": total_potions, "total_gold_paid": total_cost}

