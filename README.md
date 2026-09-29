# Baghewala Field Intelligence

Hackathon-ready MVP for an integrated well-to-surface digital twin focused on heavy-oil production at the Baghewala Field in Rajasthan. The application connects reservoir conditions, cyclic steam stimulation (CSS), sucker-rod pumping (SRP), production, operational alerts, and simulated optimization recommendations in one field operations workspace.

> **DEMO DATA:** All well records, time series, alerts, and model outputs included with this project are synthetic demonstrations. The predictions are not trained on Baghewala field history, have no accuracy guarantee, and are not operating instructions. Human review is required before any operational action.

## Field Context

The demonstration represents 17–19° API heavy crude from the Jodhpur Sandstone reservoir. The operating scenario models high viscosity and asphaltene content, low reservoir pressure, low reservoir temperature (typically 46–48°C before steam response), and poor primary oil mobility. CSS and artificial lift are therefore considered together: cooling after a steam cycle can increase viscosity, reduce pump fillage and efficiency, increase energy demand, and contribute to rod loading, floating, impact, pump unsetting, and equipment failure risk.

The MVP is intended to demonstrate how historical production, CSS records, SRP/VFD signals, reservoir measurements, fluid properties, and equipment events could support integrated monitoring and decision-making.

## What Is Included

- Role-selectable login for Admin, Operations Manager, and Field Engineer, backed by expiring JWTs when the API is available.
- Executive overview with field production, per-well production, reservoir temperature, viscosity, steam, SOR, energy intensity, high-risk wells, predicted failures, production trends, and recent alerts.
- Searchable and risk-filterable well table with 24 simulated wells.
- Well digital twin showing the reservoir-to-surface path, thermal zone, wellbore, SRP, operating metrics, and production trend.
- CSS scenario form comparing current cycle inputs with simulated steam, pressure, soak, production, SOR, recovery, and energy outcomes. The calculate action calls the FastAPI CSS optimizer when connected.
- SRP optimization and pump-card views, rod-floating detection, reliability risk ranking, production forecasting, steam and energy analytics, advanced analytics, alerts, and AI recommendations.
- Alert acknowledgement and resolution actions, and human approval/decline actions for recommendations.
- Architecture view of the data, processing, model, digital-twin, and decision-support layers.
- FastAPI endpoints, a centralized frontend demo-data module, and a PostgreSQL-oriented starting schema.

### Current Integration Boundaries

The well list is fetched from FastAPI after login and falls back to the local dataset when the API cannot be reached. CSS optimization also calls its API endpoint. Other charts, alert states, and several module scenarios currently use centralized frontend demo fixtures or fixed backend simulations; they are not connected to live telemetry, a trained model, or a database. The SRP, failure-risk, rod-floating, recommendations, and analytics endpoints are available for integration, but their corresponding views still use demonstration behavior in places.

## Roles

| Capability | Admin | Operations Manager | Field Engineer |
| --- | --- | --- | --- |
| View all wells and field overview | Yes | Yes | Assigned demo wells only |
| Digital twin and SRP/rod monitoring | Yes | Yes | Yes |
| CSS optimization | Yes | Yes | Not shown in navigation |
| Failure prediction, alerts, recommendations | Yes | Yes | Yes |
| Production forecast, steam/energy, analytics | Yes | Yes | Not shown in navigation |
| Approve or decline AI recommendations | Yes | Yes | No |
| Manage users and settings | Yes | No | No |

The Field Engineer demo assignment includes BGL-005, BGL-008, BGL-012, BGL-014, and BGL-019. This is a UI demonstration scope, not database-backed assignment management. FastAPI currently protects routes by role for CSS optimization and field analytics; additional production authorization checks are required for every resource and well assignment.

## Demo Sign-In

All three demo accounts use the same demonstration password:

| Role | Email | Password |
| --- | --- | --- |
| Admin | `admin@baghewala.in` | `demo-field-2026` |
| Operations Manager | `ops.manager@baghewala.in` | `demo-field-2026` |
| Field Engineer | `field.engineer@baghewala.in` | `demo-field-2026` |

The backend signs an HS256 JWT with an eight-hour expiry. If the API is unavailable, the frontend permits a local demonstration session and uses its fallback data. These accounts and the fallback signing secret are for local demonstration only.

