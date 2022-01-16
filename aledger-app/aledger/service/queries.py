import uuid
from aledger.adapters import ACCOUNTS_REPOSITORY
from aledger.exceptions import AccountNotFound
from .views import AccountView


def retrieve_account(account_id: uuid.UUID) -> AccountView:

    # NOTE: data could be retrieved directly from storage, it could skip the repository.
    account = ACCOUNTS_REPOSITORY.get(account_id)
    if not account:
        raise AccountNotFound()

    # NOTE: balance calculation would normally be deferred to SQL storage.
    balance = sum(
        [
            entry.amount * (-1 if entry.direction != account.direction else 1)
            for entry in account.entries
        ]
    )

    return AccountView(
        id=account.id,
        name=account.name,
        direction=account.direction,
        balance=balance,
    )