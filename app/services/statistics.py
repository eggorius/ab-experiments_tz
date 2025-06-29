from sqlalchemy import func, select, distinct
from sqlalchemy.orm import Session

from app.db.models import Experiment, DeviceAssignment


def get_experiments_stats(db: Session) -> list[dict]:
    variant_counts = db.execute(
        select(
            DeviceAssignment.experiment_id,
            DeviceAssignment.variant_id,
            func.count().label("variant_count"),
        ).group_by(
            DeviceAssignment.experiment_id,
            DeviceAssignment.variant_id,
        )
    ).all()

    total_counts = db.execute(
        select(
            DeviceAssignment.experiment_id,
            func.count(distinct(DeviceAssignment.device_id)).label("total_devices"),
        ).group_by(DeviceAssignment.experiment_id)
    ).all()

    var_map = {
        (row.experiment_id, row.variant_id): row.variant_count for row in variant_counts
    }
    tot_map = {row.experiment_id: row.total_devices for row in total_counts}

    stats = []
    for exp in db.execute(select(Experiment)).scalars().all():
        exp_stat = {
            "experiment_id": exp.id,
            "experiment_key": exp.key,
            "experiment_name": exp.name,
            "total_devices": tot_map.get(exp.id, 0),
            "variants": [],
        }
        for variant in exp.variants:
            variant_count = var_map.get((exp.id, variant.id), 0)
            percentage = (
                (variant_count / exp_stat["total_devices"] * 100)
                if exp_stat["total_devices"]
                else 0
            )
            exp_stat["variants"].append(
                {
                    "variant_id": variant.id,
                    "variant_key": variant.key,
                    "count": variant_count,
                    "percentage": round(percentage, 1),
                    "weight": variant.weight
                }
            )
        stats.append(exp_stat)

    return stats
