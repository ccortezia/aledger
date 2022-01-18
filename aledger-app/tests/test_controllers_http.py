import uuid
import pytest
from fastapi.testclient import TestClient
from aledger.adapters import ACCOUNTS_REPOSITORY, TRANSACTIONS_REPOSITORY
from aledger.controllers.http import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_data_at_setup():
    ACCOUNTS_REPOSITORY.clear()
    TRANSACTIONS_REPOSITORY.clear()


# --------------------------------------------------------------------------------------
# Test /accounts endpoints
# --------------------------------------------------------------------------------------


def test_register_account_should_persist_account_record():
    id = str(uuid.uuid4())

    # Registers Account.
    body = {"id": id, "name": "cash", "direction": "debit"}
    response = client.post("/account", json=body)
    assert response.status_code == 200
    assert response.json() == {
        "id": id,
        "name": "cash",
        "direction": "debit",
        "balance": 0,
    }

    # Retrieves Account.
    response = client.get(f"/account/{id}")
    assert response.status_code == 200
    assert response.json() == {
        "id": id,
        "name": "cash",
        "direction": "debit",
        "balance": 0,
    }


def test_register_account_with_missing_id_should_create_id_automatically():

    # Registers an Account with a missing id.
    body = {"name": "cash", "direction": "debit"}
    response = client.post("/account", json=body)
    assert response.status_code == 200

    # Verify an id has been automatically created.
    generated_id = response.json()["id"]

    # Retrieves Account.
    response = client.get(f"/account/{generated_id}")
    assert response.status_code == 200
    assert response.json() == {
        "id": generated_id,
        "name": "cash",
        "direction": "debit",
        "balance": 0,
    }


def test_register_account_with_invalid_direction_field_should_error_out():
    body = {"name": "cash", "direction": "unknown"}
    response = client.post("/account", json=body)
    assert response.status_code == 400


def test_register_account_with_repeated_id_should_error_out():
    id = str(uuid.uuid4())

    # Registers Account.
    body = {"id": id, "name": "cash", "direction": "debit"}
    response = client.post("/account", json=body)
    assert response.status_code == 200

    # Attempts to re-register the Account.
    body = {"id": id, "name": "cash", "direction": "debit"}
    response = client.post("/account", json=body)
    assert response.status_code == 400


def test_register_account_with_repeated_name_should_error_out():
    # Registers Account.
    body = {"name": "cash", "direction": "debit"}
    response = client.post("/account", json=body)
    assert response.status_code == 200

    # Attempts to re-register the Account.
    body = {"name": "cash", "direction": "debit"}
    response = client.post("/account", json=body)
    assert response.status_code == 400


def test_register_account_with_empty_name_should_error_out():
    # Attempts to Register an Account with empty name.
    body = {"name": "", "direction": "debit"}
    response = client.post("/account", json=body)
    assert response.status_code == 400


def test_retrieve_account_with_unknown_account_id_should_error_out():
    response = client.get(f"/account/{uuid.uuid4()}")
    assert response.status_code == 404


def test_post_transaction_with_invalid_entry_should_error_out():
    broken_entry = {"amount": 100, "direction": "debit"}
    body = {"id": str(uuid.uuid4()), "entries": [broken_entry]}
    response = client.post("/transaction", json=body)
    assert response.status_code == 400


def test_post_transaction_with_unknown_accounts_should_error_out():
    entry_1 = {"account_id": str(uuid.uuid4()), "amount": 100, "direction": "debit"}
    entry_2 = {"account_id": str(uuid.uuid4()), "amount": 100, "direction": "credit"}
    body = {"id": str(uuid.uuid4()), "entries": [entry_1, entry_2]}
    response = client.post("/transaction", json=body)
    assert response.status_code == 400


def test_post_transaction_with_unbalanced_entries_should_error_out():
    entry_1 = {"account_id": str(uuid.uuid4()), "amount": 101, "direction": "debit"}
    entry_2 = {"account_id": str(uuid.uuid4()), "amount": 100, "direction": "credit"}
    body = {"id": str(uuid.uuid4()), "entries": [entry_1, entry_2]}
    response = client.post("/transaction", json=body)
    assert response.status_code == 400


# --------------------------------------------------------------------------------------
# Test /transactions endpoints
# --------------------------------------------------------------------------------------


@pytest.fixture
def furniture_acc():
    body = {"id": str(uuid.uuid4()), "name": "furniture", "direction": "debit"}
    response = client.post("/account", json=body)
    return response.json()


