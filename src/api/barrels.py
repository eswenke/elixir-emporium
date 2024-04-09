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

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    t = sqlalchemy.text("UPDATE global_inventory SET num_green_ml = num_green_ml + :ml, gold = gold - :price")
    ml = 0
    price = 0
    for barrel in barrels_delivered:
        ml += barrel.ml_per_barrel * barrel.quantity
        price += barrel.price * barrel.quantity
        with db.engine.begin() as connection:
            connection.execute(t, ml=ml, price=price)

    
    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).scalar_one()

    return [
        {
            "sku": "SMALL_GREEN_BARREL",
            "quantity": 1 if result < 10 else 0,
        }
    ]

