# Production Readiness Guide & Documentation

This document outlines the steps and configurations required to deploy the UniSync Backend to a production environment.

## Environment Variables

The following environment variables MUST be set in production:

| Variable         | Description                                          | Example                   |
| ---------------- | ---------------------------------------------------- | ------------------------- |
| `SUPABASE_URL`   | Your Supabase project URL                            | `https://xyz.supabase.co` |
| `SUPABASE_KEY`   | Supabase Service Role Key (for administrative tasks) | `eyJhbG...`               |
| `GOOGLE_API_KEY` | Gemini AI API Key                                    | `AIzaSy...`               |
| `RESEND_API_KEY` | Resend API Key for emails                            | `re_123...`               |
| `FRONTEND_URL`   | URL of the frontend application                      | `https://app.unisync.com` |
| `ENVIRONMENT`    | Deployment environment                               | `production`              |

## Database Setup

1.  Run the consolidated schema script: `migrations/000_core_schema.sql`.
2.  Enable the `pgcrypto` extension in Supabase if not already enabled.
3.  Apply RLS policies using `migrations/rls_policies.sql`.

## Deployment

### Docker (Recommended)

```bash
docker build -t unisync-backend .
docker run -p 8000:8000 --env-file .env unisync-backend
```

### Health Monitoring

The API exposes a health check endpoint at `/health`. Configure your load balancer or monitoring service to probe this endpoint.

## Observability

- **Logs**: Structured JSON logs are emitted in production mode.
- **Correlation IDs**: Every request is assigned a unique `correlation_id` (e.g., `req_170...`) for easy tracing across services.
- **Error Tracking**: Integration with Sentry is supported via `SENTRY_DSN`.

## Maintenance

- **Backups**: Supabase handles daily database backups automatically.
- **Scaling**: The FastAPI application is stateless and can be scaled horizontally.
- **Rate Limiting**: Configured in `app/config.py` using memory or Redis.
