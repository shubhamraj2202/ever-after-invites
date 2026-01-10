"""
Event Invitation Platform - FastAPI Backend
Modular architecture designed for SaaS scalability

Phase 1 (Current): Single event, file-based, localhost
Phase 2: Multi-event, database, user accounts
Phase 3: Theme marketplace, payments, email
Phase 4: GCP deployment, custom domains, analytics
"""

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pathlib import Path
import json
import shutil
from typing import Optional, List

from config import settings

# Initialize FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Config-driven event invitation platform with multi-tenant support",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc UI
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (default theme assets for backward compatibility)
# Phase 1: Mount default theme assets at /assets
# Phase 2: Dynamic theme selection will use /themes/{theme_id}/assets
default_theme_assets = Path("themes/beach/assets")
if default_theme_assets.exists():
    app.mount("/assets", StaticFiles(directory=str(default_theme_assets)), name="assets")

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


# ============================================
# Pydantic Models (API Schemas)
# ============================================

class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    token: str
    user: dict


class ConfigUpdate(BaseModel):
    config: dict


class UserCreate(BaseModel):
    username: str
    email: str  # Phase 2: Add email validation with pydantic[email]
    password: str
    full_name: Optional[str] = None


# ============================================
# Phase 1: In-Memory User Store
# Phase 2: Will migrate to database (models.py)
# ============================================

users_db = {
    "admin": {
        "username": "admin",
        "email": "admin@example.com",
        "hashed_password": pwd_context.hash("admin"),
        "role": "admin",
        "full_name": "Administrator"
    }
}


# ============================================
# Authentication Functions
# Phase 1: Simple JWT
# Phase 2: Add Google OAuth
# ============================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify JWT token and return user payload
    Used as dependency for protected routes
    """
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        username = payload.get("username")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


def require_admin(user: dict = Depends(verify_token)):
    """Require admin role (for protected routes)"""
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user


# ============================================
# Config Storage Interface
# Phase 1: File-based (config.json)
# Phase 2: Database-based (Event.config column)
# ============================================

class ConfigStorage:
    """
    Abstract interface for config storage
    Allows switching between file and database seamlessly
    """

    def get(self, event_id: str = "default") -> dict:
        """Get config for an event"""
        raise NotImplementedError

    def save(self, config: dict, event_id: str = "default") -> str:
        """Save config, return backup filename"""
        raise NotImplementedError

    def list_backups(self) -> List[dict]:
        """List all backup configs"""
        raise NotImplementedError

    def restore(self, backup_filename: str) -> None:
        """Restore from backup"""
        raise NotImplementedError


class FileConfigStorage(ConfigStorage):
    """
    Phase 1: File-based storage (current)
    Simple and works for single event
    """

    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)

    def get(self, event_id: str = "default") -> dict:
        """Load config from JSON file"""
        if not self.config_file.exists():
            raise HTTPException(status_code=404, detail="Config file not found")

        with open(self.config_file, "r") as f:
            return json.load(f)

    def save(self, config: dict, event_id: str = "default") -> str:
        """Save config with automatic backup"""
        # Create backup
        timestamp = int(datetime.now().timestamp() * 1000)
        backup_path = f"config.backup.{timestamp}.json"

        if self.config_file.exists():
            shutil.copy(self.config_file, backup_path)

        # Save new config
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)

        return backup_path

    def list_backups(self) -> List[dict]:
        """List all backup files"""
        backups = []
        for file in Path(".").glob("config.backup.*.json"):
            try:
                timestamp = int(file.stem.split(".")[-1])
                backups.append({
                    "filename": file.name,
                    "timestamp": timestamp,
                    "date": datetime.fromtimestamp(timestamp / 1000).isoformat()
                })
            except ValueError:
                continue

        return sorted(backups, key=lambda x: x["timestamp"], reverse=True)

    def restore(self, backup_filename: str) -> None:
        """Restore config from backup"""
        if not backup_filename.startswith("config.backup."):
            raise HTTPException(status_code=400, detail="Invalid backup filename")

        backup_path = Path(backup_filename)
        if not backup_path.exists():
            raise HTTPException(status_code=404, detail="Backup file not found")

        # Backup current config before restore
        self.save(self.get(), "pre-restore")

        # Restore from backup
        shutil.copy(backup_path, self.config_file)


# Initialize storage (will be swapped in Phase 2)
config_storage = FileConfigStorage()


# ============================================
# Theme Management
# ============================================

class ThemeManager:
    """
    Manage themes and theme loading
    Phase 1: File-based themes
    Phase 3: Database themes with marketplace
    """

    def __init__(self, themes_dir: str = "themes"):
        self.themes_dir = Path(themes_dir)

    def list_themes(self) -> List[dict]:
        """List all available themes"""
        themes = []

        if not self.themes_dir.exists():
            return themes

        for theme_dir in self.themes_dir.iterdir():
            if theme_dir.is_dir():
                theme_json_path = theme_dir / "theme.json"
                if theme_json_path.exists():
                    with open(theme_json_path, "r") as f:
                        theme_data = json.load(f)
                        themes.append(theme_data)

        return themes

    def get_theme(self, theme_id: str) -> dict:
        """Get theme metadata"""
        theme_path = self.themes_dir / theme_id / "theme.json"

        if not theme_path.exists():
            raise HTTPException(status_code=404, detail="Theme not found")

        with open(theme_path, "r") as f:
            return json.load(f)

    def get_theme_file_path(self, theme_id: str, filename: str) -> Path:
        """Get path to theme file"""
        theme_dir = self.themes_dir / theme_id

        if not theme_dir.exists():
            raise HTTPException(status_code=404, detail="Theme not found")

        file_path = theme_dir / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found in theme")

        return file_path


# Initialize theme manager
theme_manager = ThemeManager()


# ============================================
# API Routes
# ============================================

@app.get("/")
async def root():
    """Serve main invitation page from default theme (beach)"""
    default_theme = "beach"
    theme_index = theme_manager.get_theme_file_path(default_theme, "index.html")
    return FileResponse(theme_index)


@app.get("/config.json")
async def serve_config():
    """
    Serve config.json publicly for frontend to load
    This is the event-specific configuration (not sensitive)
    """
    config_file = Path("config.json")
    if not config_file.exists():
        raise HTTPException(status_code=404, detail="Config file not found")
    return FileResponse(config_file)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================
# Authentication Routes
# ============================================

@app.post("/api/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    User login endpoint
    Phase 1: Username/password
    Phase 2: Add Google OAuth
    """
    user = users_db.get(request.username)

    if not user or not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Create access token
    access_token = create_access_token(
        data={
            "username": user["username"],
            "email": user["email"],
            "role": user.get("role", "user")
        }
    )

    return {
        "success": True,
        "token": access_token,
        "user": {
            "username": user["username"],
            "email": user["email"],
            "role": user.get("role", "user"),
            "full_name": user.get("full_name")
        }
    }