@pytest.fixture
def petty_cash_acc():
    body = {"id": str(uuid.uuid4()), "name": "petty-cash", "direction": "debit"}
    response = client.post("/account", json=body)
    return response.json()


@pytest.fixture
def bank_loan_acc():
    body = {"id": str(uuid.uuid4()), "name": "bank-loan", "direction": "credit"}
    response = client.post("/account", json=body)
    return response.json()


def test_post_transaction_with_two_legs_should_update_account_balances(
    furniture_acc, petty_cash_acc
):
    furniture_acc_id = furniture_acc["id"]
    petty_cash_acc_id = petty_cash_acc["id"]

    # Post a transaction: use petty cash to buy furniture.
    entry_1 = {
        "id": str(uuid.uuid4()),
        "account_id": furniture_acc_id,
        "amount": 15000,
        "direction": "debit",
    }
    entry_2 = {
        "id": str(uuid.uuid4()),
        "account_id": petty_cash_acc_id,
        "amount": 15000,
        "direction": "credit",
    }
    body = {"id": str(uuid.uuid4()), "entries": [entry_1, entry_2]}
    response = client.post("/transaction", json=body)
    assert response.status_code == 200
    assert response.json() == {
        "id": body["id"],
        "entries": [
            {
                "id": entry_1["id"],
                "account_id": entry_1["account_id"],
                "direction": "debit",
                "amount": 15000,
            },
            {
                "id": entry_2["id"],
                "account_id": entry_2["account_id"],
                "direction": "credit",
                "amount": 15000,
            },
        ],
    }

    # Verify furniture balance increased.
    response = client.get(f"/account/{furniture_acc_id}")
    assert response.status_code == 200
    assert response.json()["balance"] == 15000

    # Verify petty-cash balance decreased.
    response = client.get(f"/account/{petty_cash_acc_id}")
    assert response.status_code == 200
    assert response.json()["balance"] == -15000


def test_post_transaction_with_three_legs_should_update_account_balances(
    furniture_acc, petty_cash_acc, bank_loan_acc
):
    furniture_acc_id = furniture_acc["id"]
    petty_cash_acc_id = petty_cash_acc["id"]
    bank_loan_acc_id = bank_loan_acc["id"]

    # Post a transaction: take a loan to buy a table and to replenish the petty cash.
    entry_1 = {
        "id": str(uuid.uuid4()),
        "account_id": furniture_acc_id,
        "amount": 250000,
        "direction": "debit",
    }
    entry_2 = {
        "id": str(uuid.uuid4()),
        "account_id": petty_cash_acc_id,
        "amount": 50000,
        "direction": "debit",
    }
    entry_3 = {
        "id": str(uuid.uuid4()),
        "account_id": bank_loan_acc_id,
        "amount": 300000,
        "direction": "credit",
    }
    body = {"id": str(uuid.uuid4()), "entries": [entry_1, entry_2, entry_3]}
    response = client.post("/transaction", json=body)
    assert response.status_code == 200
    assert response.json() == {
        "id": body["id"],
        "entries": [
            {
                "id": entry_1["id"],
                "account_id": entry_1["account_id"],
                "direction": "debit",
                "amount": 250000,
            },
            {
                "id": entry_2["id"],
                "account_id": entry_2["account_id"],
                "direction": "debit",
                "amount": 50000,
            },
            {
                "id": entry_3["id"],
                "account_id": entry_3["account_id"],
                "direction": "credit",
                "amount": 300000,
            },
        ],
    }

    # Verify furniture balance increased.
    response = client.get(f"/account/{furniture_acc_id}")
    assert response.status_code == 200
    assert response.json()["balance"] == 250000

    # Verify petty-cash balance increased.
    response = client.get(f"/account/{petty_cash_acc_id}")
    assert response.status_code == 200
    assert response.json()["balance"] == 50000

    # Verify bank loan balance increased.
    response = client.get(f"/account/{bank_loan_acc_id}")
    assert response.status_code == 200
    assert response.json()["balance"] == 300000


def test_post_transaction_with_missing_id_should_create_id_automatically(
    furniture_acc, petty_cash_acc
):
    furniture_acc_id = furniture_acc["id"]
    petty_cash_acc_id = petty_cash_acc["id"]

    # Post a transaction with a missing transaction id.
    entry_1 = {"account_id": furniture_acc_id, "amount": 15000, "direction": "debit"}
    entry_2 = {"account_id": petty_cash_acc_id, "amount": 15000, "direction": "credit"}
    body = {"entries": [entry_1, entry_2]}
    response = client.post("/transaction", json=body)
    assert response.status_code == 200

    # Verify an id has been automatically created.
    assert response.json()["id"]
    assert response.json()["entries"][0]["id"]
    assert response.json()["entries"][1]["id"]


