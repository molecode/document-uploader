# Document Uploader for Paperless-ngx

A simple, secure Flask web application for uploading documents to Paperless-ngx without exposing your Paperless instance to the internet.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
  - [1. Clone or Download the Project](#1-clone-or-download-the-project)
  - [2. Generate Configuration](#2-generate-configuration)
  - [3. Configure Environment Variables](#3-configure-environment-variables)
  - [4. Build and Run](#4-build-and-run)
- [Deployment on Synology DiskStation](#deployment-on-synology-diskstation)
  - [Option 1: Docker via SSH](#option-1-docker-via-ssh)
  - [Option 2: Synology Docker GUI](#option-2-synology-docker-gui)
  - [Setting up Reverse Proxy in Synology](#setting-up-reverse-proxy-in-synology)
  - [SSL Certificate Setup](#ssl-certificate-setup)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [Rate Limiting](#rate-limiting)
- [Security Features](#security-features)
- [Usage](#usage)
- [Monitoring](#monitoring)
  - [Health Check](#health-check)
  - [Logs](#logs)
- [Troubleshooting](#troubleshooting)
  - [Files not appearing in Paperless-ngx](#files-not-appearing-in-paperless-ngx)
  - [Cannot login](#cannot-login)
  - [Rate limiting too strict](#rate-limiting-too-strict)
- [Updating](#updating)
- [Backup](#backup)
- [Security Recommendations](#security-recommendations)
- [Uninstallation](#uninstallation)
- [AI-Generated Code](#ai-generated-code)
- [License](#license)
- [Support](#support)

## Features

- Simple drag-and-drop file upload interface
- Password-protected access
- Rate limiting to prevent brute force attacks
- Support for multiple file formats (PDF, images, documents)
- Docker-based deployment
- Health check endpoint for monitoring
- Designed for Synology DiskStation deployment

## Prerequisites

- Docker and Docker Compose installed
- Paperless-ngx instance running
- Access to the Paperless-ngx consume directory
- Python 3.12+ (for password generation)

## Quick Start

### 1. Clone or Download the Project

```bash
git clone <repository-url>
cd document-uploader
```

### 2. Generate Configuration

First, generate your secret key and password hash:

```bash
uv run generate_password.py
```

Or manually:

```bash
# Generate secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Generate password hash (replace 'your-password' with your actual password)
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your-password'))"
```

### 3. Configure Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Edit the `.env` file and set the following variables:

```env
SECRET_KEY=<generated-secret-key>
PASSWORD_HASH=<generated-password-hash>
PAPERLESS_CONSUME_DIR=/volume1/docker/paperless/consume
ALLOWED_EXTENSIONS=pdf,png,jpg,jpeg,gif,tiff,txt,doc,docx,odt,rtf
MAX_FILE_SIZE=52428800
```

**Important:** Adjust `PAPERLESS_CONSUME_DIR` to match your actual Paperless-ngx consume directory path.

### 4. Run with Docker Compose

Start the application using the pre-built image from GitHub Container Registry:

```bash
docker compose up -d
```

The application will be available at `http://localhost:5000`

**Available image tags:**
- `latest` - Latest release (recommended)
- `1.0.0` - Specific version
- `1.0` - Major.minor version
- `1` - Major version

To use a specific version, update `compose.yml`:
```yaml
image: ghcr.io/molecode/document-uploader:1.0.0
```

## Deployment on Synology DiskStation

### Option 1: Docker via SSH

1. SSH into your Synology NAS:
   ```bash
   ssh admin@your-nas-ip
   ```

2. Create a directory for the project:
   ```bash
   mkdir -p /volume1/docker/document-uploader
   cd /volume1/docker/document-uploader
   ```

3. Download the compose file and create `.env`:
   ```bash
   wget https://raw.githubusercontent.com/molecode/document-uploader/main/compose.yml
   wget https://raw.githubusercontent.com/molecode/document-uploader/main/.env.example
   cp .env.example .env
   ```

4. Configure the `.env` file as described above

5. Run the application:
   ```bash
   docker compose up -d
   ```

### Option 2: Synology Docker GUI

1. Open Docker package in DSM
2. Go to Registry tab and search for `molecode/document-uploader`
3. Download the image from GitHub Container Registry
   - Or manually pull: `ghcr.io/molecode/document-uploader:latest`
4. Create a container with these settings:
   - Port: 5000:5000
   - Volume: Mount your Paperless consume directory to `/paperless-consume`
   - Environment variables: Add all variables from `.env` file

### Setting up Reverse Proxy in Synology

1. Open **Control Panel** → **Login Portal** → **Advanced** → **Reverse Proxy**

2. Click **Create** and configure:
   - **Description:** Document Uploader
   - **Source:**
     - Protocol: HTTPS
     - Hostname: upload.yourdomain.com
     - Port: 443
     - Enable HSTS: Yes
   - **Destination:**
     - Protocol: HTTP
     - Hostname: localhost
     - Port: 5000

3. Click **Custom Header** and add:
   - Create: `X-Forwarded-For`
   - Create: `X-Forwarded-Proto`

4. Save and apply

### SSL Certificate Setup

1. Go to **Control Panel** → **Security** → **Certificate**
2. Add a new certificate (Let's Encrypt recommended)
3. Assign the certificate to your reverse proxy rule

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask session secret key | Random generated |
| `PASSWORD_HASH` | Hashed password for authentication | Hash of 'changeme' |
| `PAPERLESS_CONSUME_DIR` | Path to Paperless consume directory | `/volume1/docker/paperless/consume` |
| `UPLOAD_FOLDER` | Internal upload folder (in container) | `/paperless-consume` |
| `ALLOWED_EXTENSIONS` | Comma-separated allowed file extensions | `pdf,png,jpg,jpeg,gif,tiff,txt,doc,docx,odt,rtf` |
| `MAX_FILE_SIZE` | Maximum file size in bytes | `52428800` (50MB) |

### Rate Limiting

The application includes built-in rate limiting:
- **Login endpoint:** 10 attempts per minute per IP
- **Upload endpoint:** 20 uploads per minute per IP
- **General:** 200 requests per day, 50 per hour per IP

## Security Features

1. **Password Protection:** All access requires authentication
2. **Rate Limiting:** Prevents brute force attacks
3. **Secure File Handling:** Files are sanitized and validated
4. **Session Management:** Secure session handling with secret key
5. **HTTPS Support:** Works behind reverse proxy with SSL
6. **Non-root Container:** Docker container runs as non-privileged user
7. **Resource Limits:** CPU and memory limits prevent DoS

## Usage

1. Navigate to your deployment URL (e.g., `https://upload.yourdomain.com`)
2. Enter your password
3. Select one or more files to upload
4. Click "Upload"
5. Files will appear in Paperless-ngx after processing

## Monitoring

### Health Check

The application provides a health check endpoint at `/health`:

```bash
curl http://localhost:5000/health
```

Response: `{"status": "healthy"}`

### Logs

View application logs:

```bash
docker-compose logs -f document-uploader
```

## Troubleshooting

### Files not appearing in Paperless-ngx

1. Check that `PAPERLESS_CONSUME_DIR` points to the correct directory
2. Verify file permissions on the consume directory
3. Check Paperless-ngx logs for processing errors

### Cannot login

1. Verify `PASSWORD_HASH` is correctly set in `.env`
2. Regenerate password hash using `generate_password.py`
3. Check application logs for authentication errors

### Rate limiting too strict

Modify the rate limits in `app.py`:

```python
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],  # Adjust these values
    storage_uri="memory://"
)
```

## Updating

To update to the latest version:

```bash
# Pull the latest image
docker compose pull

# Restart with new image
docker compose down
docker compose up -d
```

Or to update to a specific version, edit `compose.yml` and change the image tag:
```yaml
image: ghcr.io/molecode/document-uploader:1.1.0
```

## Backup

Important files to backup:
- `.env` (contains your secrets)
- `docker-compose.yml` (if customized)

## Security Recommendations

1. Use a strong, unique password
2. Always use HTTPS (reverse proxy with SSL)
3. Keep the application updated
4. Monitor logs regularly
5. Use a firewall to restrict access
6. Consider adding 2FA if needed
7. Regularly rotate your `SECRET_KEY` and password

## Uninstallation

```bash
# Stop and remove container
docker compose down

# Remove image
docker rmi ghcr.io/molecode/document-uploader:latest

# Remove project directory (if applicable)
rm -rf /volume1/docker/document-uploader
```

## AI-Generated Code

This project was developed with the assistance of [Claude Code](https://claude.com/claude-code), an AI-powered development tool by Anthropic. While the code was generated with AI assistance, it has been reviewed and tested to ensure:

- **Security**: All security best practices are followed, including password hashing, rate limiting, and input validation
- **Functionality**: The application has been tested for both direct execution and Docker deployment
- **Code Quality**: The code follows Python and Flask best practices
- **Documentation**: Comprehensive documentation and comments are provided

## License

MIT License

## Support

For issues, questions, or contributions, please open an issue on the repository.
