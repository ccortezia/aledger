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
    """PostTransaction Command Handler

    Validates and persists a transaction, and submits account entries to the respective
    accounts. The transaction must be uniquely identified and balanced in to be accepted.

    Args:
        cmd (commands.PostTransaction): the command message

    Raises:
        TransactionUnbalanced: when the transaction entries don't balance.
        AccountNotFound: when an entry refers to a non-existent account.
        TransactionAlreadyExists: when a transaction already exists for the given id.
        AccountEntryAlreadyExists: when an entry already exists for a given entry id.

    Returns:
        Transaction: details about the posted transaction.
    """
    txn = Transaction(id=cmd.id, name=cmd.name, entries=cmd.entries)

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
    """RegisterAccount Command Handler

    Attempts to create a new account. An account record must be unique to be accepted.

    Args:
        cmd (commands.RegisterAccount): the command message

    Raises:
        AccountAlreadyExists: when an account already exists for the given id.
        AccountNameAlreadyExists: when an account with the given name already exists.

    Returns:
        AccountView: details about the created account
    """
    account = Account(id=cmd.id, name=cmd.name, direction=cmd.direction)
    ACCOUNTS_REPOSITORY.add(account)
    return AccountView(
        id=account.id,
        name=account.name,
        direction=account.direction,
        balance=0,
    )
