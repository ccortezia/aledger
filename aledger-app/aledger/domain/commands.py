import uuid
from typing import Optional
from .models import Direction, AccountEntry, Label
from pydantic import BaseModel, Field


class Command(BaseModel):
    pass


class RegisterAccount(Command):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4)
    name: Optional[Label] = Field(default_factory=lambda: "acc")  # type: ignore
    direction: Direction


class PostTransaction(Command):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4)
    name: Optional[Label] = Field(default_factory=lambda: "txn")  # type: ignore
    entries: list[AccountEntry] = Field(default_factory=list)
