# 📋 Product Requirements Document (PRD)
## BizOS — All-in-One Business Operations Platform
**Version:** 1.0.0  
**Date:** February 2026  
**Stack:** Flask (Backend API) · Next.js (Frontend) · PostgreSQL (Primary DB) · Redis (Cache/Sessions)  
**UI Library:** shadcn/ui (New York style) · Tailwind CSS v4 · Dark Mode First  
**Inspiration:** Odoo · Shopify Ecosystem · Linear · Notion · Vercel Dashboard

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture Overview](#2-system-architecture-overview)
3. [Authentication & Security](#3-authentication--security)
4. [Role & Permission System](#4-role--permission-system)
5. [Tenant Onboarding & Multi-Tenancy](#5-tenant-onboarding--multi-tenancy)
6. [Client Portal Module](#6-client-portal-module)
7. [Booking & Appointment Module](#7-booking--appointment-module)
8. [Invoicing & Receipt Scanner Module](#8-invoicing--receipt-scanner-module)
9. [Inventory Management Module](#9-inventory-management-module)
10. [Team & Onboarding Module](#10-team--onboarding-module)
11. [Field Reports & Daily Logs Module](#11-field-reports--daily-logs-module)
12. [Feedback & Surveys Module](#12-feedback--surveys-module)
13. [Social Media Scheduler Module](#13-social-media-scheduler-module)
14. [Dashboard & Analytics](#14-dashboard--analytics)
15. [API Design](#15-api-design)
16. [Encryption & Audit Logs](#16-encryption--audit-logs)
17. [UI Design System — shadcn/ui · Dark Mode First](#17-ui-design-system--shadcnui--dark-mode-first)
18. [Tech Stack & Dependencies](#18-tech-stack--dependencies)
19. [Database Schema](#19-database-schema)
20. [Non-Functional Requirements](#20-non-functional-requirements)
21. [Deployment & DevOps](#21-deployment--devops)
22. [Monetization & Subscription Tiers](#22-monetization--subscription-tiers)
23. [Future Roadmap](#23-future-roadmap)

---

## 1. Executive Summary

**BizOS** is a **multi-tenant, modular SaaS platform** built for **small and medium-sized businesses** across industries — including agencies, clinics, contractors, restaurants, salons, and retail operations. Instead of forcing businesses to subscribe to 5–10 separate tools, BizOS consolidates core operations into a single branded workspace.

The platform is built around a **module-based architecture**: businesses activate only the modules they need, keeping the interface clean and relevant. Each module communicates through a shared data layer, so contacts, invoices, bookings, and tickets are all connected.

Core capabilities include:

- A **Client Portal** for sharing files, updates, and invoices with external clients
- A **Booking & Appointment System** with calendar sync and Stripe payment
- **Invoicing with AI Receipt Scanning** (Claude/OpenAI powered)
- **Inventory Tracking** with multi-location and low-stock alerts
- **Team Management & Employee Onboarding** with task checklists and document collection
- **Field Report & Daily Log** submission from mobile for field workers
- **Feedback & Survey** tools with branded forms and response analytics
- A **Social Media Scheduler** with AI-generated captions
- A **unified Dashboard** with cross-module KPIs and reporting

The platform is designed to be sold **per niche** — the same codebase powers "BizOS for Dentists," "BizOS for Contractors," and "BizOS for Agencies" with different default module sets and onboarding flows.

---

## 2. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                           CLIENT LAYER                              │
│  ┌──────────────────────────────┐   ┌──────────────────────────┐   │
│  │   Business Admin Portal      │   │   Client Public Portal    │   │
│  │   Next.js App (internal)     │   │   Next.js App (external)  │   │
│  │   /app/* routes              │   │   /portal/* routes        │   │
│  └──────────────┬───────────────┘   └──────────────┬────────────┘   │
└─────────────────┼──────────────────────────────────┼────────────────┘
                  │ HTTPS / JWT                       │ HTTPS / JWT
┌─────────────────▼───────────────────────────────── ▼────────────────┐
│                        FLASK REST API (v1)                           │
│  Blueprints: auth · admin · portal · bookings · invoices ·          │
│              inventory · team · reports · surveys · social ·        │
│              ai · webhooks · notifications                           │
│  Middleware: CSRF · Rate Limiter · Audit Logger · Role Gate          │
└──────────┬──────────────────────────────┬───────────────────────────┘
           │                              │
   ┌───────▼──────┐              ┌────────▼──────┐
   │  PostgreSQL  │              │  Redis Cache   │
   │  Primary DB  │              │  Sessions/Jobs │
   └──────────────┘              └───────────────┘
           │                              │
   ┌───────▼──────┐              ┌────────▼──────┐
   │  File Store  │              │  Celery Queue  │
   │  (S3/MinIO)  │              │  Async Tasks   │
   │  Docs/PDFs   │              └───────────────┘
   └──────────────┘
           │
   ┌───────▼──────┐
   │  AI Gateway  │
   │ Claude/OpenAI│
   │ Captions/OCR │
   └──────────────┘
```

### Deployment Topology

- **Frontend:** Next.js (App Router), deployed on Vercel or self-hosted behind Nginx. Split into two entry points: `app.domain.com` (admin) and `portal.domain.com` (client-facing)
- **Backend:** Flask with Gunicorn (4–8 workers), behind Nginx reverse proxy
- **Database:** PostgreSQL 16 with connection pooling via PgBouncer
- **Cache:** Redis 7 (sessions, OTP codes, rate limit counters, job queues)
- **Queue:** Celery + Redis (PDF generation, AI tasks, email notifications, social scheduling)
- **Storage:** MinIO (self-hosted S3-compatible) or AWS S3 for files and PDFs
- **AI:** Anthropic Claude API (receipt OCR, caption generation, report summaries) with OpenAI fallback

---

## 3. Authentication & Security

### 3.1 Password Security

Inspired by Laravel's Bcrypt implementation:

```python
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

# Hashing — cost factor 12 (bcrypt, NOT sha2 or md5)
password_hash = bcrypt.generate_password_hash(password, rounds=12).decode('utf-8')

# Verification
bcrypt.check_password_hash(stored_hash, provided_password)
```

**Rules:**
- All passwords hashed with **bcrypt (cost factor 12)**
- Passwords in logs: **NEVER stored in plaintext or SHA2**
- Minimum password length: 12 characters
- Must contain uppercase, lowercase, number, and special character

### 3.2 JWT Token Strategy

```
Access Token:  15-minute expiry, RS256-signed (asymmetric key pair)
Refresh Token: 7-day expiry, stored in HttpOnly cookie
Portal Token:  Separate issuer salt for client portal users
Share Token:   Ed25519 signed, time-limited or single-use (for shared links)
```

### 3.3 Security Patterns

| Feature | Implementation |
|---|---|
| CSRF Protection | `flask-wtf` CSRFProtect on all state-changing endpoints |
| Rate Limiting | `flask-limiter` with Redis backend (5 login attempts / 15 min) |
| Policy Gates | Custom `@require_permission('invoices.create')` decorators |
| Signed URLs | `itsdangerous.URLSafeTimedSerializer` for public share links |
| API Tokens | Personal Access Tokens stored hashed in DB |
| Middleware Pipeline | Flask `before_request` / `after_request` hooks |
| SQL Injection | SQLAlchemy ORM only — raw queries forbidden |
| XSS Prevention | Next.js escaping + Content-Security-Policy headers |
| CORS | `flask-cors` with strict origin whitelist |

### 3.4 Two-Factor Authentication (2FA)

- TOTP (Google Authenticator compatible) via `pyotp`
- Required for: Super Admin, Company Owner
- Optional for: All other staff roles
- Backup codes: 8 single-use codes, bcrypt-hashed in DB

### 3.5 Session Security

```
Session ID: 128-bit random (secrets.token_hex(64))
Stored in Redis with TTL
Invalidated on password change
Concurrent session limit: configurable per role (default: 3)
IP pinning: optional per company setting
```

---

## 4. Role & Permission System

### 4.1 Default Role Hierarchy

```
Super Admin (Platform Level)
  └── Company Owner (per-tenant)
        ├── Admin
        │     ├── Manager
        │     │     ├── Staff Member
        │     │     ├── Field Worker (reports only)
        │     │     └── Receptionist (bookings only)
        │     └── Accountant (read-only financials)
        └── Viewer (read-only, all modules)
```

### 4.2 Account Activation Flow

**New staff accounts are DEACTIVATED by default.**

```
1. Admin creates user account → status = 'pending'
2. System sends activation email with signed link (24hr TTL)
3. User sets password via link
4. Account → 'active' (after admin approval if company requires it)
5. Admin can toggle: auto-activate OR require manual approval
```

```python
class User(db.Model):
    status = db.Column(db.Enum('pending', 'active', 'suspended', 'deactivated'),
                       default='pending', nullable=False)
    activated_at = db.Column(db.DateTime, nullable=True)
    activated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
```

### 4.3 Permission Namespaces

| Namespace | Permissions |
|---|---|
| `portal.*` | view, create, edit, delete, share |
| `bookings.*` | view, create, edit, cancel, manage |
| `invoices.*` | view, create, send, void, export |
| `inventory.*` | view, create, edit, delete, alert |
| `team.*` | view, create, edit, deactivate |
| `reports.*` | view, submit, export, share |
| `surveys.*` | view, create, send, export |
| `social.*` | view, create, schedule, publish |
| `analytics.*` | view, export, share |
| `users.*` | view, create, edit, activate, deactivate |
| `roles.*` | view, create, edit, delete |
| `logs.*` | view (admin only) |
| `ai.*` | use (module-level AI features) |

### 4.4 Permission Enforcement

```python
from functools import wraps
from flask import g, abort

def require_permission(*permissions):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = g.current_user
            if not user.has_any_permission(permissions):
                abort(403)
            return f(*args, **kwargs)
        return decorated
    return decorator

# Usage
@bp.route('/invoices', methods=['POST'])
@jwt_required
@require_permission('invoices.create')
def create_invoice():
    ...
```

---

## 5. Tenant Onboarding & Multi-Tenancy

### 5.1 Company Registration Flow

```
1. Company signs up via platform landing page
2. Company Owner account created (status: pending)
3. Email verification + account activation
4. Guided setup wizard:
   a. Business name, logo, industry, timezone
   b. Module selection (which features to activate)
   c. Branding (accent color, portal subdomain)
   d. Team setup (invite first admin/staff)
   e. Payment (Stripe subscription, select tier)
5. Dashboard ready
```

### 5.2 Module Activation

Each company independently activates modules. Deactivated modules are hidden from the UI entirely.

```python
class CompanyModules(db.Model):
    company_id      = db.Column(db.Integer, db.ForeignKey('companies.id'))
    client_portal   = db.Column(db.Boolean, default=True)
    bookings        = db.Column(db.Boolean, default=True)
    invoicing       = db.Column(db.Boolean, default=True)
    inventory       = db.Column(db.Boolean, default=False)
    team_onboarding = db.Column(db.Boolean, default=False)
    field_reports   = db.Column(db.Boolean, default=False)
    surveys         = db.Column(db.Boolean, default=False)
    social_scheduler = db.Column(db.Boolean, default=False)
```

### 5.3 Multi-Tenancy

- Each company is a **tenant** identified by `company_id`
- All DB queries scoped by `company_id` at the ORM level
- Row-Level Security (RLS) policies enforced in PostgreSQL as a second layer
- Company data is logically isolated (shared DB, partitioned by `company_id`)
- Custom subdomains: `company-slug.bizos.app` or custom domain via CNAME

### 5.4 Niche Presets

When a company selects their industry during onboarding, default module sets are pre-activated:

| Industry | Default Modules |
|---|---|
| Agency / Freelancer | Client Portal, Invoicing, Social Scheduler |
| Clinic / Healthcare | Bookings, Client Portal, Invoicing, Surveys |
| Construction / Contractor | Field Reports, Invoicing, Team Onboarding |
| Restaurant | Inventory, Surveys, Bookings |
| Retail | Inventory, Invoicing |
| General / Other | Client Portal, Invoicing, Bookings |

---

## 6. Client Portal Module

### 6.1 Overview

The Client Portal gives businesses a **branded, secure workspace** to share with their external clients. Clients log in and see only their own files, project updates, and invoices.

### 6.2 Portal Features

**For Staff (Internal)**
- Create and manage client portal accounts
- Upload and organize files into folders
- Post project updates (title, rich text body, status badge)
- Link invoices to client portal view
- Messaging thread per client

**For Clients (External)**
- Dedicated login at `portal.domain.com` or `company-slug.bizos.app/portal`
- View shared files and download originals
- Read project updates with status (In Progress / Review / Completed)
- View and download invoices; pay online if payment gateway configured
- Submit support messages (routed to staff inbox)

### 6.3 Client Account Flow

```
Staff creates client account → email invite sent
Client clicks invite → sets password
Client accesses portal → sees only their own workspace
```

Client accounts are **entirely separate** from staff accounts — different DB table, different JWT issuer salt.

### 6.4 File Sharing

- Files stored in S3/MinIO under `company_id/client_id/`
- Max file size: 50MB per upload, 5GB per tenant (plan-dependent)
- Supported types: PDF, DOCX, XLSX, PNG, JPG, MP4, ZIP
- Files can be set to: public (download link) or private (portal login required)
- Expiring download links generated via signed tokens (1hr / 24hr / 7 days)

---

## 7. Booking & Appointment Module

### 7.1 Overview

A complete scheduling solution for service-based businesses. Clients can book directly from a public booking page without logging in.

### 7.2 Features

**Service Configuration**
- Define services (name, duration, price, buffer time, max bookings per slot)
- Staff assignment per service (any available staff or specific assignee)
- Location or virtual (Zoom/Meet link auto-generated)

**Availability Management**
- Per-staff weekly availability schedules
- Block-out dates and hours (holidays, vacations)
- Timezone handling (staff TZ vs client TZ)

**Public Booking Page**
- URL: `company-slug.bizos.app/book` or embedded widget (iframe)
- Client selects service → picks date/time → enters details → confirms
- No login required for clients to book
- reCAPTCHA v3 on booking form

**Booking Lifecycle**
```
Client books → Confirmation email (client + staff)
             → Calendar invite (.ics) attached
             → Status: Confirmed
             → Reminder sent 24hr before (email/SMS)
             → Appointment completed → auto-trigger survey (optional)
             → Staff marks: Completed / No-Show / Cancelled
```

**Payments**
- Optional Stripe payment at booking (full or deposit)
- Refund flow for cancellations (configurable policy)
- Invoice auto-generated on payment

**Calendar Views**
- Staff calendar: Day / Week / Month view
- Google Calendar / Outlook sync (two-way via OAuth)
- iCal export

### 7.3 Booking Data Model (Summary)

```
Service → BookingSlots (generated from availability)
Booking → Service (N:1)
Booking → Client (N:1, nullable for guest bookings)
Booking → StaffMember (N:1, assignee)
Booking → Invoice (1:1, optional)
```

---

## 8. Invoicing & Receipt Scanner Module

### 8.1 Invoice Features

- Create invoices with line items (description, qty, unit price, tax rate, discount)
- Multiple currencies (configured per company)
- Invoice statuses: Draft / Sent / Partial / Paid / Overdue / Void
- Auto-numbering: `INV-YYYYMM-XXXX`
- Payment recording (partial and full)
- Stripe payment link embedded in invoice
- PDF generation (WeasyPrint via Celery async task)
- Email invoice directly from platform (SMTP or SendGrid)

### 8.2 AI Receipt Scanner

**Feature:** Upload a photo or PDF of a receipt → AI extracts structured data → logged as an expense.

```
Upload image/PDF
       ↓
Celery task: send to Claude API (vision)
       ↓
Extract: vendor name, date, total, line items, tax, payment method
       ↓
Return structured JSON → create Expense record
       ↓
Staff reviews, edits, confirms
       ↓
Optional: attach to invoice as billable expense
```

```python
# Celery task: AI receipt scan
@celery.task
def scan_receipt(file_url, company_id):
    image_data = download_and_encode_base64(file_url)
    response = anthropic_client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64",
                 "media_type": "image/jpeg", "data": image_data}},
                {"type": "text", "text": RECEIPT_EXTRACTION_PROMPT}
            ]
        }]
    )
    return parse_receipt_response(response.content[0].text)
```

### 8.3 PDF Invoice Template

```
[Company Logo]                     [Invoice #INV-202602-0001]
[Company Name & Address]           [Issue Date / Due Date]

Bill To:
[Client Name & Address]

| Description       | Qty | Unit Price | Tax  | Total  |
|-------------------|-----|------------|------|--------|
| Web Design        | 1   | ₱50,000    | 12%  | ₱56,000|

                              Subtotal:      ₱50,000
                              Tax (12%):     ₱6,000
                              Total Due:     ₱56,000
                              Amount Paid:   ₱0.00
                              Balance Due:   ₱56,000

[Payment Link Button]
[Terms & Conditions]
```

### 8.4 Public Invoice Share Link

```
Admin clicks "Share Invoice"
       ↓
Signed URL: /invoice/view/{public_token}
       ↓
Client views + downloads PDF (no login required)
       ↓
Pay Now button (Stripe) if gateway configured
       ↓
Token expiry: 30 days (configurable)
Admin can revoke at any time
```

---

## 9. Inventory Management Module

### 9.1 Features

**Product Catalog**
- Products with: name, SKU, category, description, images, unit cost, sale price
- Variants support (size, color, etc.)
- Barcode/QR code generation and scanning

**Stock Management**
- Current stock levels per product per location
- Manual stock adjustments with reason log
- Minimum stock threshold → low-stock alert (email + dashboard badge)
- Stock transfer between locations

**Multi-Location**
- Define warehouse / store locations
- Stock tracked independently per location
- Consolidated view across all locations

**Purchase Orders**
- Create purchase orders (POs) to suppliers
- PO statuses: Draft / Sent / Received / Cancelled
- Receiving flow: mark items received → stock auto-updated

**Reports**
- Stock valuation report
- Low-stock report
- Movement history per product
- Slow-moving inventory (no sales in X days)

### 9.2 Low-Stock Alert System

```python
# Celery periodic task (runs every hour)
@celery.task
def check_low_stock():
    items = InventoryItem.query.filter(
        InventoryItem.quantity <= InventoryItem.reorder_threshold
    ).all()
    for item in items:
        send_low_stock_alert(item)
        create_dashboard_notification(item)
```

---

## 10. Team & Onboarding Module

### 10.1 Features

**Employee Directory**
- Staff profiles: name, role, department, contact info, documents
- Employment status: Active / On Leave / Terminated
- Org chart view

**Onboarding Checklists**
- Define onboarding templates per role/department
- Tasks with: title, description, due date offset (e.g., "Day 1", "Week 1"), assignee
- New hire sees their personalized checklist on first login
- Manager sees completion progress dashboard

**Document Collection**
- Request documents from new hires via portal (government IDs, contracts, certs)
- New hire uploads directly to their profile
- Staff/HR marks documents as verified or rejected with notes

**Leave Management (Basic)**
- Submit leave requests (sick, vacation, unpaid)
- Manager approves / rejects
- Leave balance tracking per employee

### 10.2 Onboarding Flow

```
HR creates employee account
       ↓
Employee activates via email
       ↓
Onboarding checklist generated from role template
       ↓
Employee completes tasks (watch video, sign contract, upload ID)
       ↓
HR/Manager receives completion notification
       ↓
Account fully activated (access to all assigned modules)
```

---

## 11. Field Reports & Daily Logs Module

### 11.1 Overview

Designed for **construction, maintenance, delivery, and field service** businesses where workers are on-site and need to submit end-of-day reports from their phone.

### 11.2 Features

**Report Submission (Mobile-First)**
- Simple form: date, site/job, hours worked, work summary, issues, photos
- Photo upload (up to 10 photos per report, compressed on upload)
- GPS location stamp (optional, toggleable per company)
- Works offline, syncs when online

**Report Types**
- Daily Site Report
- Incident / Safety Report
- Equipment Check Report
- Custom report types (admin configurable)

**Manager Dashboard**
- View all submitted reports by date, team, or site
- Filter by: staff member, date range, site/job
- Flag reports for follow-up
- Export to PDF or CSV

**Notifications**
- Manager notified when a report is not submitted by end of day (configurable cutoff)
- Staff reminded to submit report (push notification or email)

### 11.3 Report Data Model

```sql
field_reports (
  id, company_id, submitted_by, report_type, job_site_id,
  report_date, hours_worked, work_summary, issues_noted,
  photos_json, gps_lat, gps_lng,
  status [draft/submitted/reviewed/flagged],
  reviewed_by, reviewed_at,
  created_at, updated_at
)
```

---

## 12. Feedback & Surveys Module

### 12.1 Features

**Survey Builder**
- Question types: text, multiple choice, rating (1–5 stars / NPS), yes/no, dropdown
- Multi-page surveys
- Branching logic (show question B only if answer to A is X)
- Company branding (logo, colors)

**Survey Distribution**
- Shareable link (no login required for respondents)
- Email blast to customer list
- Embed as widget on company website
- Auto-trigger: after appointment completed, after invoice paid, after ticket resolved

**Response Dashboard**
- Total responses, completion rate, average scores
- Per-question breakdown with charts
- NPS score calculation and trend
- Export responses to CSV

**Templates**
- Post-appointment satisfaction (CSAT)
- Net Promoter Score (NPS)
- Product feedback
- Employee satisfaction (internal)

### 12.2 Auto-trigger Integration

```python
# Triggered via Celery after appointment completion
@celery.task
def send_post_appointment_survey(booking_id):
    booking = Booking.query.get(booking_id)
    company = booking.company
    if company.modules.surveys and company.settings.auto_survey_on_completion:
        survey = Survey.query.filter_by(
            company_id=company.id,
            trigger='post_appointment'
        ).first()
        if survey:
            send_survey_email(booking.client_email, survey)
```

---

## 13. Social Media Scheduler Module

### 13.1 Overview

A lightweight social media scheduling tool for businesses that manage their own social presence. Uses AI (Claude) to generate captions based on post context.

### 13.2 Supported Platforms

- Facebook (Pages via Meta Graph API)
- Instagram (Business Accounts via Meta Graph API)
- LinkedIn (Company Pages via LinkedIn API)
- Twitter/X (via X API v2) *(optional, due to API cost)*

### 13.3 Features

**Post Composer**
- Upload image/video, write caption, add hashtags
- Schedule date/time per platform or post to all at once
- Preview how post will look on each platform
- Link-in-bio support for Instagram

**AI Caption Generator**
```
Staff provides: topic, tone, target audience, key message
       ↓
Claude API generates 3 caption variations
       ↓
Staff picks, edits, and schedules
```

```python
# AI caption generation
def generate_captions(topic, tone, audience, platform):
    prompt = f"""Generate 3 social media captions for {platform}.
    Topic: {topic}
    Tone: {tone}
    Target Audience: {audience}
    Requirements: Platform-appropriate length, include relevant hashtags,
    call-to-action where natural. Return as JSON array of 3 strings."""

    response = anthropic_client.messages.create(
        model="claude-opus-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return parse_captions(response.content[0].text)
```

**Content Calendar**
- Month-view calendar showing all scheduled posts
- Drag to reschedule
- Color-coded by platform

**Publishing Queue**
- Celery beat publishes posts at scheduled time via platform APIs
- Retry on failure (3 attempts, then alert)
- Published / Failed / Pending statuses

**Analytics**
- Pull basic post metrics from platform APIs (likes, reach, comments)
- Display in dashboard after posting

---

## 14. Dashboard & Analytics

### 14.1 Overview KPI Cards

The main dashboard shows cross-module KPIs configured by the company:

| KPI Card | Source Module |
|---|---|
| Revenue this month | Invoicing |
| Bookings today | Booking |
| Open support messages | Client Portal |
| Inventory low-stock alerts | Inventory |
| Pending onboarding tasks | Team |
| Reports submitted today | Field Reports |
| Survey responses this week | Surveys |
| Posts scheduled this week | Social Scheduler |

### 14.2 Charts & Reports

- Revenue trend (monthly bar chart)
- Bookings by service (donut chart)
- Stock level overview (horizontal bar)
- Survey NPS trend (line chart)
- Social engagement trend (line chart)

All charts powered by **Recharts** wrapped in shadcn/ui `Chart` component.

### 14.3 Public Share Link (Read-Only Preview)

Admins can share a read-only dashboard snapshot with stakeholders:

```
Admin clicks "Share Dashboard" on any report panel
       ↓
Signed token generated (URLSafeTimedSerializer)
       ↓
Token encodes: company_id, report_type, date_range, expiry
       ↓
URL: https://bizos.app/preview/{signed_token}
       ↓
Recipient sees read-only view, no login required
No PII — aggregated data only
Admin sets expiry: 1hr / 24hr / 7 days / one-time
Admin can revoke at any time
```

---

## 15. API Design

### 15.1 API Structure

```
Base URL: https://api.bizos.app/v1/

Auth:
  POST   /auth/login
  POST   /auth/refresh
  POST   /auth/logout
  POST   /auth/2fa/verify

Admin Dashboard:
  GET    /admin/dashboard/summary
  GET    /admin/analytics
  POST   /admin/analytics/share-link

Client Portal:
  GET    /portal/clients
  POST   /portal/clients
  GET    /portal/clients/{id}
  GET    /portal/clients/{id}/files
  POST   /portal/clients/{id}/files
  DELETE /portal/clients/{id}/files/{file_id}
  GET    /portal/clients/{id}/updates
  POST   /portal/clients/{id}/updates
  GET    /portal/clients/{id}/messages
  POST   /portal/clients/{id}/messages

Bookings:
  GET    /bookings
  POST   /bookings
  GET    /bookings/{id}
  PUT    /bookings/{id}
  DELETE /bookings/{id}
  GET    /bookings/availability
  POST   /bookings/public (no auth — public booking page)
  GET    /services
  POST   /services
  PUT    /services/{id}

Invoicing:
  GET    /invoices
  POST   /invoices
  GET    /invoices/{id}
  PUT    /invoices/{id}
  GET    /invoices/{id}/pdf
  POST   /invoices/{id}/send
  POST   /invoices/{id}/share-link
  POST   /invoices/{id}/void
  POST   /invoices/{id}/record-payment
  GET    /expenses
  POST   /expenses
  POST   /expenses/scan (AI receipt scan upload)

Inventory:
  GET    /inventory/products
  POST   /inventory/products
  PUT    /inventory/products/{id}
  GET    /inventory/locations
  POST   /inventory/locations
  POST   /inventory/adjustments
  POST   /inventory/transfers
  GET    /inventory/purchase-orders
  POST   /inventory/purchase-orders

Team:
  GET    /team/members
  POST   /team/members/invite
  PUT    /team/members/{id}
  GET    /team/onboarding/templates
  POST   /team/onboarding/templates
  GET    /team/members/{id}/onboarding
  POST   /team/members/{id}/onboarding/{task_id}/complete
  GET    /team/documents
  POST   /team/members/{id}/documents/request

Field Reports:
  GET    /reports
  POST   /reports
  GET    /reports/{id}
  PUT    /reports/{id}/review
  GET    /reports/export

Surveys:
  GET    /surveys
  POST   /surveys
  GET    /surveys/{id}
  PUT    /surveys/{id}
  POST   /surveys/{id}/send
  GET    /surveys/{id}/responses
  GET    /surveys/{id}/export

Social Scheduler:
  GET    /social/posts
  POST   /social/posts
  PUT    /social/posts/{id}
  DELETE /social/posts/{id}
  POST   /social/posts/generate-captions (AI)
  GET    /social/calendar
  GET    /social/accounts
  POST   /social/accounts/connect/{platform}

Users & Roles:
  GET    /users
  POST   /users/invite
  PUT    /users/{id}/activate
  PUT    /users/{id}/deactivate
  PUT    /users/{id}/role
  GET    /roles
  POST   /roles
  PUT    /roles/{id}
  DELETE /roles/{id}

Audit:
  GET    /logs (admin only)

Public (No Auth):
  GET    /preview/{token}           (shared dashboard)
  GET    /invoice/view/{token}      (shared invoice view)
  GET    /invoice/view/{token}/pdf  (shared invoice download)
  POST   /book/{company_slug}       (public booking submission)
  GET    /survey/{survey_token}     (public survey access)
  POST   /survey/{survey_token}/submit

Client Portal Auth (Separate):
  POST   /client/auth/login
  POST   /client/auth/register (via invite only)
  GET    /client/files
  GET    /client/updates
  GET    /client/invoices
  GET    /client/messages
  POST   /client/messages
```

### 15.2 API Response Format

```json
{
  "success": true,
  "data": { },
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 150
  },
  "message": "Invoice created successfully"
}
```

Error format:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The given data was invalid.",
    "details": {
      "email": ["Email already exists."],
      "amount": ["Amount must be greater than zero."]
    }
  }
}
```

---

## 16. Encryption & Audit Logs

### 16.1 Encryption Strategy

| Data Type | Encryption Method |
|---|---|
| User Passwords | bcrypt (rounds=12) — **never SHA2 or below** |
| PII in DB (Tax ID, gov IDs) | AES-256-GCM (SQLAlchemy encrypted column) |
| API Tokens (stored) | SHA-256 hash of token (one-way) |
| PDF/File storage | Server-side encryption (S3 SSE-S3) |
| Transport | TLS 1.3 only |
| Refresh Tokens | bcrypt hash stored; raw value sent to client once |
| Audit Log Entries | AES-256-GCM encrypted |
| Session tokens in Redis | HMAC-SHA256 fingerprint stored; raw token in HttpOnly cookie |

**Explicit Non-Use:** MD5, SHA1, SHA2 are **never used for passwords or user credentials**. They may only appear in non-security contexts (e.g., file integrity checksums).

### 16.2 Audit Log System

**What is logged:**
- All authentication events (login, logout, failed attempts, 2FA)
- All data mutations on sensitive models
- Permission changes (role assignment, activation/deactivation)
- Invoice actions (create, send, void, payment recorded)
- File access (downloads, share link generation)
- AI feature usage (receipt scans, caption generation)
- Admin actions (user management, log access)

```python
class AuditLog(db.Model):
    id                  = db.Column(db.UUID, primary_key=True, default=uuid4)
    company_id          = db.Column(db.Integer, db.ForeignKey('companies.id'))
    actor_id            = db.Column(db.Integer, db.ForeignKey('users.id'))
    actor_ip            = db.Column(db.String(45))     # IPv6 compatible
    action              = db.Column(db.String(100))    # e.g., 'invoice.sent'
    resource_type       = db.Column(db.String(50))
    resource_id         = db.Column(db.String(100))
    payload_encrypted   = db.Column(db.Text)           # AES-256-GCM JSON
    session_fingerprint = db.Column(db.String(64))     # HMAC of session
    created_at          = db.Column(db.DateTime, default=datetime.utcnow)
```

**Access Control:**
- Audit logs viewable **only by users with `logs.view` permission**
- Logs are append-only — no update or delete endpoints
- Log export requires 2FA re-authentication

**Retention:** 90 days hot (PostgreSQL), 2 years cold (S3 Glacier).

---

## 17. UI Design System — shadcn/ui · Dark Mode First

### 17.1 Philosophy & Approach

The entire UI — admin portal and client-facing portal — is built exclusively with **shadcn/ui** components (New York style). shadcn/ui is a copy-paste component collection built on **Radix UI primitives** and **Tailwind CSS v4**, meaning all UI code lives in the project's own codebase (`/components/ui/`) and is fully customizable.

**Design direction:** Linear.app meets Notion — clean, spacious, data-dense without being cluttered. Dark mode is the primary experience; light mode is equally polished.

### 17.2 Dark Mode — Default Behavior

Dark mode is applied to `<html>` on first load and persisted in `localStorage`. System preference (`prefers-color-scheme`) respected on first visit if no stored preference.

```typescript
// lib/theme.ts — runs before React mounts to prevent flash
const STORAGE_KEY = 'ui-theme';
export function initTheme() {
  const stored = localStorage.getItem(STORAGE_KEY);
  const theme = stored ?? 'dark';
  document.documentElement.classList.toggle('dark', theme === 'dark');
}
```

### 17.3 CSS Variable Token System

```css
@import "tailwindcss";
@import "tw-animate-css";
@custom-variant dark (&:is(.dark *));

@theme inline {
  --color-background:          var(--background);
  --color-foreground:          var(--foreground);
  --color-card:                var(--card);
  --color-primary:             var(--primary);
  --color-muted:               var(--muted);
  --color-muted-foreground:    var(--muted-foreground);
  --color-border:              var(--border);
  --color-chart-1:             var(--chart-1);
  --color-chart-2:             var(--chart-2);
  --color-chart-3:             var(--chart-3);
  --color-chart-4:             var(--chart-4);
  --color-chart-5:             var(--chart-5);
}

/* Dark (default) */
:root {
  --background:   oklch(0.10 0.01 240);
  --foreground:   oklch(0.97 0.00 0);
  --card:         oklch(0.14 0.01 240);
  --primary:      oklch(0.65 0.19 264);  /* indigo accent */
  --muted:        oklch(0.18 0.01 240);
  --border:       oklch(0.22 0.01 240);
  --chart-1:      oklch(0.65 0.19 264);
  --chart-2:      oklch(0.70 0.18 180);
  --chart-3:      oklch(0.75 0.18 84);
  --chart-4:      oklch(0.68 0.22 320);
  --chart-5:      oklch(0.72 0.20 145);
}

/* Light */
.light {
  --background:   oklch(0.97 0.00 240);  /* warm grey, not pure white */
  --foreground:   oklch(0.12 0.01 240);
  --card:         oklch(1.00 0.00 0);
  --primary:      oklch(0.50 0.19 264);
  --muted:        oklch(0.93 0.01 240);
  --border:       oklch(0.88 0.01 240);
}
```

### 17.4 shadcn/ui Component Inventory

```bash
npx shadcn@latest init
# New York style, Zinc base color, CSS variables: yes

npx shadcn@latest add button card input label select textarea
npx shadcn@latest add dialog sheet drawer popover dropdown-menu
npx shadcn@latest add table data-table pagination
npx shadcn@latest add form checkbox radio-group switch
npx shadcn@latest add badge avatar tooltip separator
npx shadcn@latest add sidebar navigation-menu breadcrumb
npx shadcn@latest add tabs accordion collapsible
npx shadcn@latest add alert alert-dialog toast sonner
npx shadcn@latest add command combobox calendar date-picker
npx shadcn@latest add progress skeleton
npx shadcn@latest add chart
```

| shadcn/ui Component | Used For |
|---|---|
| `Sidebar` + `SidebarMenu` | Main nav — admin portal |
| `Card` + `CardHeader` | KPI widgets, module panels |
| `DataTable` (`@tanstack/react-table`) | Bookings, invoices, inventory, team |
| `Chart` (Recharts wrapper) | Dashboard analytics |
| `Dialog` / `Sheet` | Create/edit forms (desktop vs mobile) |
| `Command` (⌘K) | Global search |
| `Form` + `react-hook-form` + `zod` | All forms |
| `Sonner` | Toast notifications |
| `Alert` / `AlertDialog` | Destructive confirmations |
| `Badge` | Invoice status, booking status, module tags |
| `Calendar` / `DatePicker` | Booking scheduler, invoice dates |
| `Combobox` | Assignee picker, client search |
| `Progress` | Onboarding completion bars |
| `Skeleton` | All async loading states |
| `Tabs` | Module detail views |
| `Switch` | Module toggles, feature flags in settings |

### 17.5 Frontend File Structure

```
src/
├── app/                        # Next.js App Router
│   ├── (admin)/                # Admin portal routes
│   │   ├── dashboard/
│   │   ├── portal/
│   │   ├── bookings/
│   │   ├── invoices/
│   │   ├── inventory/
│   │   ├── team/
│   │   ├── reports/
│   │   ├── surveys/
│   │   ├── social/
│   │   └── settings/
│   ├── (client)/               # Client portal routes
│   │   ├── files/
│   │   ├── updates/
│   │   ├── invoices/
│   │   └── messages/
│   └── (public)/               # No auth
│       ├── book/[slug]/
│       ├── survey/[token]/
│       ├── invoice/view/[token]/
│       └── preview/[token]/
├── components/
│   ├── ui/                     # shadcn/ui components (owned)
│   ├── modules/                # Module-specific components
│   │   ├── bookings/
│   │   ├── invoicing/
│   │   ├── inventory/
│   │   └── ...
│   └── shared/                 # Cross-module components
├── lib/
│   ├── api.ts                  # Axios instance + interceptors
│   ├── theme.ts                # Theme bootstrap
│   └── utils.ts                # cn() and helpers
├── hooks/                      # Custom React hooks
└── stores/                     # Zustand stores
```

---

## 18. Tech Stack & Dependencies

### 18.1 Backend (Flask)

```
Flask==3.1.x
Flask-SQLAlchemy==3.1.x        # ORM
Flask-Migrate==4.x              # DB migrations (Alembic)
Flask-JWT-Extended==4.6.x       # JWT auth
Flask-Bcrypt==1.0.x             # Password hashing
Flask-Limiter==3.x              # Rate limiting (Redis backend)
Flask-WTF==1.2.x                # CSRF protection
Flask-CORS==4.x                 # CORS handling
Flask-Mail==0.9.x               # Email sending
Celery==5.3.x                   # Async task queue
Redis==5.x                      # Cache, sessions, Celery broker
psycopg2-binary==2.9.x          # PostgreSQL driver
SQLAlchemy==2.x
itsdangerous==2.1.x             # Signed tokens / share links
WeasyPrint==61.x                # HTML-to-PDF invoice generation
Jinja2==3.1.x                   # PDF/email templates
Pillow==10.x                    # Image processing (receipts)
pyotp==2.9.x                    # TOTP 2FA
cryptography==42.x              # AES-256-GCM encryption
marshmallow==3.21.x             # Serialization / validation
anthropic==0.25.x               # Claude API (receipt scanner, AI captions)
stripe==8.x                     # Payment processing
boto3==1.34.x                   # S3/MinIO file storage
gunicorn==21.x                  # WSGI server
```

### 18.2 Frontend (Next.js)

```
# Core
next==15.x
react==19.x
typescript==5.x

# State & Data
@tanstack/react-query==5.x      # Server state caching
zustand==4.x                    # Client state (theme, sidebar)
axios==1.x                      # HTTP client

# UI — shadcn/ui ecosystem (ALL UI from here)
shadcn/ui                       # Component collection (New York style)
@radix-ui/react-*               # Radix UI primitives
tailwindcss==4.x                # Styling
tw-animate-css                  # shadcn animation utilities
lucide-react                    # Icons (shadcn default)
class-variance-authority (cva)  # Component variants
clsx + tailwind-merge           # cn() utility
cmdk                            # Command palette (⌘K)
next-themes                     # Theme persistence

# Charts
recharts==2.x                   # Via shadcn Chart wrapper

# Forms & Validation
react-hook-form==7.x
zod==3.x

# Other
@tanstack/react-table==8.x      # Headless table (shadcn DataTable)
sonner                          # Toast notifications
date-fns==3.x                   # Date utilities
react-dropzone==14.x            # File upload
@stripe/stripe-js               # Stripe frontend
```

### 18.3 Infrastructure

```
PostgreSQL 16          # Primary database
Redis 7                # Cache, sessions, Celery broker
Nginx                  # Reverse proxy, static file serving
Docker + Docker Compose # Containerization
GitHub Actions         # CI/CD
MinIO (or AWS S3)      # File storage
Let's Encrypt          # SSL/TLS
Celery Beat            # Scheduled tasks (social posting, alerts)
```

---

## 19. Database Schema

### 19.1 Core Tables

```sql
-- Multi-tenancy
companies (
  id, name, slug, industry, plan, logo_url,
  accent_color, custom_domain,
  settings_json, created_at, updated_at
)

company_modules (
  company_id, client_portal, bookings, invoicing,
  inventory, team_onboarding, field_reports,
  surveys, social_scheduler, updated_at
)

-- Staff Users
users (
  id, company_id, email, password_hash,
  first_name, last_name, phone,
  status [pending/active/suspended/deactivated],
  role_id, totp_secret_encrypted,
  last_login_at, activated_at, activated_by,
  created_at, updated_at
)

-- Client Portal Users
clients (
  id, company_id, email, password_hash,
  first_name, last_name, phone, company_name,
  status [pending/active/suspended],
  email_verified_at, created_at, updated_at
)

-- Roles & Permissions
roles (id, company_id, name, is_system_default, created_at)
permissions (id, namespace, action, description)
role_permissions (role_id, permission_id)

-- Client Portal
portal_files (
  id, company_id, client_id, uploaded_by,
  filename, file_url, file_size, mime_type,
  is_public, share_token, share_token_expires_at,
  created_at
)

portal_updates (
  id, company_id, client_id, author_id,
  title, body, status [in_progress/review/completed],
  created_at, updated_at
)

portal_messages (
  id, company_id, client_id, sender_id, sender_type,
  body, read_at, created_at
)

-- Bookings
services (
  id, company_id, name, description, duration_minutes,
  price, currency, buffer_minutes, max_per_slot,
  is_active, created_at
)

staff_availability (
  id, user_id, company_id, day_of_week,
  start_time, end_time, is_active
)

bookings (
  id, company_id, service_id, assigned_to,
  client_id, guest_name, guest_email, guest_phone,
  booking_date, start_time, end_time,
  status [pending/confirmed/completed/cancelled/no_show],
  payment_status, stripe_payment_intent_id,
  notes, invoice_id, created_at, updated_at
)

-- Invoicing
invoices (
  id, company_id, invoice_number, client_id,
  status [draft/sent/partial/paid/overdue/void],
  issue_date, due_date, currency,
  subtotal, discount_total, tax_total, total, paid_amount,
  notes, terms, pdf_url,
  share_token, share_token_expires_at,
  stripe_payment_link, sent_at, paid_at, void_at,
  created_by, created_at, updated_at
)

invoice_items (
  id, invoice_id, description, quantity,
  unit_price, discount_pct, tax_rate, line_total
)

expenses (
  id, company_id, submitted_by,
  vendor_name, amount, currency, expense_date,
  category, receipt_url, ai_extracted_data_json,
  status [pending_review/approved/rejected],
  invoice_id, created_at
)

-- Inventory
products (
  id, company_id, name, sku, category_id,
  description, unit_cost, sale_price, currency,
  reorder_threshold, barcode, is_active, created_at
)

inventory_locations (
  id, company_id, name, address, is_active
)

inventory_items (
  id, product_id, location_id, quantity, reserved_quantity
)

stock_movements (
  id, company_id, product_id, location_id,
  type [adjustment/transfer/purchase/sale],
  quantity_change, reason, reference_id, created_by, created_at
)

-- Team & Onboarding
employees (
  id, user_id, company_id, department,
  position, employment_type, start_date,
  status [active/on_leave/terminated], created_at
)

onboarding_templates (
  id, company_id, name, role_id, created_at
)

onboarding_tasks (
  id, template_id, title, description,
  due_offset_days, assignee_type [self/hr/manager], order_index
)

employee_onboarding (
  id, employee_id, task_id,
  status [pending/completed/skipped],
  completed_at, created_at
)

-- Field Reports
field_reports (
  id, company_id, submitted_by, report_type,
  job_site, report_date, hours_worked,
  work_summary, issues_noted, photos_json,
  gps_lat, gps_lng,
  status [draft/submitted/reviewed/flagged],
  reviewed_by, reviewed_at, created_at
)

-- Surveys
surveys (
  id, company_id, name, description,
  trigger [manual/post_appointment/post_payment/post_ticket],
  questions_json, branding_json,
  is_active, created_at
)

survey_responses (
  id, survey_id, respondent_email, answers_json,
  completed_at, created_at
)

-- Social Scheduler
social_accounts (
  id, company_id, platform [facebook/instagram/linkedin/twitter],
  account_name, access_token_encrypted, expires_at, created_at
)

social_posts (
  id, company_id, created_by,
  caption, media_urls_json, hashtags,
  scheduled_at, published_at,
  status [draft/scheduled/published/failed],
  platform_post_ids_json, created_at
)

-- Share Tokens
share_tokens (
  id, company_id, token_hash, type [report/invoice/file/survey],
  resource_id, config_json,
  expires_at, revoked_at, view_count, max_views,
  created_by, created_at
)

-- Audit Logs
audit_logs (
  id, company_id, actor_id, actor_ip,
  action, resource_type, resource_id,
  payload_encrypted, session_fingerprint, created_at
)
```

---

## 20. Non-Functional Requirements

### 20.1 Performance

| Metric | Target |
|---|---|
| API p95 response time | < 300ms |
| Dashboard load time | < 2 seconds |
| PDF generation time | < 5 seconds (async) |
| AI receipt scan time | < 8 seconds (async) |
| Concurrent users per tenant | 50 (starter), 500 (pro), 2000 (enterprise) |
| Database query time (p99) | < 100ms |
| File upload (50MB) | < 30 seconds |

### 20.2 Availability

- Uptime SLA: 99.9% (8.7 hours downtime/year)
- Maintenance windows: Sundays 2 AM – 4 AM local time
- Database backups: Every 6 hours, retained 30 days
- Disaster recovery RPO: 6 hours, RTO: 4 hours

### 20.3 Security Compliance

- OWASP Top 10 mitigation (required)
- GDPR-ready data handling (data export, right to deletion)
- PCI-DSS awareness (no raw card data stored — Stripe tokenization)
- Philippine Data Privacy Act (RA 10173) compliance for PH market

### 20.4 Browser & Device Support

- Chrome / Edge (last 2 versions)
- Firefox (last 2 versions)
- Safari (last 2 versions)
- Mobile: iOS Safari, Android Chrome (field reports are mobile-first)

### 20.5 Accessibility

- WCAG 2.1 AA for client-facing portal
- Keyboard navigation support across admin portal
- Screen reader compatible
- shadcn/ui is built on **Radix UI primitives** — WAI-ARIA compliant dialogs, dropdowns, and comboboxes out of the box

---

## 21. Deployment & DevOps

### 21.1 Docker Compose (Development)

```yaml
version: '3.9'
services:
  nginx:
    image: nginx:alpine
    ports: ["80:80", "443:443"]

  flask_api:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://...
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - JWT_PRIVATE_KEY=${JWT_PRIVATE_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
    depends_on: [postgres, redis]

  celery_worker:
    build: ./backend
    command: celery -A app.celery worker --loglevel=info -Q default,ai,pdf,social
    depends_on: [flask_api, redis]

  celery_beat:
    build: ./backend
    command: celery -A app.celery beat --loglevel=info
    depends_on: [flask_api, redis]

  next_admin:
    build: ./frontend/admin
    environment:
      - NEXT_PUBLIC_API_URL=http://flask_api:5000/v1

  next_client:
    build: ./frontend/client

  postgres:
    image: postgres:16
    volumes: [postgres_data:/var/lib/postgresql/data]

  redis:
    image: redis:7-alpine

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    volumes: [minio_data:/data]
```

### 21.2 Environment Variables (Required)

```bash
# App
SECRET_KEY=                    # Flask secret (64+ chars)
JWT_PRIVATE_KEY=               # RS256 private key (PEM)
JWT_PUBLIC_KEY=                # RS256 public key (PEM)
SHARE_LINK_SALT=               # Salt for URLSafeTimedSerializer

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname
REDIS_URL=redis://host:6379/0

# Encryption
LOG_ENCRYPTION_KEY=            # AES-256 key for audit log encryption
PII_ENCRYPTION_KEY=            # AES-256 key for PII fields

# Email
MAIL_SERVER=
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=

# AI
ANTHROPIC_API_KEY=             # Claude API

# Payments
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_PUBLISHABLE_KEY=

# Storage
S3_ENDPOINT=
S3_ACCESS_KEY=
S3_SECRET_KEY=
S3_BUCKET=

# Social APIs
META_APP_ID=
META_APP_SECRET=
LINKEDIN_CLIENT_ID=
LINKEDIN_CLIENT_SECRET=

# Security
BCRYPT_ROUNDS=12
SESSION_LIFETIME_MINUTES=1440
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15
```

### 21.3 CI/CD Pipeline (GitHub Actions)

```
Push to main →
  Lint (flake8, eslint) →
  Unit Tests (pytest, jest) →
  Security Scan (bandit, npm audit) →
  Build Docker Images →
  Push to Registry →
  Deploy to Staging →
  Smoke Tests →
  Manual Approval →
  Deploy to Production
```

---

## 22. Monetization & Subscription Tiers

### 22.1 Pricing Tiers

| Feature | Starter ($49/mo) | Pro ($99/mo) | Agency ($249/mo) |
|---|---|---|---|
| Staff accounts | 3 | 10 | Unlimited |
| Client portal accounts | 5 | 25 | Unlimited |
| Active modules | 3 | All | All |
| File storage | 5GB | 25GB | 100GB |
| AI receipt scans | 20/mo | 100/mo | Unlimited |
| AI caption generations | 30/mo | Unlimited | Unlimited |
| Bookings/mo | 100 | Unlimited | Unlimited |
| Invoices/mo | 20 | Unlimited | Unlimited |
| Multi-location inventory | ✗ | ✓ | ✓ |
| Custom domain | ✗ | ✓ | ✓ |
| Priority support | ✗ | ✓ | ✓ |
| White-label branding | ✗ | ✗ | ✓ |
| API access | ✗ | ✗ | ✓ |

### 22.2 Add-ons

- Additional staff seat: $8/mo
- Additional 10GB storage: $5/mo
- SMS notifications (via Twilio): $0.05/SMS

---

## 23. Future Roadmap

### Phase 2 (Months 4–6)
- **Payment Gateway Expansion** — PayMongo (PH), Maya Business, GCash
- **Mobile App (React Native)** — Field reports, bookings, and client portal
- **Webhook System** — Outbound webhooks for third-party integrations
- **Zapier / Make Integration** — No-code automation triggers
- **Email Marketing** — Campaign builder with segment targeting

### Phase 3 (Months 7–12)
- **Multi-Branch Support** — Separate inventory, bookings, and staff per branch
- **AI-Powered Insights** — Revenue forecasting, churn risk, anomaly detection
- **Custom Report Builder** — Drag-and-drop analytics with export
- **Loyalty & Rewards Program** — Points, tiers, referral codes
- **Third-Party Integrations** — QuickBooks, Xero, Google Workspace, Slack

### Phase 4 (Year 2)
- **White-Label Offering** — Fully rebrandable platform for agencies
- **Marketplace App Store** — Third-party plugins and extensions
- **Enterprise SSO** — SAML 2.0, Azure AD, Okta
- **Advanced Fraud Detection** — ML-based anomaly scoring on transactions
- **AI Assistant (BizOS Copilot)** — Natural language queries across all modules

---

## Appendix A: Security Checklist

- [x] bcrypt (rounds=12) for all passwords — no SHA2 or below for credentials
- [x] JWT with RS256 asymmetric keys
- [x] Separate JWT issuer salt for client portal users
- [x] CSRF protection on all state-changing endpoints
- [x] Rate limiting on auth endpoints (Redis-backed)
- [x] SQL injection prevention (ORM only, no raw queries)
- [x] XSS prevention (Next.js escaping + CSP headers)
- [x] Staff accounts deactivated by default
- [x] Client portal accounts separate from staff accounts
- [x] Audit logs encrypted with AES-256-GCM
- [x] Audit logs accessible by admin-role only
- [x] Passwords never appear in logs
- [x] HTTPS/TLS 1.3 enforced
- [x] Signed, revocable public share tokens
- [x] 2FA required for Owner and Super Admin
- [x] Session invalidation on password change
- [x] PII fields encrypted at rest
- [x] AI API keys stored server-side only — never exposed to frontend
- [x] Stripe webhooks verified via signature

---

## Appendix B: UI / Design System Checklist

- [x] Dark mode applied by default via `dark` class on `<html>` — no flash of light mode
- [x] Theme preference persisted in `localStorage` via `next-themes`
- [x] System preference (`prefers-color-scheme`) respected on first visit
- [x] All UI components from **shadcn/ui** (New York style)
- [x] CSS variable tokens for all semantic colors
- [x] OKLCH color space used throughout (Tailwind v4 default)
- [x] Light mode uses warm grey base (`oklch(0.97)`) — not pure white
- [x] Chart colors readable in both dark and light themes
- [x] `Skeleton` loaders for all async content
- [x] `AlertDialog` required before all destructive actions
- [x] `Command` palette (⌘K) available globally
- [x] `Sheet` for forms on mobile, `Dialog` on desktop
- [x] `Sonner` for all toast notifications
- [x] `Inter` font via CSS
- [x] Lucide icons used consistently
- [x] Radix UI primitives ensure ARIA compliance

---

## Appendix C: Module Dependency Map

Some modules share data and trigger cross-module actions:

```
Booking completed
  → auto-send Survey (if Surveys module on)
  → auto-generate Invoice (if Invoicing module on)
  → log Activity in Client Portal

Invoice paid
  → auto-send Survey (if configured)
  → update Client Portal status

Field Report submitted
  → notify Manager (Team module)
  → link to Job/Site (Inventory if applicable)

Social Post published
  → log to Audit Log
  → update Analytics dashboard
```

---

## Appendix D: Glossary

| Term | Definition |
|---|---|
| **shadcn/ui** | Open-source, copy-paste React component collection built on Radix UI + Tailwind |
| **New York style** | shadcn/ui's refined preset — sharper borders, denser spacing, ideal for admin UIs |
| **OKLCH** | Perceptually uniform color space used by Tailwind v4 |
| **Radix UI** | Headless, accessible UI primitives underpinning shadcn/ui |
| **Tenant** | A company (business) using the BizOS platform |
| **Module** | A feature bundle that can be independently activated per tenant |
| **Client** | An external client of the business using the Client Portal |
| **Share Token** | Signed URL token for public, read-only access to reports, invoices, or files |
| **SLA** | Service Level Agreement — response/resolution commitments |
| **CSAT** | Customer Satisfaction score |
| **NPS** | Net Promoter Score |
| **Celery Beat** | Celery's periodic task scheduler (social posting, low-stock checks, reminders) |
| **bcrypt** | Password hashing algorithm — the only approved hash for credentials |
| **AES-256-GCM** | Symmetric encryption used for audit logs and PII fields |
| **PO** | Purchase Order — a formal request to a supplier |

---

*Document Owner: BizOS Platform Architecture Team*  
*Version 1.0.0 — Initial Release*  
*Review Cycle: Quarterly*  
*Next Review: May 2026*
