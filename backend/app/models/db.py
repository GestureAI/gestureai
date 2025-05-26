from __future__ import annotations

from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import String
from sqlalchemy import VARCHAR
from sqlalchemy import DateTime
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapped_column


Base = declarative_base()


class TelemetryDb(Base):
    __tablename__ = "telemetries"
    id = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    precision = mapped_column("precision", Float, nullable=False)
    letter = mapped_column("letter", VARCHAR(1), nullable=False)
    prediction_time = mapped_column("prediction_time", Integer, nullable=False)
    response_time = mapped_column("response_time", Integer, nullable=False)
    model_name = mapped_column("model_name", String, nullable=False)
    created_at = mapped_column(
        "created_at", DateTime(timezone=True), server_default=current_timestamp()
    )
