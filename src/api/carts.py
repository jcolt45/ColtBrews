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

class Node:
    def __init__(self, key:str, value:Cart):
        self.key = key
        self.value = value
        self.next = None
  
class HashTable:
    """
    Hash Table based off implemention on geeksforgeeks.org
    """
    def __init__(self, capacity):
        self.capacity = capacity
        self.size = 0
        self.table = [None] * capacity
  
    def _hash(self, key):
        return hash(key) % self.capacity
  
    def insert(self, key, value):
        index = self._hash(key)
  
        if self.table[index] is None:
            self.table[index] = Node(key, value)
            self.size += 1
        else:
            current = self.table[index]
            while current:
                if current.key == key:
                    current.value = value
                    return
                current = current.next
            new_node = Node(key, value)
            new_node.next = self.table[index]
            self.table[index] = new_node
            self.size += 1
  
    def search(self, key):
        index = self._hash(key)
  
        current = self.table[index]
        while current:
            if current.key == key:
                return current.value
            current = current.next
  
        raise KeyError(key)
  
    def remove(self, key):
        index = self._hash(key)
  
        previous = None
        current = self.table[index]
  
        while current:
            if current.key == key:
                if previous:
                    previous.next = current.next
                else:
                    self.table[index] = current.next
                self.size -= 1
                return
            previous = current
            current = current.next
  
        raise KeyError(key)
  
    def __len__(self):
        return self.size
  
    def __contains__(self, key):
        try:
            self.search(key)
            return True
        except KeyError:
            return False

ht = HashTable(100)

class NewCart(BaseModel):
    customer: str

@router.post("/")
def create_cart(new_cart: NewCart):
    """ """
    newC = Cart
    newC.items = []
    newC.quantity = []
    ht.insert(NewCart.customer, newC)
    return {"cart_id": NewCart.customer}


@router.get("/{cart_id}")
def get_cart(cart_id: str):
    """ """
    cart:Cart = ht.search(cart_id)
    return {"items": cart.items, "quantity": cart.quantity}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: str, item_sku: str, cart_item: CartItem):
    """ """
    cart:Cart = ht.search(cart_id)
    cart.items.append(item_sku)
    cart.quantity.append(cart_item.quantity)
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    cart:Cart = ht.search(cart_id)
    index = 0
    cost = 0
    total_potions = 0
    for item in cart.items:
        if item == "RED_POTION_0":
            cart_red_potions = cart.quantity[index]
            total_potions += cart_red_potions
            cost += (50 * cart_red_potions)
        index += 1
    
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        for row in result:
            cur_red_potions = row.num_red_potions
            bank = row.gold
        cur_red_potions -= cart_red_potions
        bank += cost
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = %d" (bank)))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = %d" (cur_red_potions)))

    ht.remove(cart_id)
    return {"total_potions_bought": total_potions, "total_gold_paid": cost}
