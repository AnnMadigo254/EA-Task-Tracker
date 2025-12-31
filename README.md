# EA Task Tracker - Enterprise Architecture Management System

A comprehensive task management system built for Co-operative Bank of Kenya's Enterprise Architecture team, featuring a modern Vue.js frontend and powerful Django REST Framework backend.

## 🎯 Overview

EA Task Tracker is a full-stack solution designed to manage and track Enterprise Architecture projects across multiple architects. It provides visual workflow management, advanced search capabilities, historical tracking, and comprehensive reporting.

### ✨ Key Features

**Frontend (Vue 3 + Tailwind CSS):**
- 📋 Visual Kanban boards for each architect
- 🎨 Co-operative Bank green theme with responsive design
- 🔄 Drag & drop task management (To Do → In Progress → Done)
- 📱 Mobile-friendly interface
- 🌓 Clean, professional UI optimized for executive demos

**Backend (Django REST Framework):**
- 🔐 JWT authentication with role-based access
- 🔍 Advanced search & filtering across all task fields
- 📊 Report generation (CSV/Excel exports)
- 📝 Complete audit trail & historical tracking
- 📎 File attachments for tasks
- 🔔 Notification system
- 👨‍💼 Custom admin portal with visual dashboards
- 🗄️ Support for both SQLite (dev) and MySQL (production)

### 🔗 Links

- **API Documentation**: `http://localhost:8000/swagger/`
- **Admin Portal**: `http://localhost:8000/admin/`

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 14+
- MySQL 8.0+ (or SQLite for development)

### Frontend Setup
```bash
# Navigate to frontend
cd EA-Task-Tracker-frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

### Backend Setup
```bash
# Navigate to backend
cd EA-Task-Tracker-backend

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start server
python manage.py runserver
```

---

## 🏗️ Tech Stack

### Frontend
- **Vue 3** - Progressive JavaScript framework
- **Tailwind CSS** - Utility-first CSS framework
- **Vite** - Next-generation frontend tooling
- **Pinia** - State management

### Backend
- **Django 4.2** - High-level Python web framework
- **Django REST Framework** - Powerful toolkit for building Web APIs
- **JWT Authentication** - Secure token-based auth
- **MySQL/SQLite** - Database options
- **Swagger/OpenAPI** - API documentation

### Key Features Implemented
- 📦 **10 Database Models** with relationships
- 🔌 **40+ API Endpoints** with filtering
- 🔍 **Full-text Search** across tasks
- 📈 **Report Generation** in multiple formats
- 📜 **Historical Tracking** with audit logs
- 🎨 **Custom Admin Interface** with badges & actions

---

## 📊 Project Structure
```
EA-Task-Tracker/
├── EA-Task-Tracker-frontend/    # Vue Frontend
│   ├── src/
│   │   ├── components/          # Vue components
│   │   ├── stores/              # State management
│   │   └── assets/              # Static assets
│   └── tailwind.config.js       # Co-op Bank theme
│
└── EA-Task-Tracker-backend/     # Django Backend
    ├── tasktracker_backend/     # Django project
    │   ├── settings.py          # Configuration
    │   └── urls.py              # URL routing
    │
    └── tasks/                   # Django app
        ├── models.py            # Database models
        ├── serializers.py       # DRF serializers
        ├── views.py             # API viewsets
        └── admin.py             # Custom admin
```

---

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/login/` - Obtain JWT token
- `POST /api/auth/refresh/` - Refresh token

### Core Resources
- `GET/POST /api/boards/` - Board management
- `GET/POST /api/tasks/` - Task CRUD operations
- `POST /api/tasks/search/` - Advanced search
- `POST /api/tasks/{id}/move/` - Move task between columns
- `GET /api/tasks/my_tasks/` - Current user's tasks

### Reports & Analytics
- `POST /api/reports/generate_task_summary/` - Generate CSV/Excel
- `POST /api/reports/generate_team_performance/` - Team metrics
- `GET /api/boards/{id}/statistics/` - Board statistics

**Full API Documentation**: Visit `/swagger/` when running the backend

---

## 📝 Environment Variables

### Backend (.env)
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_NAME=ea_task_tracker
DATABASE_USER=ea_user
DATABASE_PASSWORD=your-password
DATABASE_HOST=localhost
DATABASE_PORT=3306
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

---

## 📦 Deployment

### Frontend (Netlify/Vercel)
```bash
npm run build
# Deploy 'dist' folder
```

### Backend (Production)
```bash
gunicorn tasktracker_backend.wsgi:application --bind 0.0.0.0:8000
```

---

## 👨‍💻 Author

**Ann Steffie Madigo**  
Solution Architect | Enterprise Architecture  
Co-operative Bank of Kenya

---

## 📄 License

Internal use - Co-operative Bank of Kenya  
Enterprise Architecture Department

---
