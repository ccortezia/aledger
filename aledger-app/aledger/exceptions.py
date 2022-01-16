class AledgerException(Exception):
    pass


class TransactionAlreadyExists(AledgerException):
    pass


class TransactionUnbalanced(AledgerException):
    pass


class AccountNotFound(AledgerException):
    pass


class AccountAlreadyExists(AledgerException):
    pass


class AccountNameAlreadyExists(AledgerException):
    pass


class AccountEntryAlreadyExists(AledgerException):
    pass
