# Store ICU - Project Documentation Index

**Generated:** 2026-02-16 | **Scan Level:** Exhaustive | **Workflow:** document-project v1.2.0

## Project Overview

- **Type:** Multi-part monorepo with 3 main parts + testing component
- **Primary Languages:** TypeScript (Frontend), Python (Backend), HCL (Infrastructure)
- **Architecture:** Client-server with independent deployment pipelines on GCP
- **Purpose:** Brand health evaluation system for Shopee e-commerce stores

## Quick Reference

### Frontend (web)
- **Tech Stack:** React 19, TypeScript 5.9, Vite 7.2, Tailwind CSS 4.1, Firebase Auth
- **Entry Point:** `frontend/src/main.tsx`
- **Architecture:** Component-based SPA with React Query for server state

### Backend (backend)
- **Tech Stack:** Python 3.14, FastAPI 0.115+, asyncpg, PostgreSQL (Neon), Alembic
- **Entry Point:** `backend/app/main.py`
- **Architecture:** Modular service-based API with pure function calculators

### Infrastructure (infra)
- **Tech Stack:** Terraform, GCP (Cloud Run, Firebase Hosting, Cloud Storage, Secret Manager)
- **Entry Point:** `infrastructure/terraform/main.tf`
- **Architecture:** Cloud-native serverless with environment-based deployments (dev/prod)

---

## Generated Documentation

### Overview & Architecture
- [Project Overview](./project-overview.md) — Executive summary, tech stack, core workflow
- [Architecture - Frontend](./architecture-frontend.md) — React SPA architecture, state management, component patterns
- [Architecture - Backend](./architecture-backend.md) — FastAPI modules, calculator engine, auth, database
- [Architecture - Infrastructure](./architecture-infrastructure.md) — Terraform resources, CI/CD pipelines, environments
- [Integration Architecture](./integration-architecture.md) — How parts communicate, data flow diagrams

### Technical Reference
- [API Contracts](./api-contracts.md) — All REST endpoints with request/response schemas
- [Data Models](./data-models.md) — Database schema, 9 tables, migration history
- [Component Inventory](./component-inventory.md) — 45+ React components, 13+ hooks, UI primitives
- [Source Tree Analysis](./source-tree-analysis.md) — Annotated directory tree with critical paths

### Development
- [Development Guide](./development-guide.md) — Setup, commands, environment variables, workflows

---

## Existing Documentation

- [Calculator Logic Reference](./calculator-logic-reference.md) — Complete 75-row scoring system replication guide (37KB)
- [Deployment Guide](./deployment-guide.md) — GCP deployment instructions, Cloud Run, Firebase Hosting
- [Onboarding Guide](./onboarding-guide.md) — BD team walkthrough: login, sync, upload, evaluate, score (27KB)
- [Launch Readiness](./launch-readiness.md) — Pre-launch validation checklist template
- [Validation Report Template](./validation-report-template.md) — Brand validation report template
- [Root README](../README.md) — Project overview with quick start
- [Terraform README](../infrastructure/terraform/README.md) — Infrastructure provisioning guide
- [Smoke Tests README](../smoke-tests/README.md) — API smoke test setup
- [Manual Checklist](../smoke-tests/MANUAL_CHECKLIST.md) — Manual smoke test checklist

---

## Getting Started

### For Developers
1. Read the [Development Guide](./development-guide.md) for setup instructions
2. Review [Architecture - Backend](./architecture-backend.md) or [Architecture - Frontend](./architecture-frontend.md) for the part you're working on
3. Check [API Contracts](./api-contracts.md) for endpoint details
4. Review [Data Models](./data-models.md) for database schema

### For New Features
1. Start with [Project Overview](./project-overview.md) to understand the system
2. Review the [Integration Architecture](./integration-architecture.md) to understand data flow
3. Check [Component Inventory](./component-inventory.md) for reusable UI components
4. Reference [Calculator Logic Reference](./calculator-logic-reference.md) for scoring details

### For Deployment
1. Follow the [Deployment Guide](./deployment-guide.md)
2. Review [Architecture - Infrastructure](./architecture-infrastructure.md) for Terraform resources
3. Use [Launch Readiness](./launch-readiness.md) checklist before go-live

### For AI-Assisted Development
Point your AI tool to this `index.md` file as the primary context source. For specific tasks:
- **UI changes:** Load `architecture-frontend.md` + `component-inventory.md`
- **API changes:** Load `architecture-backend.md` + `api-contracts.md`
- **Database changes:** Load `data-models.md` + `architecture-backend.md`
- **Full-stack features:** Load `integration-architecture.md` + both architecture docs
- **Scoring changes:** Load `calculator-logic-reference.md` + `architecture-backend.md`