def test_post_transaction_with_amount_0_should_error_out(furniture_acc, petty_cash_acc):
    furniture_acc_id = furniture_acc["id"]
    petty_cash_acc_id = petty_cash_acc["id"]

    # Post a transaction with a missing transaction id.
    entry_1 = {"account_id": furniture_acc_id, "amount": 0, "direction": "debit"}
    entry_2 = {"account_id": petty_cash_acc_id, "amount": 0, "direction": "credit"}
    body = {"entries": [entry_1, entry_2]}
    response = client.post("/transaction", json=body)
    assert response.status_code == 400


def test_post_transaction_with_negative_amount_should_error_out(furniture_acc, petty_cash_acc):
    furniture_acc_id = furniture_acc["id"]
    petty_cash_acc_id = petty_cash_acc["id"]

    # Post a transaction with a missing transaction id.
    entry_1 = {"account_id": furniture_acc_id, "amount": -1000, "direction": "debit"}
    entry_2 = {"account_id": petty_cash_acc_id, "amount": -1000, "direction": "credit"}
    body = {"entries": [entry_1, entry_2]}
    response = client.post("/transaction", json=body)
    assert response.status_code == 400


def test_post_transaction_with_repeated_transaction_id_should_error_out(
    furniture_acc, petty_cash_acc
):
    furniture_acc_id = furniture_acc["id"]
    petty_cash_acc_id = petty_cash_acc["id"]

    txn_id = str(uuid.uuid4())

    # Post a transaction.
    entry_1 = {"account_id": furniture_acc_id, "amount": 15000, "direction": "debit"}
    entry_2 = {"account_id": petty_cash_acc_id, "amount": 15000, "direction": "credit"}
    body = {"id": txn_id, "entries": [entry_1, entry_2]}
    response = client.post("/transaction", json=body)
    assert response.status_code == 200

    # Post a transaction re-using the previous transaction id.
    entry_1 = {"account_id": furniture_acc_id, "amount": 15000, "direction": "debit"}
    entry_2 = {"account_id": petty_cash_acc_id, "amount": 15000, "direction": "credit"}
    body = {"id": txn_id, "entries": [entry_1, entry_2]}
    response = client.post("/transaction", json=body)
    assert response.status_code == 400


def test_post_transaction_with_repeated_entry_id_should_error_out(furniture_acc, petty_cash_acc):
    furniture_acc_id = furniture_acc["id"]
    petty_cash_acc_id = petty_cash_acc["id"]

    common_id = str(uuid.uuid4())

    # Post a transaction with repeated ids.
    entry_1 = {
        "id": common_id,
        "account_id": furniture_acc_id,
        "amount": 10,
        "direction": "debit",
    }
    entry_2 = {
        "id": common_id,
        "account_id": petty_cash_acc_id,
        "amount": 10,
        "direction": "credit",
    }
    body = {"entries": [entry_1, entry_2]}
    response = client.post("/transaction", json=body)
    assert response.status_code == 400


def test_post_transaction_with_repeated_entry_id_from_prior_transaction_should_error_out(
    furniture_acc, petty_cash_acc
):
    furniture_acc_id = furniture_acc["id"]
    petty_cash_acc_id = petty_cash_acc["id"]

    # Post a valid transaction.
    entry_1 = {
        "id": str(uuid.uuid4()),
        "account_id": furniture_acc_id,
        "amount": 10,
        "direction": "debit",
    }
    entry_2 = {
        "id": str(uuid.uuid4()),
        "account_id": petty_cash_acc_id,
        "amount": 10,
        "direction": "credit",
    }
    body = {"entries": [entry_1, entry_2]}
    response = client.post("/transaction", json=body)
    assert response.status_code == 200

    # Post a transaction with an entry that has an id used in a prior transaction.
    entry_1 = {
        "id": entry_1["id"],
        "account_id": furniture_acc_id,
        "amount": 10,
        "direction": "debit",
    }
    entry_2 = {
        "id": str(uuid.uuid4()),
        "account_id": petty_cash_acc_id,
        "amount": 10,
        "direction": "credit",
    }
    body = {"entries": [entry_1, entry_2]}
    response = client.post("/transaction", json=body)
    assert response.status_code == 400
