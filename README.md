# BizOS - Multi-Tenant SaaS Operations Platform

**BizOS** is a robust, modular, and AI-enhanced business operations platform built with Flask. It is designed to empower modern businesses with a unified suite of tools for client management, automated invoicing, inventory tracking, and social media orchestration.

## 🚀 Vision
To provide a scalable, multi-tenant ecosystem where businesses can manage their entire operational lifecycle—from first contact to final invoice—with the power of AI-driven insights.

## ✨ Key Features

### 🏢 Core Multi-Tenancy
- **Company Isolation**: Strict data segregation for multiple organizations.
- **RBAC**: Granular Role-Based Access Control (Owner, Admin, Manager, Staff, etc.).
- **Security**: JWT-based authentication with standard Access/Refresh token lifecycles.

### 👥 Client Portal
- **Managed Access**: Secure login for external clients.
- **Transparency**: Real-time project updates and shared file repository.
- **Communication**: Direct messaging and feedback loops.

### 📅 Booking & Appointments
- **Service Management**: Define services with custom durations and pricing.
- **Availability**: Staff-specific scheduling and calendar management.
- **Seamless Booking**: Public-facing booking endpoints for clients.

### 📄 Invoicing & AI Receipt Scanner
- **Automated Invoicing**: Create, send, and track invoice statuses.
- **AI OCR**: Intelligent receipt scanning using Anthropic Claude/OpenAI for automated expense entry.
- **Financial Overview**: Detailed tracking of unpaid and overdue accounts.

### 📦 Inventory Management
- **Product Catalog**: Manage SKU-based products with categories.
- **Stock Tracking**: Real-time stock levels and low-stock alerts.
- **History**: Detailed stock movement logs (Sales, Damage, Restock).

### 🤳 Social Media Scheduler
- **Integrated Posting**: Connect Facebook, Instagram, Twitter, and LinkedIn.
- **Scheduling**: Queue posts with media for future publication.
- **Connectivity**: Real-time monitoring of platform connection status.

### 📊 Dashboard & Analytics
- **At-a-glance Stats**: Real-time overview of clients, bookings, and revenue.
- **Field Reports**: Location-based reporting for off-site teams.

## 🛠 Tech Stack
- **Backend**: Flask (Factory Pattern)
- **Database**: PostgreSQL (via SQLAlchemy/Migrate) - *SQLite supported for local dev*
- **Authentication**: JWT & Bcrypt
- **Async Tasks**: Celery & Redis
- **AI Gateway**: Anthropic Claude / OpenAI
- **Security**: Flask-Limiter (Rate Limiting), CSRF Protection

## 🛠 Getting Started

1. **Clone the Repo**:
   ```bash
   git clone https://github.com/EE2506/BizOs.git
   cd BizOs
   ```
2. **Environment Setup**:
   Follow the detailed [Setup Guide](flask_guide.md) to initialize your virtual environment and local database.
3. **Run the App**:
   ```bash
   flask run
   ```

---
Built with ❤️ for modern business efficiency.