## Technology

- **Frontend:** React, TypeScript, Vite, Tailwind CSS, Recharts, Lucide icons.
- **Backend:** Python 3.11+, FastAPI, Pydantic, PyJWT, Uvicorn.
- **Data:** In-memory deterministic demo records in the current API; frontend demo fixtures in `src/data.ts`.
- **Database starting point:** PostgreSQL DDL in `backend/schema.sql`. No live database connection or persistence layer is configured in the MVP.
- **ML integration point:** Deterministic simulation functions in `backend/main.py`; there are no trained Random Forest, XGBoost, regression, time-series, or anomaly-detection models in this demo.

## Run Locally

Use two terminals from the project root.

### Frontend

```powershell
npm install
npm run dev
```

Open `http://localhost:5173`. Vite proxies `/api` requests to `http://127.0.0.1:8000`.

### FastAPI Backend

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
python -m uvicorn backend.main:app --reload
```

The API listens on `http://127.0.0.1:8000`. Interactive endpoint documentation is available at `http://127.0.0.1:8000/docs`. The frontend can run without this service using the local fallback dataset, but API-backed login, well loading, and CSS optimization require the backend.

### Build the Frontend

```powershell
npm run build
npm run preview
```

The production assets are written to `dist/`. The current build succeeds; Vite reports an advisory that the chart-heavy JavaScript bundle exceeds its default 500 kB warning threshold.

## API Reference

All routes are prefixed with `/api`. Except for health and login, routes require `Authorization: Bearer <access_token>`.

### Session and Health

| Method | Route | Access | Purpose |
| --- | --- | --- | --- |
| `GET` | `/api/health` | Public | Service health and demo-mode marker. |
| `POST` | `/api/auth/login` | Public | Validate a demo email/password/role and issue an expiring JWT. |

Login JSON body:

```json
{
  "username": "ops.manager@baghewala.in",
  "password": "demo-field-2026",
  "role": "OPERATIONS_MANAGER"
}
```

### Wells and Time Series

| Method | Route | Access | Purpose |
| --- | --- | --- | --- |
| `GET` | `/api/wells` | Authenticated | Return the 24 demo wells. |
| `GET` | `/api/wells/{well_id}` | Authenticated | Return one well and its demo operating values. |
| `GET` | `/api/wells/{well_id}/production` | Authenticated | Return a 30-day production and water-cut series. |
| `GET` | `/api/wells/{well_id}/temperature` | Authenticated | Return an 18-week temperature series. |
| `GET` | `/api/wells/{well_id}/srp` | Authenticated | Return demo SRP settings and pump indicators. |
| `GET` | `/api/wells/{well_id}/css` | Authenticated | Return the demo CSS cycle record. |
| `GET` | `/api/wells/{well_id}/alerts` | Authenticated | Return demo alerts for a well. |

### Optimization and AI Simulation

| Method | Route | Access | Purpose |
| --- | --- | --- | --- |
| `POST` | `/api/ai/css-optimize` | Admin, Operations Manager | Return simulated thermal, production, SOR, recovery, and CSS parameter recommendations. |
| `POST` | `/api/ai/srp-optimize` | Authenticated | Return simulated stroke, SPM, VFD, efficiency, production, and energy recommendations. |
| `POST` | `/api/ai/failure-prediction` | Authenticated | Return a simulated failure-risk example. |
| `POST` | `/api/ai/rod-floating` | Authenticated | Return a simulated rod-floating classification and suggested review actions. |
| `GET` | `/api/ai/recommendations` | Authenticated | Return a simulated recommendation example. |

CSS optimization request example:

```json
{
  "steam_volume": 420,
  "injection_pressure": 85,
  "injection_hours": 36,
  "soak_hours": 72,
  "cut_off_bopd": 35,
  "reservoir_temperature": 49,
  "reservoir_pressure": 31,
  "viscosity_cp": 2180
}
```

Every prediction response uses the `AI SIMULATION / DEMO MODEL` marker and includes illustrative values only.

### Analytics

