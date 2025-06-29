from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session

from app.schemas.statistics import ExperimentStat
from app.services.statistics import get_experiments_stats
from app.db.session import get_db

router = APIRouter(prefix="/stats", tags=["statistics"])


@router.get("/experiments", response_model=List[ExperimentStat])
def experiments_statistics(
    db: Session = Depends(get_db),
):
    return get_experiments_stats(db)
