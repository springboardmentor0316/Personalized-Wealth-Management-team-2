# Personalized Wealth Management System

## Overview

The Personalized Wealth Management System is a full-stack web application designed to help users plan financial goals, manage investments, and track portfolio performance. The platform provides secure authentication along with goal tracking and portfolio management features.

This project demonstrates a modern full-stack architecture with a separate frontend and backend.

---

## Tech Stack

### Frontend

* React
* TypeScript
* Tailwind CSS
* Axios
* React Router

### Backend

* FastAPI (Python)
* SQLAlchemy ORM
* Pydantic
* JWT Authentication

### Database

* PostgreSQL

---

## Features

### Authentication System

* User Registration
* User Login
* Secure Password Hashing
* JWT Token Authentication
* Protected API Routes

### Goal Management

Users can create and track financial goals such as:

* Retirement planning
* Buying a house
* Education savings

Each goal includes:

* Target amount
* Target date
* Monthly contribution

The system calculates progress automatically.

### Investment Management

Users can manage investments including:

* Adding investments
* Updating investment details
* Tracking cost basis
* Monitoring current value

### Transactions

Users can record financial transactions:

* Buy assets
* Sell assets
* Track transaction history

### Portfolio Dashboard

The portfolio dashboard displays:

* Total portfolio value
* Cost basis
* Profit or loss
* Asset allocation
* Individual investment positions

---

## Project Structure

```
Personalized-Wealth-Management-team-2
│
├── backend
│   ├── main.py
│   ├── database.py
│   ├── config.py
│   ├── models
│   ├── routers
│   │   ├── auth_router.py
│   │   ├── goals_router.py
│   │   ├── investments_router.py
│   │   └── transactions_router.py
│   └── schemas
│
├── frontend
│   ├── index.html
│   └── src
│       ├── pages
│       │   ├── LoginPage.tsx
│       │   ├── RegisterPage.tsx
│       │   ├── GoalsPage.tsx
│       │   └── PortfolioPage.tsx
│       ├── components
│       └── services
│
├── README.md
└── .gitignore
```

---

## Backend Setup

1. Navigate to backend folder

```
cd backend
```

2. Install dependencies

```
pip install -r requirements.txt
```

3. Create `.env` file

```
DATABASE_URL=postgresql://username:password@localhost:5432/wealthdb
SECRET_KEY=your_secret_key
ALGORITHM=HS256
```

4. Start the backend server

```
uvicorn main:app --reload
```

Backend runs at:

```
http://127.0.0.1:8000
```

API documentation available at:

```
http://127.0.0.1:8000/docs
```

---

## Frontend Setup

1. Navigate to frontend folder

```
cd frontend
```

2. Install dependencies

```
npm install
```

3. Run the frontend

```
npm run dev
```

Frontend runs at:

```
http://localhost:5173
```

---

## Expected Output

After running the application, users can:

* Register a new account
* Login securely
* Create financial goals
* Track goal progress
* Add investments
* Record transactions
* View portfolio performance

All user data is stored securely in the database.


## Future Improvements

* Real-time stock price integration
* Advanced portfolio analytics
* Financial risk analysis
* Mobile responsive UI improvements
