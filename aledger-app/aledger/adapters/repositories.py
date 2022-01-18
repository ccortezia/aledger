import uuid
from aledger.domain.models import Transaction, Account
from aledger.exceptions import (
    TransactionAlreadyExists,
    AccountNotFound,
    AccountAlreadyExists,
    AccountNameAlreadyExists,
    AccountEntryAlreadyExists,
)


class InMemoryTransactionRepository:

    _data: list[Transaction] = []
    _ids: set[uuid.UUID] = set()

    def add(self, txn: Transaction) -> None:
        # Prevent claimed transaction ids from being reused.
        if txn.id in self._ids:
            raise TransactionAlreadyExists(txn.id)

        # Update main repository and indexes.
        self._data.append(txn)
        self._ids.add(txn.id)

    def clear(self) -> None:
        self._data = []
        self._ids = set()


class InMemoryAccountRepository:

    _data: dict[uuid.UUID, Account] = {}
    _entry_ids: set[uuid.UUID] = set()
    _acc_names: set[str] = set()

    def add(self, account: Account) -> None:
        # Prevent claimed account ids from being reused.
        if self.exists(account.id):
            raise AccountAlreadyExists(account.id)

        # Prevent repeated entries from being added.
        set_entry_ids = set([entry.id for entry in account.entries])
        repeated_entry_ids = set_entry_ids & self._entry_ids
        if repeated_entry_ids:
            raise AccountEntryAlreadyExists(repeated_entry_ids)

        # Prevent claimed account names from being reused.
        if account.name in self._acc_names:
            raise AccountNameAlreadyExists(account.name)

        # Update main repository and indexes.
        self._data[account.id] = account
        self._entry_ids.update(set_entry_ids)
        self._acc_names.add(account.name)

    def update(self, account: Account) -> None:
        current_account = self.get(account.id)

        # Prevent repeated entries from being added.
        set_entry_ids = set([entry.id for entry in account.entries])
        old_entry_ids = set([entry.id for entry in current_account.entries])
        new_entry_ids = set_entry_ids - old_entry_ids
        repeated_entry_ids = new_entry_ids & self._entry_ids
        if repeated_entry_ids:
            raise AccountEntryAlreadyExists(repeated_entry_ids)

        # Prevent claimed account names from being reused.
        if account.name != current_account.name:  # type: ignore
            if account.name in self._acc_names:
                raise AccountNameAlreadyExists(account.name)

        # Update main repository and indexes.
        self._acc_names.add(account.name)
        self._entry_ids.update(set_entry_ids)
        self._data[account.id] = account

    def get(self, account_id: uuid.UUID) -> Account:
        record = self._data.get(account_id)
        if not record:
            raise AccountNotFound()
        return record and record.copy(deep=True)

    def exists(self, account_id: uuid.UUID) -> bool:
        return account_id in self._data

    def clear(self) -> None:
        self._data = {}
        self._acc_names = set()
        self._entry_ids = set()


# NOTE: temporary in-memory storage.
ACCOUNTS_REPOSITORY = InMemoryAccountRepository()
TRANSACTIONS_REPOSITORY = InMemoryTransactionRepository()
