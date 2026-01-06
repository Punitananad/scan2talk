# Gateway Platform

A production-grade Django SaaS platform for privacy-first communication routing. Enable third parties to initiate contact without revealing personal contact details using QR codes, short links, IVR, or messaging gateways.

## 🚀 Features

### Core Functionality
- **Privacy-First Communication**: Route messages without exposing personal contact information
- **Multiple Entry Points**: QR codes, short links, IVR numbers, WhatsApp, SMS
- **Multi-Channel Routing**: SMS, WhatsApp, Email, Voice calls
- **Smart Routing Rules**: Filter by intent, time windows, rate limits
- **Real-time Analytics**: Track interactions, success rates, channel performance
- **Abuse Prevention**: IP blocking, rate limiting, spam protection

### Security & Compliance
- **Data Encryption**: Sensitive data encrypted at rest and in transit
- **Session Management**: Secure, time-limited communication sessions
- **Rate Limiting**: Configurable limits per gateway and global
- **Audit Logging**: Comprehensive interaction and routing logs
- **CSRF Protection**: Built-in security middleware
- **Legal Compliance**: GDPR-ready privacy controls

### Scalability
- **Redis Caching**: High-performance session and rate limit storage
- **Celery Tasks**: Asynchronous message processing
- **Database Optimization**: Indexed queries and efficient data models
- **API-First Design**: RESTful APIs for all functionality
- **Horizontal Scaling**: Stateless architecture ready for load balancing

## 🏗️ Architecture

### Technology Stack
- **Backend**: Django 4.x, Django REST Framework
- **Database**: PostgreSQL with optimized indexes
- **Cache/Queue**: Redis for sessions, rate limiting, and Celery
- **Frontend**: Django Templates, Tailwind CSS, HTMX, Alpine.js
- **Communication**: Twilio (SMS/Voice), WhatsApp Business API, SMTP

### Application Structure
```
gateway_platform/
├── apps/
│   ├── core/           # Base models, middleware, utilities
│   ├── accounts/       # User management and authentication
│   ├── gateways/       # Gateway and entry point management
│   ├── routing/        # Routing rules and communication flow
│   ├── interactions/   # Session management and logging
│   └── communications/ # Multi-channel message adapters
├── templates/          # HTML templates
├── static/            # Static assets
└── requirements.txt   # Python dependencies
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- Node.js (for frontend assets, optional)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd gateway-platform
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment configuration**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Database setup**
```bash
python manage.py migrate
python manage.py createsuperuser
```

6. **Generate encryption key**
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Add the output to ENCRYPTION_KEY in .env
```

7. **Run the development server**
```bash
python manage.py runserver
```

### Production Deployment

