from typing import List
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum

import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.
    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.
    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.
    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.
    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """
    
        

    return {
        "previous": "",
        "next": "",
        "results": [
            {
                "line_item_id": 1,
                "item_sku": "1 oblivion potion",
                "customer_name": "Scaramouche",
                "line_item_total": 50,
                "timestamp": "2021-01-01T00:00:00Z",
            },
            {
                "line_item_id": 2,
                "item_sku": "2 oblivion potion",
                "customer_name": "Scaramouche",
                "line_item_total": 50,
                "timestamp": "2021-01-01T00:00:00Z",
            }
        ],
    }


class NewCart(BaseModel):
    customer: str

@router.post("/")
def create_cart(new_cart: NewCart):
    """ """
    with db.engine.begin() as connection:
        new_id = connection.execute(
            sqlalchemy.text("""
                            INSERT INTO carts
                            (name)
                            VALUES (:name) 
                            RETURNING cart_id
                            """),
                            [{"name": new_cart.customer}]).first().cart_id
    return {"cart_id": new_id}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """
    items = []
    quantity = []
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("""
                            SELECT * 
                            FROM cart_items 
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
        potion = connection.execute(
            sqlalchemy.text("""
                            SELECT potion_id
                            FROM potion_inventory
                            WHERE sku = :item_sku
                            """),
                            [{"item_sku": item_sku}]).first().potion_id
        connection.execute(
            sqlalchemy.text("""
                            INSERT INTO cart_items 
                            (cart_id, potion_id, sku, quantity)
                            VALUES (:cart_id, :potion_id, :sku, :quantity)
                            """),
                            [{"cart_id": cart_id, "potion_id": potion, "sku": item_sku, "quantity": cart_item.quantity}])
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    with db.engine.begin() as connection:
        new_id = connection.execute(
            sqlalchemy.text("""
                            INSERT INTO transactions
                            (description)
                            VALUES ('Cart Checkout') 
                            RETURNING transaction_id
                            """)).first().transaction_id
        result = connection.execute(
            sqlalchemy.text("""
                            SELECT * 
                            FROM cart_items 
                            WHERE cart_id = :cart_id
                            """),
                            [{"cart_id": cart_id}])
        total_potions = 0
        total_cost = 0
        for row in result:
            total_potions += row.quantity
            connection.execute(
                sqlalchemy.text("""
                                INSERT INTO potion_ledger 
                                (potion_id, potion_change, transaction_id)
                                VALUES (:potion_id, :potion_change, :t_id)
                                """),
                                [{"potion_id": row.potion_id, "potion_change": (-1 * row.quantity), "t_id": new_id}])
            cost = connection.execute(
                sqlalchemy.text("""
                                SELECT cost 
                                FROM potion_inventory 
                                WHERE potion_id = :pot_id
                                """),
                                [{"pot_id": row.potion_id}]).first().cost
            total_cost += cost * row.quantity
        connection.execute(
            sqlalchemy.text("""
                            INSERT INTO inventory_ledger
                            (gold, transaction_id)
                            VALUES (:gold, :t_id)
                            """),
                            [{"gold": total_cost, "t_id": new_id}])
        return {"total_potions_bought": total_potions, "total_gold_paid": total_cost}

