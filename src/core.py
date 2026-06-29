import asyncio
import database


async def add_transaction_async(user_id: int, transaction_type: str, value_float: int, description: str) -> None:
    value_cents = int(round(value_float*100))
    await asyncio.to_thread(database.create_transaction, user_id, transaction_type, value_cents, description)


async def get_balance_async(user_id: int) -> float:
    value_cents = await asyncio.to_thread(database.get_balance, user_id)
    return value_cents/100


async def get_transactions_async(user_id: int, limit: int = 10) -> list:
    return await asyncio.to_thread(database.get_transactions, user_id, limit)


async def delete_transaction_async(user_id: int, transaction_id: int) -> bool:
    return await asyncio.to_thread(database.delete_transaction, transaction_id, user_id)