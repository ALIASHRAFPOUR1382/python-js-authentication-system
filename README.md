# 🔐 Python & JavaScript Authentication System

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-yellow.svg)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A complete authentication system built with raw Python (no framework) for the backend and JavaScript/HTML/CSS for the frontend. This project includes user registration, login, OTP verification, session management, and a modern UI with RTL support.

## ✨ Features

- ✅ **User Registration** - With first name, last name, email or phone number
- ✅ **OTP Verification** - 6-digit verification code sent via email
- ✅ **Smart Login** - Direct login with valid cookie (2 days)
- ✅ **Session Management** - Automatic session management with secure cookies
- ✅ **Modern UI** - Split-screen design with professional animations
- ✅ **RTL Support** - Persian/Farsi UI with right-to-left layout
- ✅ **Responsive Design** - Works on mobile, tablet, and desktop
- ✅ **Security** - HttpOnly and SameSite cookies for session protection

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Modern web browser (Chrome, Firefox, Edge, Safari)
- Internet connection (for sending OTP emails)

### Installation & Setup

1. **Clone or download the project**
   ```bash
   git clone https://github.com/ALIASHRAFPOUR1382/python-js-authentication-system.git
   cd python-js-authentication-system
   ```

2. **Configure Email (Optional)**
   
   To send real OTP via email:
   ```bash
   python setup_email.py
   ```
   
   Or manually create `email_config.json`:
   ```json
   {
     "smtp_server": "smtp.gmail.com",
     "smtp_port": 587,
     "email": "your-email@gmail.com",
     "password": "your-app-password"
   }
   ```
   
   > 📝 **Note**: For Gmail, you must use an [App Password](https://support.google.com/accounts/answer/185833).

3. **Run the Server**
   
   **Windows:**
   ```bash
   start_server.bat
   ```
   
   **Linux/Mac:**
   ```bash
   chmod +x start_server.sh
   ./start_server.sh
   ```
   
   **Or manually:**
   ```bash
   cd backend
   python server.py
   ```

4. **Open Browser**
   
   Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

## 📖 Usage Guide

### Registration

1. Go to the registration page (`http://localhost:8000/register.html`)
2. Enter your first name, last name, and email or phone number
3. Click the "Sign Up" button
4. Receive the 6-digit OTP code from your email
5. Enter the code to complete registration
6. After verification, you'll be redirected to the dashboard

### Login

1. Go to the login page (`http://localhost:8000/index.html`)
2. Enter your email or phone number
3. **If you have a valid cookie (less than 2 days)**: You'll be logged in directly
4. **Otherwise**: An OTP code will be sent to you
5. Enter the code to log in

### Logout

From the dashboard, click the "Logout" button.

## 📁 Project Structure

```
.
├── backend/
│   ├── server.py          # Main HTTP server
│   ├── database.py        # JSON database management
│   ├── auth.py            # Authentication and session management
│   ├── otp_manager.py     # OTP code management
│   └── email_sender.py    # Email OTP sending
├── frontend/
│   ├── index.html         # Login page
│   ├── register.html     # Registration page
│   ├── dashboard.html     # User dashboard
│   ├── css/
│   │   └── style.css      # CSS styles
│   └── js/
│       └── auth.js        # JavaScript logic
├── data/                  # Data storage folder (auto-created)
│   ├── users.json         # User information
│   ├── otp_storage.json   # OTP codes
│   └── temp_data.json     # Temporary data
├── start_server.bat       # Server startup script (Windows)
├── start_server.sh        # Server startup script (Linux/Mac)
├── setup_email.py         # Email configuration setup
├── README.md              # This file
├── TROUBLESHOOTING.md    # Troubleshooting guide
└── .gitignore            # Ignored files
```

## 🔌 API Endpoints

### POST `/api/register`
Register a new user

**Request:**
```json
{
  "first_name": "Ali",
  "last_name": "Ahmadi",
  "email": "ali@example.com",
  "phone": "09123456789"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Verification code sent",
  "data": {
    "identifier": "ali@example.com"
  }
}
```

### POST `/api/verify-otp`
Verify OTP code for registration

**Request:**
```json
{
  "identifier": "ali@example.com",
  "otp": "123456"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Registration successful",
  "data": {
    "user": {
      "first_name": "Ali",
      "last_name": "Ahmadi",
      "email": "ali@example.com",
      "phone": "09123456789"
    }
  }
}
```

### POST `/api/login`
Login to the system

**Request:**
```json
{
  "email": "ali@example.com",
  "phone": "09123456789"
}
```

**Response (Direct Login):**
```json
{
  "success": true,
  "data": {
    "direct_login": true,
    "user": {
      "first_name": "Ali",
      "last_name": "Ahmadi"
    }
  }
}
```

**Response (Requires OTP):**
```json
{
  "success": true,
  "message": "Verification code sent",
  "data": {
    "identifier": "ali@example.com",
    "requires_verification": true
  }
}
```

### POST `/api/verify-login-otp`
Verify OTP code for login

**Request:**
```json
{
  "identifier": "ali@example.com",
  "otp": "123456"
}
```

### GET `/api/check-auth`
Check authentication status

**Response:**
```json
{
  "success": true,
  "authenticated": true,
  "user": {
    "first_name": "Ali",
    "last_name": "Ahmadi",
    "email": "ali@example.com",
    "phone": "09123456789"
  }
}
```

### POST `/api/logout`
Logout from the system

**Response:**
```json
{
  "success": true,
  "message": "Logout successful"
}
```

## 🔒 Security

- ✅ OTP codes expire after 5 minutes
- ✅ Sessions expire after 2 days
- ✅ Cookies are set with `HttpOnly` and `SameSite=Lax`
- ✅ Secure token generation for sessions
- ✅ User input validation
- ✅ Protection against OTP reuse

## ⚠️ Important Notes

> **This project is for educational and development purposes**

- 🔐 In production, you must use HTTPS
- 📧 For real OTP delivery, use SMS/Email services
- 🗄️ For better security, use a real database (PostgreSQL, MySQL)
- 🛡️ For enhanced security, use secure frameworks like Flask or Django
- 🔑 Data is stored in JSON files (use a real database for production)

## 🛠️ Development

### Adding Real OTP Delivery Service

In `backend/email_sender.py`, you can use the following services:

- **SMS**: Use SMS service APIs (KavehSMS, PayamGostar, etc.)
- **Email**: Use SMTP for email delivery (Gmail, Outlook, etc.)

### Changing Session Duration

In `backend/server.py`, change the `max_age_days` variable in the `_set_cookie` method:
```python
cookie = self._set_cookie('session_token', session_token, max_age_days=2)
```

### Changing OTP Expiry Time

In `backend/otp_manager.py`, change the `OTP_EXPIRY_MINUTES` variable:
```python
OTP_EXPIRY_MINUTES = 5  # Change to desired time
```

## 🐛 Troubleshooting

If you encounter any issues, refer to [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

### Common Issues

1. **404 Error**: Make sure the server is running
2. **OTP not received**: Check email configuration
3. **SMTP Error**: Use App Password for Gmail

## 📝 License

This project is free to use.

## 🤝 Contributing

Contributions, suggestions, and bug reports are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Support

If you encounter any issues or have questions:

- 📖 Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- 🐛 Open an Issue
- 💬 Ask questions in Discussions

## 🌟 Future Features

- [ ] 2FA (Two-Factor Authentication) support
- [ ] Password recovery
- [ ] User profile update
- [ ] Multi-language support
- [ ] Real database integration (PostgreSQL, MySQL)
- [ ] OAuth support (Google, GitHub, etc.)
- [ ] Logging and monitoring
- [ ] Automated tests

## 📊 Project Stats

- **Languages**: Python, JavaScript, HTML, CSS
- **Framework**: No framework (Raw Python)
- **Storage**: JSON Files
- **Protocol**: HTTP/1.0
- **Port**: 8000

---

<div align="center">

**Made with ❤️ for learning and development**

⭐ If this project was helpful, please give it a star!

</div>
