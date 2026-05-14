import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

import database as db
from services.identity_service import require_user

router = APIRouter()


class HistorySummary(BaseModel):
    id: int
    action: str
    created_at: str
    summary: dict[str, Any]


class HistoryDetail(HistorySummary):
    input_data: dict[str, Any]
    output_data: Any


def _summarise(action: str, output_data) -> dict:
    if action == "match":
        results = output_data if isinstance(output_data, list) else []
        return {
            "total": len(results),
            "strong_match": sum(1 for r in results if r.get("fit") == "strong_match"),
            "possible": sum(1 for r in results if r.get("fit") == "possible"),
            "not_suitable": sum(1 for r in results if r.get("fit") == "not_suitable"),
        }
    if action == "plan":
        schemes = output_data.get("schemes", []) if isinstance(output_data, dict) else []
        shared = output_data.get("shared_requirements", []) if isinstance(output_data, dict) else []
        return {
            "scheme_count": len(schemes),
            "shared_requirements_count": len(shared),
            "scheme_ids": [s.get("scheme_id") for s in schemes],
        }
    return {}


@router.get("/history", response_model=list[HistorySummary])
async def get_history(user: dict = Depends(require_user)):
    rows = db.get_history(user["profile_id"])
    return [
        HistorySummary(
            id=row["id"],
            action=row["action"],
            created_at=row["created_at"],
            summary=_summarise(row["action"], json.loads(row["output_data"])),
        )
        for row in rows
    ]


@router.get("/history/{interaction_id}", response_model=HistoryDetail)
async def get_interaction(
    interaction_id: int,
    user: dict = Depends(require_user),
):
    row = db.get_interaction(user["profile_id"], interaction_id)
    if not row:
        raise HTTPException(status_code=404, detail="Interaction not found")

    output = json.loads(row["output_data"])
    return HistoryDetail(
        id=row["id"],
        action=row["action"],
        created_at=row["created_at"],
        summary=_summarise(row["action"], output),
        input_data=json.loads(row["input_data"]),
        output_data=output,
    )
