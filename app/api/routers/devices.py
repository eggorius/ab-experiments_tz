from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.models import Device
from app.db.session import get_db
from app.schemas.experiment import ActiveExperimentOut
from app.services.experiments import get_active_experiments

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get(
    "/{device_id}/experiments",
    response_model=List[ActiveExperimentOut],
    response_model_exclude={"variant": {"weight"}},
)
def list_active_experiments(
    device_id: str,
    db: Session = Depends(get_db),
):
    """Return list of active experiments."""
    device = db.query(Device).filter_by(device_id=device_id).first()
    if not device:
        db.add(Device(device_id=device_id))
        db.commit()

    return get_active_experiments(db, device_id)