@app.post("/api/logout")
async def logout(user: dict = Depends(verify_token)):
    """
    Logout endpoint (client-side token removal)
    Future: Token blacklist for extra security
    """
    return {"success": True, "message": "Logged out successfully"}


@app.get("/api/verify")
async def verify_auth(user: dict = Depends(verify_token)):
    """Verify token validity"""
    return {
        "success": True,
        "user": {
            "username": user.get("username"),
            "email": user.get("email"),
            "role": user.get("role")
        }
    }


# ============================================
# Config Management Routes
# ============================================

@app.get("/api/config")
async def get_config(user: dict = Depends(verify_token)):
    """
    Get current config
    Phase 1: Returns single config.json
    Phase 2: Returns user's event configs
    """
    config = config_storage.get()
    return {"success": True, "config": config}


@app.post("/api/config")
async def update_config(
    request: ConfigUpdate,
    user: dict = Depends(require_admin)
):
    """
    Update config (admin only)
    Phase 1: Updates config.json
    Phase 2: Updates database
    """
    backup_filename = config_storage.save(request.config)

    return {
        "success": True,
        "message": "Config updated successfully",
        "backupFile": backup_filename
    }


@app.get("/api/config/backups")
async def list_backups(user: dict = Depends(require_admin)):
    """List all config backups"""
    backups = config_storage.list_backups()
    return {"success": True, "backups": backups}


@app.post("/api/config/restore/{filename}")
async def restore_backup(
    filename: str,
    user: dict = Depends(require_admin)
):
    """Restore config from backup"""
    config_storage.restore(filename)

    return {
        "success": True,
        "message": "Config restored successfully",
        "restoredFrom": filename
    }


# ============================================
# Theme Management Routes
# ============================================

@app.get("/api/themes")
async def list_themes(user: dict = Depends(verify_token)):
    """
    List all available themes
    Phase 1: Returns file-based themes
    Phase 3: Returns marketplace themes with pricing
    """
    themes = theme_manager.list_themes()
    return {
        "success": True,
        "themes": themes
    }


@app.get("/api/themes/{theme_id}")
async def get_theme(theme_id: str, user: dict = Depends(verify_token)):
    """Get theme metadata"""
    theme = theme_manager.get_theme(theme_id)
    return {
        "success": True,
        "theme": theme
    }


@app.get("/themes/{theme_id}/{file_path:path}")
async def serve_theme_file(theme_id: str, file_path: str):
    """
    Serve theme files (CSS, JS, images, etc.)
    Allows themes to be completely self-contained
    """
    try:
        file = theme_manager.get_theme_file_path(theme_id, file_path)
        return FileResponse(file)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Static File Serving
# ============================================

@app.get("/{path:path}")
async def serve_static(path: str):
    """Serve static files (HTML, CSS, JS)"""
    file_path = Path(path)

    if file_path.exists() and file_path.is_file():
        return FileResponse(path)

    raise HTTPException(status_code=404, detail="File not found")


# ============================================
# Phase 2+ Routes (Commented out for now)
# ============================================

# @app.post("/api/users/register")
# async def register_user(user_data: UserCreate):
#     """User registration (Phase 2)"""
#     pass

# @app.get("/api/events")
# async def list_events(user: dict = Depends(verify_token)):
#     """List user's events (Phase 2)"""
#     pass

# @app.post("/api/events")
# async def create_event(event_data: dict, user: dict = Depends(verify_token)):
#     """Create new event (Phase 2)"""
#     pass

# @app.get("/api/themes")
# async def list_themes():
#     """List available themes (Phase 3)"""
#     pass

# @app.post("/api/payments/checkout")
# async def create_checkout(theme_id: int, user: dict = Depends(verify_token)):
#     """Create payment checkout (Phase 3)"""
#     pass


# ============================================
# Run Server
# ============================================

if __name__ == "__main__":
    import uvicorn

    print(f"\n{'='*60}")
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"{'='*60}")
    print(f"📍 Server: http://{settings.HOST}:{settings.PORT}")
    print(f"🎨 Invitation: http://localhost:{settings.PORT}/")
    print(f"🔐 Admin Panel: http://localhost:{settings.PORT}/admin.html")
    print(f"📚 API Docs: http://localhost:{settings.PORT}/docs")
    print(f"👤 Login: admin / admin")
    print(f"{'='*60}\n")

    uvicorn.run(
        "server:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