| Method | Route | Access | Purpose |
| --- | --- | --- | --- |
| `GET` | `/api/analytics/production` | Admin, Operations Manager | Return 12 monthly demo production points. |
| `GET` | `/api/analytics/steam` | Admin, Operations Manager | Return 12 monthly demo steam and SOR points. |
| `GET` | `/api/analytics/energy` | Admin, Operations Manager | Return 12 monthly demo energy-intensity points. |

Authenticated requests must include the JWT in the bearer header. Unauthorized requests return `401`; authenticated roles without access return `403`.

## PostgreSQL Starting Schema

`backend/schema.sql` defines the following relational entities and indexes:

- `users` and `wells`
- `reservoir_data` and `production_data`
- `css_cycles` and `srp_data`
- `rod_events` and `pump_events`
- `failure_predictions` and `alerts`
- `ai_recommendations` and `maintenance_records`
- Time-series indexes for reservoir, production, SRP, rod, pump, failure, alert, and CSS-cycle access patterns

The schema is a starting point only. The running API currently reads in-memory demo data; it does not create tables, open a PostgreSQL connection, or persist changes. Apply the DDL through a migration system and implement a repository/data-access layer before connecting field data.

## Data and Model Assumptions

- The frontend fallback dataset contains 24 wells with illustrative production, 49–63°C temperatures, low pressure, elevated viscosity, CSS/SRP settings, efficiency, risk, and rod/pump indicators.
- BGL-014 is the demonstration critical case, with low temperature, high viscosity, elevated rod load, low pump fillage, and high SOR.
- Demo charts and event scenarios are deterministic examples for a presentation workflow.
- Simulated optimization outputs must not be interpreted as measured savings, verified failure probabilities, or guaranteed operating improvements.
- Model confidence values, when present, are illustrative metadata and not empirical accuracy scores.

## Architecture and Extension Points

```text
Field / historical sources
  -> validation, cleaning, feature engineering, time alignment
  -> replaceable API repository and model services
  -> reservoir + CSS + wellbore + SRP + production digital twin
  -> forecasts, alerts, recommendations, optimization scenarios
  -> human approval and maintenance workflow
```

The current project keeps the API, deterministic simulation functions, and frontend fallback data separate enough to replace incrementally. A production implementation should add adapters for historian/SCADA/VFD/production data, PostgreSQL repositories and migrations, model versioning, calibration and backtesting, audit trails, and monitored human approval workflows. Do not connect model output directly to field control commands.

## Security and Production Readiness

Before any deployment beyond a local demonstration:

1. Set `BAGHEWALA_JWT_SECRET` to a strong, unique secret using the deployment secret manager. The code has an intentionally insecure local fallback so the demo can start easily.
2. Replace hard-coded demo identities and shared demonstration credentials with a managed identity provider, individual password hashes, password reset, revocation, and account lifecycle management.
3. Enforce well-level authorization on every API request; the current field engineer assignment is only a frontend demonstration filter.
4. Connect PostgreSQL through a least-privilege service account and migration process; add transactions, retention policy, backup, and restore testing.
5. Add audit logging, input validation against field operating envelopes, API rate limits, TLS, monitoring, and reviewed approval records.
6. Validate every predictive model against representative field data and document uncertainty, operating limits, and rollback procedures.

## Project Layout

```text
backend/
  main.py          FastAPI app, demo repository, JWT/RBAC, simulated model endpoints
  requirements.txt Python backend dependencies
  schema.sql       PostgreSQL starting schema
src/
  App.tsx          Application shell, role views, workflows, and page components
  data.ts          Central demo fixtures and API well-data adapter
  main.tsx         React entry point
  styles.css       Responsive operations-console design system
index.html         Vite HTML entry point
vite.config.ts    Vite dev server and /api proxy
```

## Verification Performed

- `npm run build` completes successfully.
- FastAPI checks verified public health, rejected unauthenticated well access (`401`), valid JWT access to wells and CSS optimization, and denied Field Engineer access to manager-only analytics (`403`).
- Authenticated well history returned 30 production points and 18 temperature points; analytics returned 12 monthly points.
- Browser checks exercised role-specific navigation, a 24-well Operations Manager view, the five-well Field Engineer view, BGL-014 digital-twin navigation, CSS scenario generation and approval messaging, and a 390px viewport without horizontal overflow.
