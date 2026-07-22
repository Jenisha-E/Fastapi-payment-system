import sqlite3
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()

DB_NAME = "payment_system.db"


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                balance REAL NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT,
                receiver TEXT,
                amount REAL,
                timestamp TEXT
            )
        """)

        # Default fallback user
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO users VALUES ('alice', 1500.0), ('bob', 250.50)"
            )


init_db()


class TransferRequest(BaseModel):
    sender: str
    receiver: str
    amount: float


class NewUserRequest(BaseModel):
    username: str
    starting_balance: float = 0.0


# --- Web Dashboard Route ---


@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Payment Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 30px auto; padding: 20px; background: #f4f6f9; }
            .card { background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            h2 { margin-top: 0; color: #333; }
            input, button { padding: 10px; margin: 5px 0; width: 100%; box-sizing: border-box; }
            button { background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
            button:hover { background: #0056b3; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { padding: 10px; border: 1px solid #ddd; text-align: left; }
            th { background: #007bff; color: white; }
            .success { color: green; font-weight: bold; }
            .error { color: red; font-weight: bold; }
        </style>
    </head>
    <body>

        <h1>💸 Payment System Dashboard</h1>

        <!-- Create New User -->
        <div class="card">
            <h2>Create New Account</h2>
            <input type="text" id="newUsername" placeholder="Enter Username (e.g. john, sara, charlie)">
            <input type="number" id="startingBalance" placeholder="Starting Balance ($) e.g. 500">
            <button onclick="createUser()">Create Account</button>
            <p id="createResult"></p>
        </div>

        <!-- Check Balance -->
        <div class="card">
            <h2>Check Account Balance</h2>
            <input type="text" id="balanceUser" placeholder="Enter ANY Username">
            <button onclick="checkBalance()">Get Balance</button>
            <p id="balanceResult"></p>
        </div>

        <!-- Transfer Money -->
        <div class="card">
            <h2>Make a Transfer</h2>
            <input type="text" id="sender" placeholder="Sender Username (Auto-created with $1000 if new)">
            <input type="text" id="receiver" placeholder="Receiver Username (Auto-created if new)">
            <input type="number" id="amount" placeholder="Amount ($)">
            <button onclick="makeTransfer()">Send Money</button>
            <p id="transferResult"></p>
        </div>

        <!-- Transaction History -->
        <div class="card">
            <h2>Transaction History</h2>
            <input type="text" id="historyUser" placeholder="Enter ANY Username">
            <button onclick="getHistory()">Fetch History</button>
            <div id="historyTableContainer"></div>
        </div>

        <script>
            async function createUser() {
                const username = document.getElementById('newUsername').value;
                const starting_balance = parseFloat(document.getElementById('startingBalance').value) || 0;
                
                const res = await fetch('/users/create', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, starting_balance })
                });
                const data = await res.json();
                const resultEl = document.getElementById('createResult');
                if (res.ok) {
                    resultEl.className = 'success';
                    resultEl.innerText = data.message;
                } else {
                    resultEl.className = 'error';
                    resultEl.innerText = data.detail || 'Failed to create user';
                }
            }

            async function checkBalance() {
                const user = document.getElementById('balanceUser').value;
                const res = await fetch(`/balance/${user}`);
                const data = await res.json();
                const resultEl = document.getElementById('balanceResult');
                if (res.ok) {
                    resultEl.className = 'success';
                    resultEl.innerText = `${data.user}'s Balance: $${data.balance}`;
                } else {
                    resultEl.className = 'error';
                    resultEl.innerText = data.detail || 'User not found';
                }
            }

            async function makeTransfer() {
                const sender = document.getElementById('sender').value;
                const receiver = document.getElementById('receiver').value;
                const amount = parseFloat(document.getElementById('amount').value);
                
                const res = await fetch('/transfer', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ sender, receiver, amount })
                });
                const data = await res.json();
                const resultEl = document.getElementById('transferResult');
                if (res.ok) {
                    resultEl.className = 'success';
                    resultEl.innerText = data.message;
                } else {
                    resultEl.className = 'error';
                    resultEl.innerText = data.detail || 'Transfer failed';
                }
            }

            async function getHistory() {
                const user = document.getElementById('historyUser').value;
                const res = await fetch(`/history/${user}`);
                const data = await res.json();
                const container = document.getElementById('historyTableContainer');
                
                if (res.ok && data.history.length > 0) {
                    let html = '<table><tr><th>ID</th><th>Sender</th><th>Receiver</th><th>Amount</th><th>Time</th></tr>';
                    data.history.forEach(tx => {
                        html += `<tr><td>${tx.id}</td><td>${tx.sender}</td><td>${tx.receiver}</td><td>$${tx.amount}</td><td>${tx.timestamp}</td></tr>`;
                    });
                    html += '</table>';
                    container.innerHTML = html;
                } else if (res.ok) {
                    container.innerHTML = '<p>No transactions found for this user.</p>';
                } else {
                    container.innerHTML = `<p class="error">${data.detail}</p>`;
                }
            }
        </script>

    </body>
    </html>
    """


