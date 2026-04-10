#!/usr/bin/env python3
"""
Setup script for Seva Setu Portal
Helps with initial configuration
"""

import os
import secrets

def generate_token():
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)

def setup_backend():
    """Setup backend environment"""
    print("Setting up backend...")
    
    env_path = "backend/.env"
    env_example = "backend/.env.example"
    
    if os.path.exists(env_path):
        print(f"✓ {env_path} already exists")
        return
    
    if not os.path.exists(env_example):
        print(f"✗ {env_example} not found")
        return
    
    # Read example
    with open(env_example, 'r') as f:
        content = f.read()
    
    # Generate tokens
    api_token = generate_token()
    content = content.replace("your_dropbox_access_token_here", "")
    content = content.replace("seva-setu-portal-secret-token-change-in-production", api_token)
    
    # Write .env
    with open(env_path, 'w') as f:
        f.write(content)
    
    print(f"✓ Created {env_path}")
    print(f"⚠ Please add your DROPBOX_ACCESS_TOKEN to {env_path}")
    print(f"✓ Generated API_TOKEN: {api_token}")

def setup_frontend():
    """Setup frontend environment"""
    print("\nSetting up frontend...")
    
    env_path = "frontend/.env"
    env_local = "frontend/.env.local"
    
    if os.path.exists(env_path) or os.path.exists(env_local):
        print(f"✓ Frontend .env already exists")
        return
    
    # Read backend .env to get API token
    backend_env = "backend/.env"
    api_token = "seva-setu-portal-secret-token-change-in-production"
    
    if os.path.exists(backend_env):
        with open(backend_env, 'r') as f:
            for line in f:
                if line.startswith("API_TOKEN="):
                    api_token = line.split("=", 1)[1].strip()
                    break
    
    # Create frontend .env
    content = f"""VITE_API_URL=http://localhost:8000
VITE_API_TOKEN={api_token}
"""
    
    with open(env_local, 'w') as f:
        f.write(content)
    
    print(f"✓ Created {env_local}")

def create_directories():
    """Create necessary directories"""
    dirs = [
        "frontend/public/sounds",
        "backend/logs"
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"✓ Created directory: {dir_path}")

def main():
    print("=" * 50)
    print("Seva Setu Portal - Setup Script")
    print("=" * 50)
    
    create_directories()
    setup_backend()
    setup_frontend()
    
    print("\n" + "=" * 50)
    print("Setup Complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Add your DROPBOX_ACCESS_TOKEN to backend/.env")
    print("2. Install backend dependencies: cd backend && pip install -r requirements.txt")
    print("3. Install frontend dependencies: cd frontend && npm install")
    print("4. Start backend: cd backend && python main.py")
    print("5. Start frontend: cd frontend && npm run dev")
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main()

