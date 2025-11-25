# UniSync Backend API

FastAPI backend service for UniSync - a feedback management platform.

## Features

- ✅ RESTful API with FastAPI
- ✅ Supabase (PostgreSQL) database integration
- ✅ Resend email service integration
- ✅ Rate limiting (5 requests per 15 minutes)
- ✅ Honeypot bot protection
- ✅ Structured logging with correlation IDs
- ✅ CORS configuration
- ✅ Health check endpoint
- ✅ Error handling and validation

## Tech Stack

- **Framework**: FastAPI
- **Database**: Supabase (PostgreSQL)
- **Email**: Resend
- **Rate Limiting**: slowapi (in-memory, can upgrade to Redis)
- **Language**: Python 3.9+

## Prerequisites

- Python 3.9 or higher
- Supabase account and project
- Resend account and API key
- (Optional) Redis for production rate limiting

## Setup

### 1. Clone and Install

```bash
cd Backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Required variables:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon key
- `RESEND_API_KEY`: Your Resend API key
- `RESEND_FROM_EMAIL`: Verified sender email (e.g., noreply@unisync.app)
- `ADMIN_EMAIL`: Email to receive subscription notifications

### 3. Database Setup

Create the `subscriptions` table in Supabase:

```sql
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    source TEXT DEFAULT 'landing_hero',
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'unsubscribed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_subscriptions_email ON subscriptions(email);
CREATE INDEX idx_subscriptions_created_at ON subscriptions(created_at);
```

### 4. Run Locally

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

## API Endpoints

### POST /api/subscribe

Subscribe to early access waitlist.

**Request:**
```json
{
  "email": "user@example.com",
  "bot_check": "",
  "source": "landing_hero",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Thank you for your interest! We'll be in touch soon."
}
```

**Response Headers:**
- `X-RateLimit-Limit`: "5"
- `X-RateLimit-Remaining`: "4"
- `X-RateLimit-Reset`: ISO timestamp

**Error Responses:**
- `400`: Validation error (invalid email, missing email)
- `429`: Rate limit exceeded
- `500`: Internal server error

### GET /health

Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "environment": "development"
}
```

## Frontend Integration

Update your Next.js frontend to call the backend API:

1. Add backend URL to environment variables:
```bash
# .env.local
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

2. Update the subscription API call in `app/page.tsx`:
```typescript
const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/subscribe`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: email.trim(),
    bot_check: botCheck,
    source: 'landing_hero',
    timestamp: new Date().toISOString(),
  }),
});
```

## Deployment

### Render

1. Create a new Web Service
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add all environment variables from `.env.example`
6. Deploy!

### Railway

1. Create a new project
2. Connect your GitHub repository
3. Railway will auto-detect Python and use `Procfile`
4. Add all environment variables
5. Deploy!

### Environment Variables for Production

Make sure to set:
- `ENVIRONMENT=production`
- `FRONTEND_URL=https://your-frontend-domain.com`
- All Supabase and Resend credentials

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black app/
isort app/
```

### Type Checking

```bash
mypy app/
```

## Project Structure

```
Backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Environment configuration
│   ├── database.py             # Supabase connection
│   ├── schemas.py              # Pydantic request/response models
│   ├── api/
│   │   └── routes/
│   │       └── subscribe.py   # Subscription endpoint
│   ├── services/
│   │   ├── email.py            # Resend email service
│   │   ├── rate_limit.py       # Rate limiting logic
│   │   └── subscription.py     # Subscription business logic
│   ├── middleware/
│   │   └── cors.py             # CORS configuration
│   └── utils/
│       ├── logger.py           # Structured logging
│       └── validation.py       # Email validation utilities
├── requirements.txt
├── .env.example
├── README.md
└── Procfile
```

## Security Features

- ✅ Rate limiting (5 requests per 15 minutes per IP)
- ✅ Honeypot bot protection
- ✅ Email validation and sanitization
- ✅ CORS configuration
- ✅ Input sanitization
- ✅ Error message sanitization (no internal details exposed)

## Monitoring

- Health check endpoint: `/health`
- Structured logging with correlation IDs
- Request/response logging (without sensitive data)

## Support

For issues or questions, contact: hello@unisynchq.com

# UniSync-Backend
