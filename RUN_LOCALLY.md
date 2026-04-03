# How to Run the Wealth Management Application Locally

## Prerequisites
- Python 3.11+ installed
- Node.js 16+ and npm installed
- Git installed

## Step-by-Step Setup Guide

### 1. Backend Setup

#### 1.1 Navigate to Backend Directory
```bash
cd d:\infosys\backend
```

#### 1.2 Create Virtual Environment (if not exists)
```bash
python -m venv venv
```

#### 1.3 Activate Virtual Environment
```bash
venv\Scripts\activate
```

#### 1.4 Install Dependencies
```bash
pip install -r requirements.txt
```

#### 1.5 Install Critical Dependencies (if requirements.txt fails)
```bash
pip install fastapi uvicorn sqlalchemy passlib bcrypt==4.0.1 python-jose[cryptography] python-dotenv email-validator
```

#### 1.6 Start Backend Server
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

**Backend will be available at:** http://localhost:8001
**API Documentation:** http://localhost:8001/docs

### 2. Frontend Setup

#### 2.1 Open New Terminal/CMD Window
Keep the backend running in the first terminal.

#### 2.2 Navigate to Frontend Directory
```bash
cd d:\infosys\frontend
```

#### 2.3 Install Dependencies
```bash
npm install
```

#### 2.4 Start Frontend Development Server
```bash
npm start
```

**Frontend will be available at:** http://localhost:3000
*(If port 3000 is busy, it will automatically use 3001)*

## Troubleshooting Common Issues

### Issue 1: Backend fails to start with bcrypt error
**Solution:** Install correct bcrypt version
```bash
pip install bcrypt==4.0.1
```

### Issue 2: Frontend shows "Network Error"
**Solution:** 
1. Ensure backend is running on port 8001
2. Check API_BASE_URL in `frontend/src/services/api.ts` is `http://localhost:8001/api`
3. Check browser console for CORS errors

### Issue 3: Registration/Login fails
**Solution:**
1. Delete the database file: `del d:\infosys\backend\wealth_management.db`
2. Restart backend
3. Try registering again

### Issue 4: Port already in use
**Solution:**
- For backend: Use different port: `python -m uvicorn main:app --port 8002`
- For frontend: It will automatically find next available port

### Issue 5: Virtual environment not activating
**Solution:**
```bash
# Try full path
d:\infosys\backend\venv\Scripts\activate
```

## Verification Steps

### 1. Test Backend API
Open browser and go to: http://localhost:8001/docs
You should see the FastAPI interactive documentation.

### 2. Test Frontend
Open browser and go to: http://localhost:3000 (or 3001)
You should see the login/register page.

### 3. Test Registration
1. Register with: demo@example.com / password123
2. Should redirect to dashboard
3. Should see the new dark sidebar with light blue background

## Quick Start Commands (Copy & Paste)

### Terminal 1 - Backend:
```bash
cd d:\infosys\backend
venv\Scripts\activate
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### Terminal 2 - Frontend:
```bash
cd d:\infosys\frontend
npm start
```

## Application Features Ready for Demo

✅ **Milestone 1: Authentication**
- User registration with password hashing
- JWT token-based login
- Protected routes
- Automatic redirects

✅ **Milestone 2: User Management**
- User profile display and updates
- Risk profile selection
- KYC status tracking
- Profile management

✅ **UI Enhancements**
- Dark gradient sidebar
- Light blue main background
- Modern glass morphism effects
- Smooth animations and transitions

## Default Test User
After first run, you can register with:
- **Email:** demo@example.com
- **Password:** password123
- **Name:** Demo User
- **Risk Profile:** Moderate

This will create a complete user profile for testing all features.
