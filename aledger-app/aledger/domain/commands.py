import uuid
from typing import Optional
from .models import Direction, AccountEntry
from pydantic.types import constr
from pydantic import BaseModel, Field


class Command(BaseModel):
    pass


class RegisterAccount(Command):
    name: constr(strip_whitespace=True, min_length=3, max_length=35)  # type: ignore
    direction: Direction
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4)


class PostTransaction(Command):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4)
    entries: list[AccountEntry] = Field(default_factory=list)
