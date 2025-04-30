from flask import Flask, jsonify, request
import uuid

app = Flask(__name__)

# In-memory database for demo purposes
accounts = {}

@app.route('/api/accounts', methods=['POST'])
def create_account():
    """Create a new bank account"""
    data = request.get_json()
    name = data.get('name')
    initial_balance = data.get('initial_balance', 0)
    
    if not name:
        return jsonify({"error": "Name is required"}), 400
    
    account_id = str(uuid.uuid4())
    accounts[account_id] = {
        "id": account_id,
        "name": name,
        "balance": float(initial_balance)
    }
    
    return jsonify(accounts[account_id]), 201

@app.route('/api/accounts/<account_id>', methods=['GET'])
def get_account(account_id):
    """Get account details"""
    if account_id not in accounts:
        return jsonify({"error": "Account not found"}), 404
    
    return jsonify(accounts[account_id])

@app.route('/api/accounts/<account_id>/deposit', methods=['POST'])
def deposit(account_id):
    """Deposit money into an account"""
    if account_id not in accounts:
        return jsonify({"error": "Account not found"}), 404
    
    data = request.get_json()
    amount = data.get('amount')
    
    if not amount or float(amount) <= 0:
        return jsonify({"error": "Valid positive amount required"}), 400
    
    accounts[account_id]["balance"] += float(amount)
    
    return jsonify({
        "message": "Deposit successful",
        "new_balance": accounts[account_id]["balance"]
    })

@app.route('/api/accounts/<account_id>/withdraw', methods=['POST'])
def withdraw(account_id):
    """Withdraw money from an account"""
    if account_id not in accounts:
        return jsonify({"error": "Account not found"}), 404
    
    data = request.get_json()
    amount = data.get('amount')
    
    if not amount or float(amount) <= 0:
        return jsonify({"error": "Valid positive amount required"}), 400
    
    if accounts[account_id]["balance"] < float(amount):
        return jsonify({"error": "Insufficient funds"}), 400
    
    accounts[account_id]["balance"] -= float(amount)
    
    return jsonify({
        "message": "Withdrawal successful",
        "new_balance": accounts[account_id]["balance"]
    })

@app.route('/api/accounts/<account_id>/transfer', methods=['POST'])
def transfer(account_id):
    """Transfer money between accounts"""
    if account_id not in accounts:
        return jsonify({"error": "Source account not found"}), 404
    
    data = request.get_json()
    destination_id = data.get('destination_account_id')
    amount = data.get('amount')
    
    if not destination_id or destination_id not in accounts:
        return jsonify({"error": "Destination account not found"}), 404
    
    if not amount or float(amount) <= 0:
        return jsonify({"error": "Valid positive amount required"}), 400
    
    if accounts[account_id]["balance"] < float(amount):
        return jsonify({"error": "Insufficient funds"}), 400
    
    accounts[account_id]["balance"] -= float(amount)
    accounts[destination_id]["balance"] += float(amount)
    
    return jsonify({
        "message": "Transfer successful",
        "source_balance": accounts[account_id]["balance"],
        "destination_balance": accounts[destination_id]["balance"]
    })

@app.route('/api/accounts/<account_id>', methods=['DELETE'])
def close_account(account_id):
    """Close a bank account (delete it)"""
    if account_id not in accounts:
        return jsonify({"error": "Account not found"}), 404
    
    del accounts[account_id]
    
    return jsonify({"message": "Account closed successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)