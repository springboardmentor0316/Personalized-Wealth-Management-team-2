<<<<<<< HEAD
# Personalized-Wealth-Management-team-2
This is a digital wealth management platform for planning goals (retirement, home, education), building portfolios, and tracking progress with market-linked updates and simulations
=======
# Wealth Management Authentication System

A complete authentication system with welcome, registration, and login pages for a wealth management platform.

## Features

- **Welcome Page**: Separate buttons for registration and login
- **Registration Page**: User registration with name, email, and password
- **Login Page**: User authentication with email and password
- **Duplicate Registration Check**: Shows popup message if user already registered
- **Modern UI**: Responsive design with gradient backgrounds and smooth animations
- **Backend API**: Node.js server with Express, bcrypt for password hashing, and JWT tokens

## Project Structure

```
d:\infosys\
├── frontend/
│   ├── index.html          # Welcome page
│   ├── register.html       # Registration page
│   ├── login.html          # Login page
│   ├── style.css           # Styles for all pages
│   └── script.js           # Frontend JavaScript
├── backend/
│   ├── server.js           # Node.js server
│   └── package.json        # Backend dependencies
└── README.md               # This file
```

## Setup Instructions

### 1. Install Backend Dependencies

Navigate to the backend directory and install required packages:

```bash
cd backend
npm install
```

### 2. Start the Server

Run the backend server:

```bash
npm start
```

Or for development with auto-restart:

```bash
npm run dev
```

### 3. Access the Application

Open your browser and go to:

```
http://localhost:3000
```

## API Endpoints

- `POST /register` - User registration
- `POST /login` - User login
- `GET /users` - Get all users (debug endpoint)

## Usage

1. **Welcome Page**: Choose between "Register" or "Login"
2. **Registration**: Fill in full name, email, and password
   - If email already exists, shows popup: "You have already registered. Please login."
3. **Login**: Enter email and password
   - Successful login redirects back to welcome page
4. **Navigation**: Use "Back" button to return to welcome page

## Technologies Used

### Frontend
- HTML5
- CSS3 with modern gradients and animations
- Vanilla JavaScript
- Responsive design

### Backend
- Node.js
- Express.js
- bcrypt (password hashing)
- JWT (JSON Web Tokens)
- CORS (Cross-Origin Resource Sharing)

## Security Features

- Password hashing with bcrypt
- JWT token generation for sessions
- Input validation on both frontend and backend
- CORS enabled for secure API access

## Development Notes

- User data is stored in memory (reset on server restart)
- In production, replace with a proper database (MongoDB, PostgreSQL, etc.)
- Change JWT_SECRET in production environment
- Add rate limiting and additional security measures for production
>>>>>>> e10f867 (Initial commit - Wealth Management App)