# --- API Endpoints ---


@app.get("/balance/{username}")
def get_balance(username: str):
    user = username.lower().strip()
    if not user:
        raise HTTPException(status_code=400, detail="Username cannot be empty")

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username, balance FROM users WHERE username = ?", (user,)
        )
        result = cursor.fetchone()

    if result:
        return {
            "user": result["username"],
            "balance": result["balance"],
            "currency": "USD",
        }
    raise HTTPException(status_code=404, detail="User not found")


@app.post("/users/create")
def create_user(data: NewUserRequest):
    user = data.username.lower().strip()
    if not user:
        raise HTTPException(status_code=400, detail="Username cannot be empty")

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE username = ?", (user,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="User already exists!")

        cursor.execute(
            "INSERT INTO users (username, balance) VALUES (?, ?)",
            (user, data.starting_balance),
        )

    return {
        "message": f"User '{user}' created with balance ${data.starting_balance}"
    }


@app.post("/transfer")
def transfer_money(data: TransferRequest):
    sender = data.sender.lower().strip()
    receiver = data.receiver.lower().strip()

    if not sender or not receiver:
        raise HTTPException(
            status_code=400, detail="Sender and Receiver names are required"
        )

    if data.amount <= 0:
        raise HTTPException(
            status_code=400, detail="Transfer amount must be greater than 0"
        )

    if sender == receiver:
        raise HTTPException(
            status_code=400, detail="Cannot transfer money to yourself"
        )

    with get_db() as conn:
        cursor = conn.cursor()

        # 1. Check/Auto-create Sender
        cursor.execute(
            "SELECT balance FROM users WHERE username = ?", (sender,)
        )
        sender_data = cursor.fetchone()
        if not sender_data:
            # Auto-create new sender with $1000 default balance
            cursor.execute(
                "INSERT INTO users (username, balance) VALUES (?, 1000.0)",
                (sender,),
            )
            sender_balance = 1000.0
        else:
            sender_balance = sender_data["balance"]

        if sender_balance < data.amount:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient balance! {sender} only has ${sender_balance}",
            )

        # 2. Check/Auto-create Receiver
        cursor.execute(
            "SELECT balance FROM users WHERE username = ?", (receiver,)
        )
        receiver_data = cursor.fetchone()
        if not receiver_data:
            # Auto-create new receiver with $0 balance
            cursor.execute(
                "INSERT INTO users (username, balance) VALUES (?, 0.0)",
                (receiver,),
            )
            receiver_balance = 0.0
        else:
            receiver_balance = receiver_data["balance"]

        # 3. Perform Transfer
        new_sender_balance = sender_balance - data.amount
        new_receiver_balance = receiver_balance + data.amount
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            "UPDATE users SET balance = ? WHERE username = ?",
            (new_sender_balance, sender),
        )
        cursor.execute(
            "UPDATE users SET balance = ? WHERE username = ?",
            (new_receiver_balance, receiver),
        )
        cursor.execute(
            "INSERT INTO transactions (sender, receiver, amount, timestamp) VALUES (?, ?, ?, ?)",
            (sender, receiver, data.amount, timestamp),
        )

    return {
        "status": "Success",
        "message": f"Transferred ${data.amount} from {sender} to {receiver}",
        "new_sender_balance": new_sender_balance,
        "new_receiver_balance": new_receiver_balance,
    }


@app.get("/history/{username}")
def get_history(username: str):
    user = username.lower().strip()
    if not user:
        raise HTTPException(status_code=400, detail="Username cannot be empty")

    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT username FROM users WHERE username = ?", (user,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="User not found")

        cursor.execute(
            "SELECT id, sender, receiver, amount, timestamp FROM transactions WHERE sender = ? OR receiver = ?",
            (user, user),
        )
        rows = cursor.fetchall()

    history = [dict(row) for row in rows]

    return {
        "user": user,
        "total_transactions": len(history),
        "history": history,
    }