1. **Environment Variables**
```bash
# Required for production
DEBUG=False
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:pass@host:port/dbname
REDIS_URL=redis://host:port/0
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
ENCRYPTION_KEY=your-fernet-encryption-key

# Communication Services
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890
WHATSAPP_BUSINESS_API_TOKEN=your-whatsapp-token
WHATSAPP_BUSINESS_PHONE_ID=your-phone-id

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.yourdomain.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

2. **Static Files**
```bash
python manage.py collectstatic --noinput
```

3. **Database Migration**
```bash
python manage.py migrate
```

4. **Celery Workers** (separate processes)
```bash
celery -A gateway_platform worker -l info
celery -A gateway_platform beat -l info
```

5. **Web Server** (Gunicorn example)
```bash
gunicorn gateway_platform.wsgi:application --bind 0.0.0.0:8000
```

## 📡 Communication Services Setup

### Twilio (SMS & Voice)
1. Sign up at [Twilio](https://www.twilio.com)
2. Get Account SID and Auth Token from Console
3. Purchase a phone number with SMS and Voice capabilities
4. Add credentials to environment variables

### WhatsApp Business API
1. Apply for WhatsApp Business API access
2. Set up Facebook Business Manager account
3. Create WhatsApp Business Account
4. Get access token and phone number ID
5. Configure webhook endpoints for status updates

### Email (SMTP)
1. Choose email service provider (Gmail, SendGrid, etc.)
2. Configure SMTP settings
3. For Gmail: Use App Passwords for authentication
4. Test email delivery

## 🔧 Configuration

### Gateway Settings
- **Rate Limiting**: Configure per-gateway and global limits
- **Time Windows**: Set availability hours for communication
- **Channel Preferences**: Choose preferred communication channels
- **Auto-responses**: Set up automated reply messages
- **Emergency Handling**: Configure emergency escalation rules

### Security Settings
- **IP Blocking**: Block abusive IP addresses
- **Session Timeouts**: Configure session expiration times
- **Encryption**: All sensitive data is automatically encrypted
- **Rate Limits**: Prevent abuse with configurable limits

### Analytics & Monitoring
- **Interaction Logs**: Track all communication attempts
- **Performance Metrics**: Monitor success rates and response times
- **Channel Analytics**: Analyze usage by communication channel
- **Geographic Data**: Optional location tracking for analytics

## 🔌 API Documentation

### Authentication
All API endpoints require authentication via session or token:
```bash
# Get auth token
curl -X POST /api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Use token in requests
curl -H "Authorization: Token your-token-here" /api/v1/gateways/
```

### Key Endpoints

#### Gateways
- `GET /api/v1/gateways/` - List user's gateways
- `POST /api/v1/gateways/` - Create new gateway
- `GET /api/v1/gateways/{id}/` - Get gateway details
- `PUT /api/v1/gateways/{id}/` - Update gateway
- `DELETE /api/v1/gateways/{id}/` - Delete gateway

#### Routing Rules
- `GET /api/v1/routing/{gateway_id}/rules/` - List routing rules
- `POST /api/v1/routing/{gateway_id}/rules/` - Create routing rule
- `PUT /api/v1/routing/rules/{id}/` - Update routing rule

#### Interactions
- `GET /api/v1/interactions/{gateway_id}/logs/` - Get interaction logs
- `GET /api/v1/interactions/{gateway_id}/stats/` - Get statistics
- `GET /api/v1/interactions/{gateway_id}/analytics/` - Get detailed analytics

#### Communications
- `GET /api/v1/communications/status/` - Check channel status
- `POST /api/v1/communications/test-channel/` - Test communication channel

## 🛡️ Security Considerations

### Data Protection
- **Encryption**: All PII encrypted using Fernet (AES 128)
- **Session Security**: Secure session cookies with CSRF protection
- **Database Security**: Parameterized queries prevent SQL injection
- **Input Validation**: All user input validated and sanitized

### Rate Limiting
- **Global Limits**: Prevent platform-wide abuse
- **Per-Gateway Limits**: Configurable limits per gateway
- **IP-based Limiting**: Rate limit by IP address
- **Channel-specific Limits**: Different limits per communication channel

### Monitoring & Alerts
- **Failed Login Tracking**: Monitor and block suspicious login attempts
- **Abuse Detection**: Automatic detection of spam and abuse patterns
- **Error Logging**: Comprehensive error logging and monitoring
- **Security Headers**: HSTS, CSP, and other security headers

## 📊 Monitoring & Analytics

### Built-in Analytics
- **Gateway Performance**: Success rates, response times, channel usage
- **User Behavior**: Interaction patterns, popular gateways, usage trends
- **System Health**: Error rates, performance metrics, resource usage
- **Security Metrics**: Failed logins, blocked IPs, abuse attempts

### External Monitoring
- **Health Check Endpoint**: `/health/` for load balancer monitoring
- **Metrics Export**: Ready for Prometheus/Grafana integration
- **Log Aggregation**: Structured logging for ELK stack integration
- **Error Tracking**: Compatible with Sentry and similar services

## 🔄 Maintenance & Operations

### Regular Tasks
- **Database Cleanup**: Remove old interaction logs and expired sessions
- **Cache Maintenance**: Monitor Redis memory usage and performance
- **Security Updates**: Regular dependency updates and security patches
- **Backup Verification**: Test database and file backups regularly

### Scaling Considerations
- **Database Scaling**: Read replicas for analytics queries
- **Cache Scaling**: Redis clustering for high availability
- **Application Scaling**: Horizontal scaling with load balancers
- **Background Tasks**: Scale Celery workers based on queue length

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Code Standards
- **PEP 8**: Follow Python style guidelines
- **Type Hints**: Use type hints for better code documentation
- **Documentation**: Document all public APIs and complex logic
- **Testing**: Maintain test coverage above 80%

### Testing
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.gateways

# Run with coverage
coverage run manage.py test
coverage report
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Documentation
- **API Documentation**: Available at `/api/docs/` when running
- **User Guide**: Comprehensive user documentation
- **Developer Guide**: Technical implementation details

### Community Support
- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: Community discussions and Q&A
- **Wiki**: Additional documentation and tutorials

### Commercial Support
For enterprise support, custom development, or consulting services, contact us at support@gatewayplatform.com.

## 🗺️ Roadmap

### Upcoming Features
- **Mobile Apps**: Native iOS and Android applications
- **Advanced Analytics**: Machine learning-powered insights
- **Multi-language Support**: Internationalization and localization
- **Enterprise SSO**: SAML and OAuth integration
- **API Webhooks**: Real-time event notifications
- **Advanced Routing**: AI-powered message classification

### Long-term Goals
- **Global Infrastructure**: Multi-region deployment
- **Compliance Certifications**: SOC 2, ISO 27001, HIPAA
- **Partner Integrations**: CRM, helpdesk, and business tool integrations
- **White-label Solutions**: Customizable branding and deployment options

---

**Gateway Platform** - Secure, Private, Scalable Communication Routing