# Engagement Invitation Platform

A config-driven, theme-based event invitation platform built with FastAPI and Python. Designed for scalability from single event to multi-tenant SaaS.

## Features

- **Theme-Based Architecture**: Separate themes for different event types (beach wedding, sunset wedding, birthday, etc.)
- **Config-Driven Content**: All content managed through `config.json`
- **Admin Panel**: Full-featured web admin for managing configurations
- **JWT Authentication**: Secure role-based access control
- **Auto-Backups**: Automatic config backups before changes
- **RESTful API**: Well-documented API with automatic Swagger docs
- **Responsive Design**: Mobile-first, fully responsive themes
- **Floating Animations**: Beautiful lantern animations and scroll effects

## Quick Start

### Prerequisites

- Python 3.11+ (tested on Python 3.13)
- pip and venv
- Git (optional, for version control)

### Installation

1. **Clone or download the repository**
   ```bash
   cd /Users/shubhamraj2202/Desktop/GitHub/engagement-invite
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the server**
   ```bash
   python server.py
   ```

5. **Access the application**
   - **Invitation Page**: http://localhost:3000/
   - **Admin Panel**: http://localhost:3000/admin.html
   - **API Documentation**: http://localhost:3000/docs
   - **Default Login**: `admin` / `admin`

## Project Structure

```
engagement-invite/
├── server.py                  # FastAPI application
├── config.py                  # Environment-based settings
├── models.py                  # SQLAlchemy database models (Phase 2+)
├── requirements.txt           # Python dependencies
├── config.json                # Event-specific configuration
├── admin.html                 # Admin panel UI
├── admin.css                  # Admin panel styles
├── admin-client.js            # Admin panel logic
├── themes/                    # Theme templates
│   └── beach/                 # Beach wedding theme (default)
│       ├── index.html         # Theme HTML template
│       ├── styles.css         # Theme styles
│       ├── config-loader.js   # Config binding logic
│       ├── theme.json         # Theme metadata
│       └── assets/            # Theme assets
│           ├── images/        # Images, photos, graphics
│           └── js/            # Theme-specific JavaScript
├── venv/                      # Virtual environment (gitignored)
└── config.backup.*.json       # Auto-generated backups
```

## Configuration

### Environment Variables

Create a `.env` file for custom configuration (optional):

```env
# Server
HOST=0.0.0.0
PORT=3000
DEBUG=True

# Security
SECRET_KEY=your-secret-key-change-in-production

# Database (Phase 2)
DATABASE_URL=sqlite:///./events.db

