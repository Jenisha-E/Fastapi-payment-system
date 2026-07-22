# 💸 FastAPI Payment System Dashboard

A full-stack payment and mini-banking microservice built with **Python**, **FastAPI**, **SQLite**, and an **interactive HTML/JS frontend**.

This system allows users to create accounts, check real-time balances, perform atomic money transfers between accounts, and view transaction history logs.

---

## ✨ Features

* **⚡ Auto-Account Creation:** Automatically provisions new user accounts on-the-fly during transfers.
* **🔒 Transaction Safety:** SQLite database transactions ensure safe, consistent fund transfers without data corruption.
* **📜 Transaction History:** Tracks all incoming and outgoing payments with timestamps.
* **🖥️ Web Dashboard:** An integrated, simple user interface served directly from FastAPI at `http://127.0.0.1:8000/`.
* **📖 Interactive API Docs:** Auto-generated OpenAPI/Swagger documentation available at `http://127.0.0.1:8000/docs`.

---

## 🛠️ Tech Stack

* **Backend:** Python, FastAPI, Uvicorn, Pydantic
* **Database:** SQLite
* **Frontend:** HTML5, CSS3, JavaScript (Fetch API)

---

## 🚀 How to Run Locally

### 1. Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/fastapi-payment-system.git](https://github.com/YOUR_USERNAME/fastapi-payment-system.git)
cd fastapi-payment-system
