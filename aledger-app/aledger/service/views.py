import uuid
from pydantic import BaseModel
from aledger.domain import Direction


class AccountView(BaseModel):
    id: uuid.UUID
    name: str
    direction: Direction
    balance: int
