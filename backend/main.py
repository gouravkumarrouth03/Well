from __future__ import annotations

import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Literal

import jwt
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field

app = FastAPI(title="Baghewala Field Intelligence API", version="1.0.0", description="Simulated demo API; prediction outputs are not trained field models.")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_methods=["*"], allow_headers=["*"])

JWT_SECRET = os.getenv("BAGHEWALA_JWT_SECRET", "local-demo-secret-change-before-deployment")
JWT_ALGORITHM = "HS256"
DEMO_PASSWORD_HASH = hashlib.sha256("demo-field-2026".encode()).hexdigest()
DEMO_USERS = {
    "admin@baghewala.in": {"password_hash": DEMO_PASSWORD_HASH, "role": "ADMIN", "display_name": "A. Kumar"},
    "ops.manager@baghewala.in": {"password_hash": DEMO_PASSWORD_HASH, "role": "OPERATIONS_MANAGER", "display_name": "P. Mehta"},
    "field.engineer@baghewala.in": {"password_hash": DEMO_PASSWORD_HASH, "role": "FIELD_ENGINEER", "display_name": "R. Singh"},
}
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

def current_principal(token: str | None = Depends(oauth2_scheme)) -> dict:
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required", headers={"WWW-Authenticate": "Bearer"})
    try:
        claims = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError as error:
        raise HTTPException(status_code=401, detail="Invalid or expired token", headers={"WWW-Authenticate": "Bearer"}) from error
    if claims.get("role") not in {"ADMIN", "OPERATIONS_MANAGER", "FIELD_ENGINEER"}:
        raise HTTPException(status_code=401, detail="Invalid token role")
    return claims

def require_roles(*allowed_roles: str):
    def authorize(principal: dict = Depends(current_principal)) -> dict:
        if principal["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient role permissions")
        return principal
    return authorize

WELLS = [
    {"id": f"BGL-{i:03d}", "name": f"Baghewala {i:02d}", "status": "Producing", "oil_bopd": 96 - (i * 11 % 43), "temperature_c": 49 + i % 15, "pressure_bar": 31 + i % 16, "viscosity_cp": 890 + i * 53 % 1300, "spm": round(6.3 + i % 18 / 10, 1), "stroke_in": 80 + i % 13, "vfd_hz": 41 + i % 9, "steam_ton": 41 + i * 7 % 32, "sor": round(3.2 + i % 20 / 10, 1), "pump_efficiency": 58 + i * 7 % 31, "risk": "CRITICAL" if i == 14 else ("HIGH RISK" if i in (5, 12, 17) else "NORMAL")} for i in range(1, 25)
]
WELLS[13].update({"status": "Attention", "oil_bopd": 58, "temperature_c": 49, "pressure_bar": 31, "viscosity_cp": 2180, "sor": 5.4, "pump_efficiency": 58})
ALERTS = [{"id": 1, "well": "BGL-014", "severity": "critical", "title": "Rod floating signature detected", "status": "OPEN", "detected_at": datetime.now(timezone.utc).isoformat()}]

class LoginRequest(BaseModel):
    username: str
    password: str
    role: Literal["ADMIN", "OPERATIONS_MANAGER", "FIELD_ENGINEER"]

class CssRequest(BaseModel):
    steam_volume: float = Field(gt=0)
    injection_pressure: float = Field(gt=0)
    injection_hours: float = Field(gt=0)
    soak_hours: float = Field(gt=0)
    cut_off_bopd: float = Field(gt=0)
    reservoir_temperature: float
    reservoir_pressure: float
    viscosity_cp: float = Field(gt=0)

class SrpRequest(BaseModel):
    stroke_in: float = Field(gt=0)
    spm: float = Field(gt=0)
    vfd_hz: float = Field(gt=0)
    rod_load_kn: float = Field(gt=0)
    pump_fillage_pct: float = Field(ge=0, le=100)
    fluid_level_m: float = Field(gt=0)
    viscosity_cp: float = Field(gt=0)
    production_bopd: float = Field(ge=0)
    bottomhole_pressure_bar: float = Field(gt=0)

@app.get("/api/health")
def health():
    return {"status": "ok", "mode": "DEMO DATA"}

