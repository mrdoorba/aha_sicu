# Store ICU - Project Overview

**Generated:** 2026-02-16 | **Scan Level:** Exhaustive | **Mode:** Initial Scan

## Executive Summary

Store ICU (AHA SICU) is a **brand health evaluation system** for Shopee e-commerce stores. It enables Business Development (BD) team members to evaluate brand performance across operational, business, content, and advertising dimensions using a structured scoring framework. The system ingests data from Google Sheets (VP & Meeting data), uploaded Shopee reports (CPC Ad, Keyword, Order Export, Mass Update), and manual inputs to produce standardized health scores with actionable recommendations.

## Project Identity

| Field | Value |
|-------|-------|
| **Project Name** | Store ICU (AHA SICU) |
| **Repository** | HandersThe/aha_sicu |
| **Repository Type** | Multi-part monorepo |
| **Primary Language** | TypeScript (Frontend), Python (Backend) |
| **Architecture** | Client-server with independent deployment pipelines |
| **Cloud Provider** | Google Cloud Platform (GCP) |
| **Region** | asia-southeast1 (Singapore) |

## Parts Overview

| Part | Type | Technology | Purpose |
|------|------|-----------|---------|
| **frontend** | Web SPA | React 19, TypeScript 5.9, Vite 7.2 | User-facing evaluation interface |
| **backend** | REST API | Python 3.14, FastAPI 0.115+ | Business logic, scoring engine, data management |
| **infrastructure** | IaC | Terraform, GCP | Cloud resource provisioning |
| **smoke-tests** | Testing | Playwright | Production verification |

## Core Workflow

1. **Brand Data Sync** - VP & Meeting data synced from Google Sheets to PostgreSQL
2. **Brand Selection** - BD team member browses and selects a brand to evaluate
3. **Manual Data Entry** - 9 sections of operational/business metrics entered by hand
4. **File Upload** - 4 Shopee report types uploaded (CPC Ad, Keyword, Order Export, Mass Update)
5. **Calculator Execution** - 3 automated calculators analyze uploaded data (Ads/Keyword, Top SKU, Discount)
6. **Score Generation** - 75-row scoring template produces final score across 11 categories
7. **Verdict & Output** - Score + verdict + email/WhatsApp templates generated
8. **Save & History** - Evaluation saved as immutable snapshot, viewable in history

## Key Features

- **Role-based access**: admin, leader, member roles with Firebase Auth
- **Real-time updates**: Server-Sent Events (SSE) for sync status and new evaluations
- **Auto-save**: Debounced form auto-save (500ms) for evaluation inputs
- **Configurable scoring**: Leader/admin can edit scoring rules with password confirmation
- **Multi-environment**: dev and prod deployments with CI/CD automation
- **Dual auth**: Firebase tokens for users, OIDC for Cloud Scheduler service calls

## Technology Stack Summary

### Frontend
React 19 + TypeScript 5.9 + Vite 7.2 + Tailwind CSS 4.1 + Radix UI + TanStack (React Query & Table) + React Hook Form + openapi-fetch + Firebase Auth + Vitest

### Backend
Python 3.14 + FastAPI + Uvicorn + asyncpg + PostgreSQL (Neon) + Alembic + Polars + Firebase Admin + Google Sheets API + SSE-Starlette + Pytest + Ruff

### Infrastructure
Terraform + GCP (Cloud Run + Firebase Hosting + Artifact Registry + Cloud Storage + Secret Manager + Cloud Scheduler) + GitHub Actions CI/CD

## Environments

| Environment | Frontend URL | Backend | Database |
|-------------|-------------|---------|----------|
| **dev** | aha-sicu-dev.web.app | Cloud Run (0-2 instances, 512Mi) | Neon PostgreSQL |
| **prod** | aha-sicu-prod.web.app | Cloud Run (1-4 instances, 512Mi) | Neon PostgreSQL |

## Links to Detailed Documentation

- [Architecture - Frontend](./architecture-frontend.md)
- [Architecture - Backend](./architecture-backend.md)
- [Architecture - Infrastructure](./architecture-infrastructure.md)
- [API Contracts](./api-contracts.md)
- [Data Models](./data-models.md)
- [Source Tree Analysis](./source-tree-analysis.md)
- [Component Inventory](./component-inventory.md)
- [Development Guide](./development-guide.md)
- [Integration Architecture](./integration-architecture.md)
- [Calculator Logic Reference](./calculator-logic-reference.md) *(existing)*
- [Deployment Guide](./deployment-guide.md) *(existing)*
- [Onboarding Guide](./onboarding-guide.md) *(existing)*
