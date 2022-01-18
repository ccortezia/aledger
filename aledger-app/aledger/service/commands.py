from aledger.domain import commands
from aledger.domain import Account, Transaction
from aledger.adapters import ACCOUNTS_REPOSITORY, TRANSACTIONS_REPOSITORY
from .views import AccountView

from aledger.exceptions import (
    TransactionUnbalanced,
)


__all__ = [
    "post_transaction",
    "register_account",
]


def post_transaction(cmd: commands.PostTransaction) -> Transaction:
    txn = Transaction(id=cmd.id, entries=cmd.entries)

    # Verifies the transaction's health before posting.
    if not txn.is_balanced:
        raise TransactionUnbalanced()

    # Adds the transaction's entries to the respective accounts.
    for entry in txn.entries:
        account = ACCOUNTS_REPOSITORY.get(entry.account_id)
        account.add_entry(entry.direction, entry.amount, id=entry.id)
        ACCOUNTS_REPOSITORY.update(account)

    # Saves the posted transaction to storage.
    TRANSACTIONS_REPOSITORY.add(txn)

    return txn


def register_account(cmd: commands.RegisterAccount) -> AccountView:
    account = Account(id=cmd.id, name=cmd.name, direction=cmd.direction)
    ACCOUNTS_REPOSITORY.add(account)
    return AccountView(
        id=account.id,
        name=account.name,
        direction=account.direction,
        balance=0,
    )
