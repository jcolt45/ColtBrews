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
    with db.engine.begin() as connection:
        if (search_page == ""):
            off = 0
        else:
            off = (int(search_page) - 1) * 5
        if (sort_col == "timestamp"):
            if ((customer_name != "") & (potion_sku != "")):
                if (sort_order == "asc"):
                    result = connection.execute(
                        sqlalchemy.text("""
                                        SELECT 
                                        carts.name as name, 
                                        carts.created_at as time, 
                                        cart_items.quantity * potion_inventory.cost as cost, 
                                        cart_items.quantity as num,
                                        potion_inventory.sku as sku
                                        FROM carts
                                        JOIN cart_items 
                                        ON carts.cart_id = cart_items.cart_id
                                        JOIN potion_inventory
                                        ON cart_items.potion_id = potion_inventory.potion_id
                                        WHERE carts.name = :name
                                        AND cart_items.sku = :sku
                                        ORDER BY carts.created_at ASC
                                        LIMIT 6
                                        OFFSET :off
                                        """),
                                        [{"name": customer_name, "sku": potion_sku, "off": off}])
                else:
                    result = connection.execute(
                        sqlalchemy.text("""
                                        SELECT 
                                        carts.name as name, 
                                        carts.created_at as time, 
                                        cart_items.quantity * potion_inventory.cost as cost, 
                                        cart_items.quantity as num,
                                        potion_inventory.sku as sku
                                        FROM carts
                                        JOIN cart_items 
                                        ON carts.cart_id = cart_items.cart_id
                                        JOIN potion_inventory
                                        ON cart_items.potion_id = potion_inventory.potion_id
                                        WHERE carts.name = :name
                                        AND cart_items.sku = :sku
                                        ORDER BY carts.created_at DESC
                                        LIMIT 6
                                        OFFSET :off
                                        """),
                                        [{"name": customer_name, "sku": potion_sku, "off": off}])
            elif (customer_name != ""):
                if (sort_order == "asc"):
                        result = connection.execute(
                        sqlalchemy.text("""
                                        SELECT 
                                        carts.name as name, 
                                        carts.created_at as time, 
                                        cart_items.quantity * potion_inventory.cost as cost, 
                                        cart_items.quantity as num,
                                        potion_inventory.sku as sku
                                        FROM carts
                                        JOIN cart_items 
                                        ON carts.cart_id = cart_items.cart_id
                                        JOIN potion_inventory
                                        ON cart_items.potion_id = potion_inventory.potion_id
                                        WHERE carts.name = :name
                                        ORDER BY carts.created_at ASC
                                        LIMIT 6
                                        OFFSET :off
                                        """),
                                        [{"name": customer_name, "off": off}])
                else:
                    result = connection.execute(
                        sqlalchemy.text("""
                                        SELECT 
                                        carts.name as name, 
                                        carts.created_at as time, 
                                        cart_items.quantity * potion_inventory.cost as cost, 
                                        cart_items.quantity as num,
                                        potion_inventory.sku as sku
                                        FROM carts
                                        JOIN cart_items 
                                        ON carts.cart_id = cart_items.cart_id
                                        JOIN potion_inventory
                                        ON cart_items.potion_id = potion_inventory.potion_id
                                        WHERE carts.name = :name
                                        ORDER BY carts.created_at DESC
                                        LIMIT 6
                                        OFFSET :off
                                        """),
                                        [{"name": customer_name, "off": off}])
            elif (potion_sku != ""):
                if (sort_order == "asc"):
                        result = connection.execute(
                        sqlalchemy.text("""
                                        SELECT 
                                        carts.name as name, 
                                        carts.created_at as time, 
                                        cart_items.quantity * potion_inventory.cost as cost, 
                                        cart_items.quantity as num,
                                        potion_inventory.sku as sku
                                        FROM carts
                                        JOIN cart_items 
                                        ON carts.cart_id = cart_items.cart_id
                                        JOIN potion_inventory
                                        ON cart_items.potion_id = potion_inventory.potion_id
                                        WHERE cart_items.sku = :sku
                                        ORDER BY carts.created_at ASC
                                        LIMIT 6
                                        OFFSET :off
                                        """),
                                        [{"sku": potion_sku, "off": off}])
                else:
                    result = connection.execute(
                        sqlalchemy.text("""
                                        SELECT 
                                        carts.name as name, 
                                        carts.created_at as time, 
                                        cart_items.quantity * potion_inventory.cost as cost, 
                                        cart_items.quantity as num,
                                        potion_inventory.sku as sku
                                        FROM carts
                                        JOIN cart_items 
                                        ON carts.cart_id = cart_items.cart_id
                                        JOIN potion_inventory
                                        ON cart_items.potion_id = potion_inventory.potion_id
                                        WHERE cart_items.sku = :sku
                                        ORDER BY carts.created_at DESC
                                        LIMIT 6
                                        OFFSET :off
                                        """),
                                        [{"sku": potion_sku, "off": off}])
            else:
                if (sort_order == "asc"):
                        result = connection.execute(
                        sqlalchemy.text("""
                                        SELECT 
                                        carts.name as name, 
                                        carts.created_at as time, 
                                        cart_items.quantity * potion_inventory.cost as cost, 
                                        cart_items.quantity as num,
                                        potion_inventory.sku as sku
                                        FROM carts
                                        JOIN cart_items 
                                        ON carts.cart_id = cart_items.cart_id
                                        JOIN potion_inventory
                                        ON cart_items.potion_id = potion_inventory.potion_id
                                        ORDER BY carts.created_at ASC
                                        LIMIT 6
                                        OFFSET :off
                                        """),
                                        [{"off": off}])
                else:
                    result = connection.execute(
                        sqlalchemy.text("""
                                        SELECT 
                                        carts.name as name, 
                                        carts.created_at as time, 
                                        cart_items.quantity * potion_inventory.cost as cost, 
                                        cart_items.quantity as num,
                                        potion_inventory.sku as sku
                                        FROM carts
                                        JOIN cart_items 
                                        ON carts.cart_id = cart_items.cart_id
                                        JOIN potion_inventory
                                        ON cart_items.potion_id = potion_inventory.potion_id
                                        ORDER BY carts.created_at DESC
                                        LIMIT 6
                                        OFFSET :off
                                        """),
                                        [{"off": off}])
        elif (sort_col == "item_sku"):
            if ((customer_name != "") & (potion_sku != "")):
                if (sort_order == "asc"):
                    result = connection.execute(
                        sqlalchemy.text("""
                                        SELECT 
                                        carts.name as name, 
                                        carts.created_at as time, 
                                        cart_items.quantity * potion_inventory.cost as cost, 
                                        cart_items.quantity as num,
                                        potion_inventory.sku as sku
                                        FROM carts
                                        JOIN cart_items 
                                        ON carts.cart_id = cart_items.cart_id
                                        JOIN potion_inventory
                                        ON cart_items.potion_id = potion_inventory.potion_id
                                        WHERE carts.name = :name
                                        AND cart_items.sku = :sku
                                        ORDER BY potion_inventory.sku ASC
                                        LIMIT 6
                                        OFFSET :off
                                        """),
                                        [{"name": customer_name, "sku": potion_sku, "off": off}])
                else:
                    result = connection.execute(
                        sqlalchemy.text("""
                                        SELECT 
                                        carts.name as name, 
                                        carts.created_at as time, 
                                        cart_items.quantity * potion_inventory.cost as cost, 
                                        cart_items.quantity as num,
                                        potion_inventory.sku as sku
                                        FROM carts
                                        JOIN cart_items 
                                        ON carts.cart_id = cart_items.cart_id
                                        JOIN potion_inventory
                                        ON cart_items.potion_id = potion_inventory.potion_id
                                        WHERE carts.name = :name
                                        AND cart_items.sku = :sku
                                        ORDER BY potion_inventory.sku DESC
                                        LIMIT 6
                                        OFFSET :off
                                        """),
                                        [{"name": customer_name, "sku": potion_sku, "off": off}])
            elif (customer_name != ""):
                if (sort_order == "asc"):
                        result = connection.execute(
                        sqlalchemy.text("""
                                        SELECT 
                                        carts.name as name, 
                                        carts.created_at as time, 
                                        cart_items.quantity * potion_inventory.cost as cost, 
                                        cart_items.quantity as num,
                                        potion_inventory.sku as sku
                                        FROM carts
                                        JOIN cart_items 
                                        ON carts.cart_id = cart_items.cart_id
                                        JOIN potion_inventory
                                        ON cart_items.potion_id = potion_inventory.potion_id
                                        WHERE carts.name = :name
                                        ORDER BY potion_inventory.sku ASC
                                        LIMIT 6
                                        OFFSET :off
                                        """),
                                        [{"name": customer_name, "off": off}])
                else:
                    result = connection.execute(
                        sqlalchemy.text("""
                                        SELECT 
                                        carts.name as name, 
                                        carts.created_at as time, 
                                        cart_items.quantity * potion_inventory.cost as cost, 
                                        cart_items.quantity as num,
                                        potion_inventory.sku as sku
                                        FROM carts
                                        JOIN cart_items 
                                        ON carts.cart_id = cart_items.cart_id
                                        JOIN potion_inventory
                                        ON cart_items.potion_id = potion_inventory.potion_id
                                        WHERE carts.name = :name
                                        ORDER BY potion_inventory.sku DESC
                                        LIMIT 6
                                        OFFSET :off
                                        """),
                                        [{"name": customer_name, "off": off}])
            elif (potion_sku != ""):
                if (sort_order == "asc"):
                        result = connection.execute(
                        sqlalchemy.text("""
                                        SELECT 
                                        carts.name as name, 
                                        carts.created_at as time, 
                                        cart_items.quantity * potion_inventory.cost as cost, 
                                        cart_items.quantity as num,
                                        potion_inventory.sku as sku
                                        FROM carts
                                        JOIN cart_items 
                                        ON carts.cart_id = cart_items.cart_id
                                        JOIN potion_inventory
                                        ON cart_items.potion_id = potion_inventory.potion_id
                                        WHERE cart_items.sku = :sku
                                        ORDER BY potion_inventory.sku ASC
                                        LIMIT 6
                                        OFFSET :off
                                        """),
                                        [{"sku": potion_sku, "off": off}])
                else:
                    result = connection.execute(
                        sqlalchemy.text("""
                                        SELECT 
                                        carts.name as name, 
                                        carts.created_at as time, 
                                        cart_items.quantity * potion_inventory.cost as cost, 
                                        cart_items.quantity as num,
                                        potion_inventory.sku as sku
                                        FROM carts
                                        JOIN cart_items 
                                        ON carts.cart_id = cart_items.cart_id
                                        JOIN potion_inventory
                                        ON cart_items.potion_id = potion_inventory.potion_id
                                        WHERE cart_items.sku = :sku
                                        ORDER BY potion_inventory.sku DESC
                                        LIMIT 6
                                        OFFSET :off
                                        """),
                                        [{"sku": potion_sku, "off": off}])
            else:
                if (sort_order == "asc"):
                        result = connection.execute(
                        sqlalchemy.text("""
                                        SELECT 
                                        carts.name as name, 
                                        carts.created_at as time, 
                                        cart_items.quantity * potion_inventory.cost as cost, 
                                        cart_items.quantity as num,
                                        potion_inventory.sku as sku
                                        FROM carts
                                        JOIN cart_items 
                                        ON carts.cart_id = cart_items.cart_id
                                        JOIN potion_inventory
                                        ON cart_items.potion_id = potion_inventory.potion_id
                                        ORDER BY potion_inventory.sku ASC
                                        LIMIT 6
                                        OFFSET :off
                                        """),
                                        [{"off": off}])
                else:
                    result = connection.execute(
                        sqlalchemy.text("""
                                        SELECT 
                                        carts.name as name, 
                                        carts.created_at as time, 
                                        cart_items.quantity * potion_inventory.cost as cost, 
                                        cart_items.quantity as num,
                                        potion_inventory.sku as sku
                                        FROM carts
                                        JOIN cart_items 
                                        ON carts.cart_id = cart_items.cart_id
                                        JOIN potion_inventory
                                        ON cart_items.potion_id = potion_inventory.potion_id
                                        ORDER BY potion_inventory.sku DESC
                                        LIMIT 6
                                        OFFSET :off
                                        """),
                                        [{"off": off}])
        elif (sort_col == "line_item_total"):
            if ((customer_name != "") & (potion_sku != "")):
                if (sort_order == "asc"):
                    result = connection.execute(
                        sqlalchemy.text("""
                                        SELECT 
                                        carts.name as name, 
                                        carts.created_at as time, 
                                        cart_items.quantity * potion_inventory.cost as cost, 
                                        cart_items.quantity as num,
                                        potion_inventory.sku as sku
                                        FROM carts
                                        JOIN cart_items 
                                        ON carts.cart_id = cart_items.cart_id
                                        JOIN potion_inventory
                                        ON cart_items.potion_id = potion_inventory.potion_id
                                        WHERE carts.name = :name
                                        AND cart_items.sku = :sku
                                        ORDER BY cost ASC
                                        LIMIT 6
                                        OFFSET :off
                                        """),
                                        [{"name": customer_name, "sku": potion_sku, "off": off}])
                else:
                    result = connection.execute(
                        sqlalchemy.text("""
                                        SELECT 
                                        carts.name as name, 
                                        carts.created_at as time, 
                                        cart_items.quantity * potion_inventory.cost as cost, 
                                        cart_items.quantity as num,
                                        potion_inventory.sku as sku
                                        FROM carts
                                        JOIN cart_items 
                                        ON carts.cart_id = cart_items.cart_id
                                        JOIN potion_inventory
                                        ON cart_items.potion_id = potion_inventory.potion_id
                                        WHERE carts.name = :name
                                        AND cart_items.sku = :sku
                                        ORDER BY cost DESC
                                        LIMIT 6
                                        OFFSET :off
                                        """),
                                        [{"name": customer_name, "sku": potion_sku, "off": off}])
            elif (customer_name != ""):
                if (sort_order == "asc"):
                        result = connection.execute(
                        sqlalchemy.text("""
                                        SELECT 
                                        carts.name as name, 
                                        carts.created_at as time, 
                                        cart_items.quantity * potion_inventory.cost as cost, 
                                        cart_items.quantity as num,
                                        potion_inventory.sku as sku
                                        FROM carts
                                        JOIN cart_items 
                                        ON carts.cart_id = cart_items.cart_id
                                        JOIN potion_inventory
                                        ON cart_items.potion_id = potion_inventory.potion_id
                                        WHERE carts.name = :name
                                        ORDER BY cost ASC
                                        LIMIT 6
                                        OFFSET :off
                                        """),
                                        [{"name": customer_name, "off": off}])
                else:
                    result = connection.execute(
                        sqlalchemy.text("""
                                        SELECT 
                                        carts.name as name, 
                                        carts.created_at as time, 
                                        cart_items.quantity * potion_inventory.cost as cost, 
                                        cart_items.quantity as num,
                                        potion_inventory.sku as sku
                                        FROM carts
                                        JOIN cart_items 
                                        ON carts.cart_id = cart_items.cart_id
                                        JOIN potion_inventory
                                        ON cart_items.potion_id = potion_inventory.potion_id
                                        WHERE carts.name = :name
                                        ORDER BY cost DESC
                                        LIMIT 6
                                        OFFSET :off
                                        """),
                                        [{"name": customer_name, "off": off}])
            elif (potion_sku != ""):
                if (sort_order == "asc"):
                        result = connection.execute(
                        sqlalchemy.text("""
                                        SELECT 
                                        carts.name as name, 
                                        carts.created_at as time, 
                                        cart_items.quantity * potion_inventory.cost as cost, 
                                        cart_items.quantity as num,
                                        potion_inventory.sku as sku
                                        FROM carts
                                        JOIN cart_items 
                                        ON carts.cart_id = cart_items.cart_id
                                        JOIN potion_inventory
                                        ON cart_items.potion_id = potion_inventory.potion_id
                                        WHERE cart_items.sku = :sku
                                        ORDER BY cost ASC
                                        LIMIT 6
                                        OFFSET :off
                                        """),
                                        [{"sku": potion_sku, "off": off}])
                else:
                    result = connection.execute(
                        sqlalchemy.text("""
                                        SELECT 
                                        carts.name as name, 
                                        carts.created_at as time, 
                                        cart_items.quantity * potion_inventory.cost as cost, 
                                        cart_items.quantity as num,
                                        potion_inventory.sku as sku
                                        FROM carts
                                        JOIN cart_items 
                                        ON carts.cart_id = cart_items.cart_id
                                        JOIN potion_inventory
                                        ON cart_items.potion_id = potion_inventory.potion_id
                                        WHERE cart_items.sku = :sku
                                        ORDER BY cost DESC
                                        LIMIT 6
                                        OFFSET :off
                                        """),
                                        [{"sku": potion_sku, "off": off}])
            else:
                if (sort_order == "asc"):
                        result = connection.execute(
                        sqlalchemy.text("""
                                        SELECT 
                                        carts.name as name, 
                                        carts.created_at as time, 
                                        cart_items.quantity * potion_inventory.cost as cost, 
                                        cart_items.quantity as num,
                                        potion_inventory.sku as sku
                                        FROM carts
                                        JOIN cart_items 
                                        ON carts.cart_id = cart_items.cart_id
                                        JOIN potion_inventory
                                        ON cart_items.potion_id = potion_inventory.potion_id
                                        ORDER BY cost ASC
                                        LIMIT 6
                                        OFFSET :off
                                        """),
                                        [{"off": off}])
                else:
                    result = connection.execute(
                        sqlalchemy.text("""
                                        SELECT 
                                        carts.name as name, 
                                        carts.created_at as time, 
                                        cart_items.quantity * potion_inventory.cost as cost, 
                                        cart_items.quantity as num,
                                        potion_inventory.sku as sku
                                        FROM carts
                                        JOIN cart_items 
                                        ON carts.cart_id = cart_items.cart_id
                                        JOIN potion_inventory
                                        ON cart_items.potion_id = potion_inventory.potion_id
                                        ORDER BY cost DESC
                                        LIMIT 6
                                        OFFSET :off
                                        """),
                                        [{"off": off}])
        elif (sort_col == "customer_name"):
            if ((customer_name != "") & (potion_sku != "")):
                if (sort_order == "asc"):
                    result = connection.execute(
                        sqlalchemy.text("""
                                        SELECT 
                                        carts.name as name, 
                                        carts.created_at as time, 
                                        cart_items.quantity * potion_inventory.cost as cost, 
                                        cart_items.quantity as num,
                                        potion_inventory.sku as sku
                                        FROM carts
                                        JOIN cart_items 
                                        ON carts.cart_id = cart_items.cart_id
                                        JOIN potion_inventory
                                        ON cart_items.potion_id = potion_inventory.potion_id
                                        WHERE carts.name = :name
                                        AND cart_items.sku = :sku
                                        ORDER BY name ASC
                                        LIMIT 6
                                        OFFSET :off
                                        """),
                                        [{"name": customer_name, "sku": potion_sku, "off": off}])
                else:
                    result = connection.execute(
                        sqlalchemy.text("""
                                        SELECT 
                                        carts.name as name, 
                                        carts.created_at as time, 
                                        cart_items.quantity * potion_inventory.cost as cost, 
                                        cart_items.quantity as num,
                                        potion_inventory.sku as sku
                                        FROM carts
                                        JOIN cart_items 
                                        ON carts.cart_id = cart_items.cart_id
                                        JOIN potion_inventory
                                        ON cart_items.potion_id = potion_inventory.potion_id
                                        WHERE carts.name = :name
                                        AND cart_items.sku = :sku
                                        ORDER BY name DESC
                                        LIMIT 6
                                        OFFSET :off
                                        """),
                                        [{"name": customer_name, "sku": potion_sku, "off": off}])
            elif (customer_name != ""):
                if (sort_order == "asc"):
                        result = connection.execute(
                        sqlalchemy.text("""
                                        SELECT 
                                        carts.name as name, 
                                        carts.created_at as time, 
                                        cart_items.quantity * potion_inventory.cost as cost, 
                                        cart_items.quantity as num,
                                        potion_inventory.sku as sku
                                        FROM carts
                                        JOIN cart_items 
                                        ON carts.cart_id = cart_items.cart_id
                                        JOIN potion_inventory
                                        ON cart_items.potion_id = potion_inventory.potion_id
                                        WHERE carts.name = :name
                                        ORDER BY name ASC
                                        LIMIT 6
                                        OFFSET :off
                                        """),
                                        [{"name": customer_name, "off": off}])
                else:
                    result = connection.execute(
                        sqlalchemy.text("""
                                        SELECT 
                                        carts.name as name, 
                                        carts.created_at as time, 
                                        cart_items.quantity * potion_inventory.cost as cost, 
                                        cart_items.quantity as num,
                                        potion_inventory.sku as sku
                                        FROM carts
                                        JOIN cart_items 
                                        ON carts.cart_id = cart_items.cart_id
                                        JOIN potion_inventory
                                        ON cart_items.potion_id = potion_inventory.potion_id
                                        WHERE carts.name = :name
                                        ORDER BY name DESC
                                        LIMIT 6
                                        OFFSET :off
                                        """),
                                        [{"name": customer_name, "off": off}])
            elif (potion_sku != ""):
                if (sort_order == "asc"):
                        result = connection.execute(
                        sqlalchemy.text("""
                                        SELECT 
                                        carts.name as name, 
                                        carts.created_at as time, 
                                        cart_items.quantity * potion_inventory.cost as cost, 
                                        cart_items.quantity as num,
                                        potion_inventory.sku as sku
                                        FROM carts
                                        JOIN cart_items 
                                        ON carts.cart_id = cart_items.cart_id
                                        JOIN potion_inventory
                                        ON cart_items.potion_id = potion_inventory.potion_id
                                        WHERE cart_items.sku = :sku
                                        ORDER BY name ASC
                                        LIMIT 6
                                        OFFSET :off
                                        """),
                                        [{"sku": potion_sku, "off": off}])
                else:
                    result = connection.execute(
                        sqlalchemy.text("""
                                        SELECT 
                                        carts.name as name, 
                                        carts.created_at as time, 
                                        cart_items.quantity * potion_inventory.cost as cost, 
                                        cart_items.quantity as num,
                                        potion_inventory.sku as sku
                                        FROM carts
                                        JOIN cart_items 
                                        ON carts.cart_id = cart_items.cart_id
                                        JOIN potion_inventory
                                        ON cart_items.potion_id = potion_inventory.potion_id
                                        WHERE cart_items.sku = :sku
                                        ORDER BY name DESC
                                        LIMIT 6
                                        OFFSET :off
                                        """),
                                        [{"sku": potion_sku, "off": off}])
            else:
                if (sort_order == "asc"):
                        result = connection.execute(
                        sqlalchemy.text("""
                                        SELECT 
                                        carts.name as name, 
                                        carts.created_at as time, 
                                        cart_items.quantity * potion_inventory.cost as cost, 
                                        cart_items.quantity as num,
                                        potion_inventory.sku as sku
                                        FROM carts
                                        JOIN cart_items 
                                        ON carts.cart_id = cart_items.cart_id
                                        JOIN potion_inventory
                                        ON cart_items.potion_id = potion_inventory.potion_id
                                        ORDER BY name ASC
                                        LIMIT 6
                                        OFFSET :off
                                        """),
                                        [{"off": off}])
                else:
                    result = connection.execute(
                        sqlalchemy.text("""
                                        SELECT 
                                        carts.name as name, 
                                        carts.created_at as time, 
                                        cart_items.quantity * potion_inventory.cost as cost, 
                                        cart_items.quantity as num,
                                        potion_inventory.sku as sku
                                        FROM carts
                                        JOIN cart_items 
                                        ON carts.cart_id = cart_items.cart_id
                                        JOIN potion_inventory
                                        ON cart_items.potion_id = potion_inventory.potion_id
                                        ORDER BY name DESC
                                        LIMIT 6
                                        OFFSET :off
                                        """),
                                        [{"off": off}])
        else:
            return "error"
        
        results = []
        num = 1
        for row in result:
            if (num <= 5):
                if (row.num == 1):
                    item = "1 {} Potion".format(row.sku)
                else:
                    item = "{} {} Potions".format(row.num, row.sku)
                results.append({
                    "line_item_id": num,
                    "item_sku": item,
                    "customer_name": row.name,
                    "line_item_total": row.cost,
                    "timestamp": row.time,
                })
            num += 1
        if (search_page == ""):
            page = 1
        else:
            page = int(search_page)
        if (page == 1):
            prev = ""
        else:
            prev = "{}".format(page - 1)
        if (num == 7):
            next = "{}".format(page + 1)
        else:
            next = ""
        return {
            "previous": prev,
            "next": next,
            "results": results,
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

