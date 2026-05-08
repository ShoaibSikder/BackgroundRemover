# BackgroundRemover

Transparent background removal with a Django backend and a modern React frontend.

## Overview

BackgroundRemover lets you upload an image, process it into a transparent PNG, preview the result, and download it from a cleaner web interface. The project is split into:

- `backend/` - Django REST API for upload, processing, download, and basic auth endpoints
- `frontend/` - React + Vite app for the upload and preview experience

## Highlights

- Image upload with automatic background removal
- Transparent PNG output
- Download endpoint for processed images
- Responsive React frontend with before/after preview
- Basic user register and login endpoints
- Admin-only image and activity views
- Fallback image-processing path when `rembg` runtime support is unavailable

## Tech Stack

- Backend: Django, Django REST Framework, Pillow, OpenCV, rembg
- Frontend: React, Vite, CSS

## Project Structure

```text
BackgroundRemover/
|-- backend/
|   |-- backend/
|   |-- images/
|   |-- users/
|   |-- media/
|   `-- manage.py
|-- frontend/
|   |-- src/
|   `-- package.json
|-- requirements.txt
`-- README.md
```

## Getting Started

### 1. Install backend dependencies

From the project root:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Set up the backend

```powershell
cd backend
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The backend runs at:

```text
http://127.0.0.1:8000
```

### 3. Set up the frontend

Open a second terminal from the project root:

```powershell
cd frontend
npm install
npm run dev
```

The frontend runs at:

```text
http://127.0.0.1:5173
```

## API Endpoints

### Auth

- `POST /api/auth/register/` - Register a new user
- `POST /api/auth/login/` - Login with username and password
- `GET /api/auth/all-users/` - List all users, admin only

### Images

- `GET /api/images/` - List current user images
- `POST /api/images/` - Upload an image and process it
- `GET /api/images/{id}/download/` - Download processed image
- `GET /api/images/all/` - List all uploaded images, admin only
- `GET /api/images/activities/` - View user activity log, admin only

## Notes

- Original uploads are stored in `backend/media/original/`
- Processed images are stored in `backend/media/processed/`
- Output images are saved as PNG to preserve transparency
- The backend tries `rembg` first and falls back to OpenCV-based segmentation if ONNX runtime is not available

## Development Tips

- Use the frontend dev server for UI work
- Use Django admin for inspecting uploaded images and activity
- If image processing behaves differently across machines, check installed native dependencies for `rembg` and ONNX runtime

## License

This project includes an MIT license in the repository.
