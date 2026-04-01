# Secure Password Reset Implementation

## Overview

Implemented a secure 2-step password reset flow with email verification and token validation.

## Setup

### 1. Add SMTP Configuration to `.env`

```env
# Email Configuration (Gmail Example)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
```

**For Gmail:**

- Enable 2-Factor Authentication
- Generate an "App Password" at https://myaccount.google.com/apppasswords
- Use this 16-character app password as `SMTP_PASSWORD`

**For Other SMTP Providers:**

- Adjust `SMTP_SERVER` and `SMTP_PORT` accordingly
- Example: Office 365: `smtp.office365.com:587` (with TLS)

### 2. Database Migration

Run migrations to create the `password_reset_tokens` table:

```bash
# The table will be created automatically when you run the app
# If using Alembic, generate and run migrations:
alembic revision --autogenerate -m "Add password reset tokens table"
alembic upgrade head
```

## API Endpoints

### 1. Request Password Reset

```http
POST /api/v1/auth/forgot-password
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Response:**

```json
{
  "message": "If email exists, password reset link will be sent"
}
```

**What happens:**

- Generates a unique reset token
- Stores token in database (expires in 30 minutes)
- Sends email with reset link
- Token is included in the reset URL

### 2. Reset Password with Token

```http
POST /api/v1/auth/reset-password
Content-Type: application/json

{
  "email": "user@example.com",
  "token": "reset_token_from_email",
  "new_password": "NewSecurePassword123"
}
```

**Response:**

```json
{
  "message": "Password reset successfully"
}
```

**Validation:**

- Token must be valid and not used before
- Token must not be expired (30-minute window)
- User email must exist
- After reset, token is marked as used

## Security Features

✅ **Token-based verification** - User must have email access to get token  
✅ **Time-limited tokens** - Tokens expire after 30 minutes  
✅ **One-time use tokens** - Each token can only be used once  
✅ **Email validation** - Reset link must come from registered email  
✅ **No email enumeration** - Forgot-password endpoint doesn't reveal if email exists  
✅ **Secure token generation** - Uses Python's `secrets` module  
✅ **Hashed passwords** - Passwords stored with Argon2 hashing

## Database Schema

### `password_reset_tokens` table

```
- token_id (UUID, Primary Key)
- user_id (FK to users)
- token (String, unique)
- expires_at (DateTime)
- is_used (Boolean, default=False)
- used_at (DateTime, nullable)
- created_at (DateTime)
```

## File Changes

1. **Models:** Added `PasswordResetToken` model to `src/models/DatabaseModels.py`
2. **Config:** Updated `src/config/config.py` with SMTP settings
3. **Security:** Added `generate_password_reset_token()` to `src/helpers/security.py`
4. **Email Utility:** Created `src/helpers/email_utils.py` for sending emails
5. **Schemas:** Updated `src/schema/Schemas.py` with new request/response models
6. **Routes:** Updated `src/routers/authRouters.py` with new endpoints

## Error Handling

All errors return appropriate HTTP status codes:

- `400` - Invalid request (missing fields)
- `404` - User not found
- `422` - Validation error (invalid email/token)
- `500` - Server error (email sending failed)

## Testing the Endpoints

### Using cURL

```bash
# Step 1: Request password reset
curl -X POST "http://localhost:8000/api/v1/auth/forgot-password" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com"}'

# Step 2: Reset password (use token from email)
curl -X POST "http://localhost:8000/api/v1/auth/reset-password" \
  -H "Content-Type: application/json" \
  -d '{
    "email":"user@example.com",
    "token":"token_from_email",
    "new_password":"NewPassword123"
  }'
```

### Using Postman

1. Create request to `/api/v1/auth/forgot-password` (POST)
2. Add email in JSON body
3. Check email for reset link with token
4. Create request to `/api/v1/auth/reset-password` (POST)
5. Add email, token, and new_password in JSON body

## Frontend Integration

1. User clicks "Forgot Password"
2. Enter email → Call `/forgot-password` endpoint
3. Email arrives with reset link: `https://yourapp.com/reset-password?token=xyz`
4. User clicks link and enters new password
5. Frontend extracts token from URL and calls `/reset-password` with email, token, new_password
