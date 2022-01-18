import uuid
from fastapi import FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from aledger.domain import models
from aledger.domain import commands
import aledger.exceptions
import aledger.service

app = FastAPI()


# -------------------------------------------------------------------------------------
# HTTP API Controller Endpoints
# -------------------------------------------------------------------------------------


@app.post("/account", response_model=aledger.service.AccountView)
def register_account(command: commands.RegisterAccount):
    try:
        account = aledger.service.register_account(command)
    except aledger.exceptions.AccountAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="account already exists"
        )
    except aledger.exceptions.AccountNameAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="account with the specified name already exists",
        )
    return account


@app.get("/account/{account_id}", response_model=aledger.service.AccountView)
def retrieve_account(account_id: uuid.UUID):
    try:
        return aledger.service.retrieve_account(account_id)
    except aledger.exceptions.AccountNotFound:
        raise HTTPException(status_code=404)


@app.post("/transaction", response_model=models.Transaction)
def post_transaction(command: commands.PostTransaction):
    try:
        transaction = aledger.service.post_transaction(command)
    except aledger.exceptions.AccountNotFound:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="account not found")
    except aledger.exceptions.TransactionUnbalanced:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="unbalanced transaction"
        )
    except aledger.exceptions.TransactionAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="transaction already exists"
        )
    except aledger.exceptions.AccountEntryAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="transaction entry with the specified id already exists",
        )
    return transaction


# -------------------------------------------------------------------------------------
# Error Response Normalization
# -------------------------------------------------------------------------------------


@app.exception_handler(HTTPException)
async def exception_handler(request, exc):
    if exc.status_code == status.HTTP_400_BAD_REQUEST:
        return JSONResponse(
            jsonable_encoder({"error": "error.application_error", "detail": exc.detail}),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return JSONResponse(
        jsonable_encoder({"error": "error.generic_error", "detail": exc.detail}),
        status_code=exc.status_code,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        jsonable_encoder({"error": "error.field_validation_failure", "detail": exc.errors()}),
        status_code=status.HTTP_400_BAD_REQUEST,
    )
