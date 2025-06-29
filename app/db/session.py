import uuid

from sqlalchemy import create_engine, select, func, delete
from sqlalchemy.orm import sessionmaker

from app.db.models import Base, Experiment, Variant, Device, DeviceAssignment
from app.services.experiments import bulk_assign_devices
from app.settings import settings

engine = create_engine(settings.DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    Base.metadata.create_all(bind=engine)

    with Session() as session:
        # ICON test
        icon_exp = session.execute(
            select(Experiment).where(Experiment.key == "icon")
        ).scalar_one_or_none()
        if icon_exp is None:
            icon_exp = Experiment(key="icon", name="Button Color Test")
            session.add(icon_exp)
            session.flush()
            session.add_all(
                [
                    Variant(
                        experiment_id=icon_exp.id,
                        key="version-1-url",
                        payload="version-1-url",
                        weight=0.3333,
                    ),
                    Variant(
                        experiment_id=icon_exp.id,
                        key="version-2-url",
                        payload="version-2-url",
                        weight=0.3333,
                    ),
                    Variant(
                        experiment_id=icon_exp.id,
                        key="version-3-url",
                        payload="version-3-url",
                        weight=0.3334,
                    ),
                ]
            )

        # PRICE test
        price_exp = session.execute(
            select(Experiment).where(Experiment.key == "price")
        ).scalar_one_or_none()
        if price_exp is None:
            price_exp = Experiment(key="price", name="Purchase Price Test")
            session.add(price_exp)
            session.flush()
            session.add_all(
                [
                    Variant(
                        experiment_id=price_exp.id, key="10", payload="10", weight=0.75
                    ),
                    Variant(
                        experiment_id=price_exp.id, key="20", payload="20", weight=0.10
                    ),
                    Variant(
                        experiment_id=price_exp.id, key="50", payload="50", weight=0.05
                    ),
                    Variant(
                        experiment_id=price_exp.id, key="5", payload="5", weight=0.10
                    ),
                ]
            )

        session.flush()

        existing_count = session.execute(
            select(func.count()).select_from(Device)
        ).scalar_one()
        if existing_count < 600:
            to_create = 600 - existing_count
            devices = [Device(device_id=str(uuid.uuid4())) for _ in range(to_create)]
            session.add_all(devices)
            session.flush()

        experiments = session.execute(select(Experiment)).scalars().all()

        for exp in experiments:
            session.execute(
                delete(DeviceAssignment).where(DeviceAssignment.experiment_id == exp.id)
            )
            session.flush()

            variants = (
                session.execute(select(Variant).where(Variant.experiment_id == exp.id))
                .scalars()
                .all()
            )

            bulk_assign_devices(session, exp.id, list(variants))

        session.commit()
