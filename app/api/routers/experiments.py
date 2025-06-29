from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.schemas.experiment import ExperimentCreate, ExperimentOut, StatusUpdate
from app.services.experiments import create_experiment, set_experiment_status

router = APIRouter(prefix="/experiments", tags=["experiments"])


@router.post("/", response_model=ExperimentOut)
def add_experiment(
    payload: ExperimentCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return create_experiment(
        db, payload.key, payload.name, [v.model_dump() for v in payload.variants]
    )


@router.patch("/{exp_id}/status", response_model=ExperimentOut)
def close_experiment(
    exp_id: int,
    payload: StatusUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    exp = set_experiment_status(db, exp_id, payload.is_active)
    if not exp:
        raise HTTPException(404, "Experiment not found")
    return exp
