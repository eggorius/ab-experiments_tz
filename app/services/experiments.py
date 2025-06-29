import math
import random

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Experiment, Variant, Device, DeviceAssignment
from app.schemas.experiment import ActiveExperimentOut, VariantOut


def create_experiment(
    db: Session, key: str, name: str, variants: list[dict]
) -> Experiment:
    """Creates a new experiment"""
    experiment = Experiment(key=key, name=name)
    db.add(experiment)
    db.flush()

    variants_ = [Variant(experiment_id=experiment.id, **v) for v in variants]
    db.add_all(variants_)
    db.flush()

    bulk_assign_devices(db, experiment.id, variants_)

    db.commit()
    db.refresh(experiment)
    return experiment


def bulk_assign_devices(
    db: Session, experiment_id: int, variants: list[Variant]
) -> None:
    """
    Bulk assign devices to an experiment with given variants
    Computes how many devices should receive each variant, then
    randomly shuffle devices and divide them accordingly
    """
    devices = list(db.execute(select(Device)).scalars().all())
    n = len(devices)

    part_sizes = [math.floor(n * v.weight) for v in variants]
    diff = n - sum(part_sizes)
    for i in range(diff):
        part_sizes[i] += 1

    random.shuffle(devices)

    assignments = []
    idx = 0
    for variant, part_size in zip(variants, part_sizes):
        chunk = devices[idx : idx + part_size]
        for device in chunk:
            assignments.append(
                DeviceAssignment(
                    device_id=device.device_id,
                    experiment_id=experiment_id,
                    variant_id=variant.id,
                )
            )
        idx += part_size

    db.bulk_save_objects(assignments)


def set_experiment_status(
    db: Session, experiment_id: int, is_active: bool
) -> Experiment:
    """Sets is_active column for experiment with experiment_id"""
    exp = db.query(Experiment).get(experiment_id)
    exp.is_active = is_active
    # TODO: Remove all DeviceAssignments?
    db.commit()
    return exp


def get_active_experiments(db: Session, device_id: str) -> list[ActiveExperimentOut]:
    """Gets active experiments for given device_id"""
    experiments = (
        db.query(
            Experiment.id.label("experiment_id"),
            Experiment.name.label("experiment_name"),
            Experiment.key.label("experiment_key"),
            Variant.id.label("variant_id"),
            Variant.key.label("variant_key"),
            Variant.payload.label("variant_payload"),
            Variant.weight.label("variant_weight"),
        )
        .select_from(Experiment)
        .join(DeviceAssignment, DeviceAssignment.experiment_id == Experiment.id)
        .join(Variant, Variant.id == DeviceAssignment.variant_id)
        .filter(
            DeviceAssignment.device_id == device_id,
            Experiment.is_active.is_(True),
        )
        .all()
    )

    return [
        ActiveExperimentOut(
            experiment_id=row.experiment_id,
            experiment_key=row.experiment_key,
            experiment_name=row.experiment_name,
            variant=VariantOut(
                id=row.variant_id,
                key=row.variant_key,
                payload=row.variant_payload,
                weight=row.variant_weight,
            ),
        )
        for row in experiments
    ]
