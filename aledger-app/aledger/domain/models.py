import enum
import uuid
from pydantic import BaseModel, Field, PositiveInt
from pydantic.types import constr
from aledger.exceptions import AccountEntryAlreadyExists


class Direction(enum.Enum):
    CREDIT = "credit"
    DEBIT = "debit"


class AccountEntry(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    account_id: uuid.UUID
    direction: Direction
    amount: PositiveInt


class Account(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: constr(strip_whitespace=True, min_length=3, max_length=35)  # type: ignore
    direction: Direction
    entries: list[AccountEntry] = Field(default_factory=list)

    def add_entry(self, direction, amount, id=None):
        if id and id in [entry.id for entry in self.entries]:
            raise AccountEntryAlreadyExists()
        self.entries.append(
            AccountEntry(
                id=id,
                account_id=self.id,
                direction=direction,
                amount=amount,
            )
        )


class Transaction(BaseModel):
    id: uuid.UUID
    entries: list[AccountEntry]

    @property
    def is_balanced(self):
        credits = [entry.amount for entry in self.entries if entry.direction == Direction.CREDIT]
        debits = [entry.amount for entry in self.entries if entry.direction == Direction.DEBIT]
        return sum(debits) - sum(credits) == 0