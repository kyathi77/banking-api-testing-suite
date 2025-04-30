import pytest
import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:5000/api"

def test_create_account():
    """Test account creation endpoint"""
    # Arrange
    payload = {
        "name": "John Doe",
        "initial_balance": 1000
    }
    
    # Act
    response = requests.post(f"{BASE_URL}/accounts", json=payload)
    data = response.json()
    
    # Assert
    assert response.status_code == 201
    assert data["name"] == "John Doe"
    assert data["balance"] == 1000
    assert "id" in data
    
    # Return the account id for use in other tests
    return data["id"]

def test_get_account():
    """Test retrieving account details"""
    # Arrange - Create an account first
    account_id = test_create_account()
    
    # Act
    response = requests.get(f"{BASE_URL}/accounts/{account_id}")
    data = response.json()
    
    # Assert
    assert response.status_code == 200
    assert data["name"] == "John Doe"
    assert data["balance"] == 1000
    assert data["id"] == account_id

def test_deposit_money():
    """Test depositing money into an account"""
    # Arrange - Create an account first
    account_id = test_create_account()
    deposit_amount = 500
    
    # Act
    response = requests.post(
        f"{BASE_URL}/accounts/{account_id}/deposit",
        json={"amount": deposit_amount}
    )
    data = response.json()
    
    # Assert
    assert response.status_code == 200
    assert data["message"] == "Deposit successful"
    assert data["new_balance"] == 1500  # 1000 initial + 500 deposit

def test_withdraw_money():
    """Test withdrawing money from an account"""
    # Arrange - Create an account first
    account_id = test_create_account()
    withdraw_amount = 300
    
    # Act
    response = requests.post(
        f"{BASE_URL}/accounts/{account_id}/withdraw",
        json={"amount": withdraw_amount}
    )
    data = response.json()
    
    # Assert
    assert response.status_code == 200
    assert data["message"] == "Withdrawal successful"
    assert data["new_balance"] == 700  # 1000 initial - 300 withdrawal

def test_withdraw_insufficient_funds():
    """Test withdrawal with insufficient funds"""
    # Arrange - Create an account first
    account_id = test_create_account()
    withdraw_amount = 2000  # More than the 1000 initial balance
    
    # Act
    response = requests.post(
        f"{BASE_URL}/accounts/{account_id}/withdraw",
        json={"amount": withdraw_amount}
    )
    data = response.json()
    
    # Assert
    assert response.status_code == 400
    assert "insufficient" in data["error"].lower()

def test_transfer_between_accounts():
    """Test transferring money between accounts"""
    # Arrange - Create two accounts
    source_id = test_create_account()  # Account with 1000 balance
    
    # Create second account with 500 initial balance
    payload = {
        "name": "Jane Smith",
        "initial_balance": 500
    }
    response = requests.post(f"{BASE_URL}/accounts", json=payload)
    destination_id = response.json()["id"]
    
    transfer_amount = 300
    
    # Act
    response = requests.post(
        f"{BASE_URL}/accounts/{source_id}/transfer",
        json={
            "destination_account_id": destination_id,
            "amount": transfer_amount
        }
    )
    data = response.json()
    
    # Assert
    assert response.status_code == 200
    assert data["message"] == "Transfer successful"
    assert data["source_balance"] == 700  # 1000 initial - 300 transfer
    assert data["destination_balance"] == 800  # 500 initial + 300 transfer

def test_close_account():
    """Test closing (deleting) an account"""
    # Arrange - Create an account first
    account_id = test_create_account()
    
    # Act
    response = requests.delete(f"{BASE_URL}/accounts/{account_id}")
    
    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "Account closed successfully"
    
    # Verify account no longer exists
    get_response = requests.get(f"{BASE_URL}/accounts/{account_id}")
    assert get_response.status_code == 404

def test_get_nonexistent_account():
    """Test retrieving a non-existent account"""
    # Act
    response = requests.get(f"{BASE_URL}/accounts/nonexistent-id")
    
    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["error"].lower()