# Features (toggle for phased rollout)
ENABLE_DATABASE=False
ENABLE_GOOGLE_OAUTH=False
ENABLE_PAYMENTS=False
ENABLE_EMAIL=False
ENABLE_CLOUD_STORAGE=False
```

### Customizing Content

Edit `config.json` to customize:
- Couple names and details
- Event date, time, venue
- Messages and content
- Image paths
- Color scheme
- Animations

Or use the **Admin Panel** for a user-friendly interface.

## Themes

### Available Themes

- **Beach Wedding** (default): Soft ocean colors, floating lanterns, beach aesthetic

### Creating New Themes

1. Create a new directory in `themes/`:
   ```bash
   mkdir themes/sunset
   ```

2. Copy files from an existing theme:
   ```bash
   cp -r themes/beach/* themes/sunset/
   ```

3. Edit `themes/sunset/theme.json`:
   ```json
   {
     "id": "sunset",
     "name": "Sunset Wedding",
     "category": "wedding",
     "description": "Warm sunset colors with romantic ambiance"
   }
   ```

4. Customize HTML, CSS, and assets

5. Restart server to load new theme

## API Documentation

### Public Endpoints

- `GET /` - Serve invitation page (default theme)
- `GET /config.json` - Get public configuration
- `GET /health` - Health check

### Authentication Endpoints

- `POST /api/login` - User login
- `POST /api/logout` - User logout
- `GET /api/verify` - Verify token

### Config Management (Authenticated)

- `GET /api/config` - Get current config
- `POST /api/config` - Update config (admin only)
- `GET /api/config/backups` - List backups (admin only)
- `POST /api/config/restore/{filename}` - Restore from backup (admin only)

### Theme Management (Authenticated)

- `GET /api/themes` - List all available themes
- `GET /api/themes/{theme_id}` - Get theme metadata
- `GET /themes/{theme_id}/{file_path}` - Serve theme files

Full interactive API documentation: http://localhost:3000/docs

## Deployment Roadmap

### Phase 1: MVP (Current - Localhost)

**Status**: ✅ **COMPLETED**

**Features**:
- Single event invitation
- File-based configuration (config.json)
- In-memory user authentication
- Admin panel for config management
- Theme-based architecture
- Local file storage
- Default beach wedding theme

**Tech Stack**:
- FastAPI + Python 3.13
- JWT authentication
- Vanilla JavaScript frontend
- CSS custom properties for theming

**Deployment**: Localhost only (`python server.py`)

### Phase 2: Multi-Event Platform (Next)

**Features**:
- Multiple events per user
- SQLite/PostgreSQL database
- User registration
- Google OAuth login
- Per-event theme selection
- Guest list management
- RSVP tracking

**Database Migration**:
- Switch from `FileConfigStorage` to `DatabaseConfigStorage`
- Use `models.py` for User, Event, Guest tables
- Migrate existing `config.json` to database

**Tech Stack**:
- Same as Phase 1
- + SQLAlchemy ORM
- + Alembic for migrations
- + Google OAuth

**Deployment**: Still localhost or basic VPS

### Phase 3: SaaS with Marketplace

**Features**:
- Theme marketplace (free + premium themes)
- Stripe/Razorpay payment integration
- Email notifications (SendGrid/AWS SES)
- RSVP confirmations via email
- Analytics dashboard
- User subscription tiers (free, basic, premium)

**New Models**:
- `Theme`: Marketplace themes with pricing
- `ThemePurchase`: E-commerce transactions
- `Subscription`: User subscription management

**Tech Stack**:
- Same as Phase 2
- + Stripe API
- + SendGrid API
- + React admin dashboard (optional)

**Deployment**: Cloud VPS with CDN

### Phase 4: Production (GCP)

**Features**:
- Custom domains per event (e.g., `sonakshi-shubham.eventinvites.com`)
- Google Cloud Storage for images
- Cloud CDN for fast global delivery
- Auto-scaling with Kubernetes
- Analytics and monitoring
- Multi-region deployment
- Professional support

**Infrastructure**:
- GCP Cloud Run / GKE
- Cloud SQL (PostgreSQL)
- Cloud Storage
- Cloud CDN
- Cloud Monitoring

**Deployment**: Fully managed GCP

## Technology Choices

### Why FastAPI?

- **Fast**: ASGI-based, async support
- **Auto-docs**: Swagger UI at `/docs`
- **Type hints**: Built-in validation with Pydantic
- **Modern**: Python 3.10+ features
- **Scalable**: Easy migration from files → database → cloud

### Why Theme-Based Architecture?

- **Flexibility**: Each event type can have unique design
- **Marketplace Ready**: Themes can be monetized (Phase 3)
- **Maintainability**: Themes are self-contained
- **User Choice**: Users select theme that fits their event

### Why File-Based First?

- **Simplicity**: No database setup for Phase 1
- **Portability**: Easy to backup and restore
- **Git-friendly**: Config is version-controlled
- **Migration Path**: Smooth transition to database (Phase 2)

## Development

### Adding New Features

1. Update `models.py` if database changes are needed
2. Add routes in `server.py`
3. Update frontend in `admin.html` and `admin-client.js`
4. Test with `curl` or Swagger UI at `/docs`

### Database Migrations (Phase 2+)

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Code Style

- Follow PEP 8 for Python
- Use type hints for all functions
- Document all API endpoints with docstrings
- Keep routes organized by feature

## Troubleshooting

### Server won't start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**: Activate virtual environment and install dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Bcrypt version warning

**Error**: `(trapped) error reading bcrypt version`

**Solution**: This is a warning, not an error. Server will work fine. To fix:
```bash
pip install bcrypt==4.2.1 --force-reinstall
```

### Theme not loading

**Problem**: Changes to theme files not reflecting

**Solution**:
1. Hard refresh browser (Cmd+Shift+R / Ctrl+Shift+F5)
2. Check console for errors (F12 → Console)
3. Restart server if using auto-reload

### Port already in use

**Error**: `Address already in use`

**Solution**: Kill existing process or use different port:
```bash
# Find process
lsof -i :3000

# Kill process
kill -9 <PID>

# Or change port in .env
PORT=8000
```

## Security Notes

### Phase 1 (Current)

- Uses in-memory user store (lost on restart)
- Default admin credentials: `admin` / `admin`
- **Change default password before exposing to internet**
- JWT secret key should be changed in production
- No HTTPS (add reverse proxy for production)

### Production Recommendations

1. Use strong `SECRET_KEY` (generate with `openssl rand -hex 32`)
2. Enable HTTPS (Let's Encrypt or cloud provider)
3. Use environment variables, never commit secrets
4. Enable rate limiting (Phase 2+)
5. Add CSRF protection for admin panel
6. Implement OAuth2 instead of password auth
7. Use database for user management

## Contributing

This is a personal project, but suggestions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## License

MIT License - feel free to use for your own events!

## Support

For questions or issues:
- Check `/docs` for API documentation
- Review this README
- Check server logs for errors
- Test with `curl` or Postman

## Roadmap Timeline (Estimated)

- **Phase 1**: ✅ Complete (January 2026)
- **Phase 2**: February-March 2026
- **Phase 3**: April-May 2026
- **Phase 4**: June 2026

## Credits

Built with:
- FastAPI
- Pydantic
- SQLAlchemy
- Uvicorn
- Python-JOSE
- Passlib

Theme design inspired by Missing Piece Invites (for learning purposes).

---

**Made with ❤️ for Sonakshi & Shubham's Engagement**