@app.post("/api/auth/login")
def login(payload: LoginRequest):
    user = DEMO_USERS.get(payload.username.strip().lower())
    supplied_hash = hashlib.sha256(payload.password.encode()).hexdigest()
    if not user or not secrets.compare_digest(user["password_hash"], supplied_hash) or payload.role != user["role"]:
        raise HTTPException(401, "Invalid demo credentials")
    token = jwt.encode({"sub": payload.username.strip().lower(), "role": user["role"], "exp": datetime.now(timezone.utc) + timedelta(hours=8)}, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return {"access_token": token, "token_type": "bearer", "role": user["role"], "display_name": user["display_name"]}

@app.get("/api/wells")
def list_wells(principal: dict = Depends(current_principal)):
    return {"mode": "DEMO DATA", "items": WELLS}

@app.get("/api/wells/{well_id}")
def get_well(well_id: str, principal: dict = Depends(current_principal)):
    well = next((item for item in WELLS if item["id"] == well_id), None)
    if not well:
        raise HTTPException(404, "Well not found")
    return {**well, "mode": "DEMO DATA", "fluid_level_m": 236, "water_cut_pct": 28, "rod_load_kn": 31.4, "steam_pressure_bar": 82, "energy_kwh_bbl": 42}

@app.get("/api/wells/{well_id}/{series}")
def get_well_series(well_id: str, series: str, principal: dict = Depends(current_principal)):
    well = next((item for item in WELLS if item["id"] == well_id), None)
    if not well:
        raise HTTPException(404, "Well not found")
    if series not in {"production", "temperature", "srp", "css", "alerts"}:
        raise HTTPException(404, "Series not found")
    if series == "production":
        items = [{"day": day, "oil_bopd": round(well["oil_bopd"] * (1 + 0.025 * ((day % 7) - 3))), "water_cut_pct": 28 + day % 6} for day in range(1, 31)]
    elif series == "temperature":
        items = [{"week": week, "temperature_c": round(well["temperature_c"] + max(0, 8 - week) * 1.6, 1)} for week in range(1, 19)]
    elif series == "srp":
        items = [{"spm": well["spm"], "stroke_in": well["stroke_in"], "vfd_hz": well["vfd_hz"], "rod_load_kn": 42.8 if well_id == "BGL-014" else 31.4, "pump_fillage_pct": 54 if well_id == "BGL-014" else 76}]
    elif series == "css":
        items = [{"cycle_no": 4, "steam_ton": well["steam_ton"], "injection_pressure_bar": 82, "injection_hours": 36, "soak_hours": 72, "sor": well["sor"]}]
    else:
        items = [alert for alert in ALERTS if alert["well"] == well_id]
    return {"mode": "DEMO DATA", "well_id": well_id, "series": series, "items": items}

@app.post("/api/ai/css-optimize")
def optimize_css(payload: CssRequest, principal: dict = Depends(require_roles("ADMIN", "OPERATIONS_MANAGER"))):
    return {"mode": "AI SIMULATION / DEMO MODEL", "predicted_temperature_c": round(payload.reservoir_temperature + 19.4, 1), "heating_duration_days": 34, "cooling_rate_c_day": 0.42, "expected_production_bopd": 83, "expected_sor": 3.7, "expected_recovery_pct": 12.8, "recommended_start_hours": 60, "recommended": {"steam_volume_ton": round(payload.steam_volume * .86), "soak_hours": 60, "injection_pressure_bar": round(payload.injection_pressure * .92)}, "predicted_impact": {"production_pct": 11.2, "sor_reduction_pct": 13.4, "energy_saving_pct": 8.1, "recovery_pct": 4.6}, "confidence": 0.72, "human_approval_required": True}

@app.post("/api/ai/srp-optimize")
def optimize_srp(payload: SrpRequest, principal: dict = Depends(current_principal)):
    return {"mode": "AI SIMULATION / DEMO MODEL", "recommended": {"stroke_in": round(payload.stroke_in * .93), "spm": round(payload.spm * .91, 1), "vfd_hz": round(payload.vfd_hz * .92)}, "expected_pump_efficiency_pct": min(90, payload.pump_fillage_pct + 14), "expected_production_bopd": round(payload.production_bopd * 1.08), "expected_energy_kwh_bbl": 37.6, "confidence": 0.69, "human_approval_required": True}

@app.post("/api/ai/failure-prediction")
def failure_prediction(principal: dict = Depends(current_principal)):
    return {"mode": "AI SIMULATION / DEMO MODEL", "items": [{"well": "BGL-014", "failure_type": "Rod failure", "risk_pct": 78, "window": "14-21 days", "factors": ["High rod load", "High viscosity", "Low pump fillage"], "inspection": "Inspect rod string; verify fluid level"}]}

@app.post("/api/ai/rod-floating")
def rod_floating(principal: dict = Depends(current_principal)):
    return {"mode": "AI SIMULATION / DEMO MODEL", "classification": "ROD FLOATING", "risk": "HIGH", "factors": ["Cyclic load variance", "Pump fillage below 60%"], "recommendation": "Consider reducing SPM and reviewing VFD; verify fluid level and pump card. Engineer approval required."}

@app.get("/api/ai/recommendations")
def recommendations(principal: dict = Depends(current_principal)):
    return {"mode": "AI SIMULATION / DEMO MODEL", "items": [{"id": "REC-014", "well": "BGL-014", "recommendation": "Reduce speed from 7.5 to 6.8 SPM and VFD from 48 to 44 Hz.", "reason": "Rising viscosity and declining pump fillage with elevated load variance.", "impact": "Illustrative +8% production, lower rod loading", "confidence": 0.72, "approval_required": True, "status": "PENDING"}]}

@app.get("/api/analytics/{metric}")
def analytics(metric: str, principal: dict = Depends(require_roles("ADMIN", "OPERATIONS_MANAGER"))):
    if metric not in {"production", "steam", "energy"}:
        raise HTTPException(404, "Metric not found")
    months = ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"]
    items = [{"month": month, "oil_bopd": 2040 - index * 17 + (index % 3) * 11, "steam_ton": 6900 + index * 70, "sor": round(4.2 - index * .035, 2), "energy_kwh_bbl": round(45 - index * .25, 1)} for index, month in enumerate(months)]
    if metric == "steam":
        items = [{"month": item["month"], "steam_ton": item["steam_ton"], "sor": item["sor"]} for item in items]
    elif metric == "energy":
        items = [{"month": item["month"], "energy_kwh_bbl": item["energy_kwh_bbl"], "oil_bopd": item["oil_bopd"]} for item in items]
    return {"mode": "DEMO DATA", "metric": metric, "items": items}
