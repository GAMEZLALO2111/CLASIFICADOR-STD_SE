from sqlalchemy import Column, Integer, String, Float
from backend.app.database.db import Base

class Setup(Base):
    __tablename__ = "setups"

    id = Column(Integer, primary_key=True, index=True)

    part_full = Column(String, index=True)
    prefix = Column(String)
    number = Column(String)
    version = Column(String)
    nivel = Column(String)

    thickness = Column(Float)
    sheet_x = Column(Integer)
    sheet_y = Column(Integer)

    stations = Column(String)      # CSV “201,202,204”
    tool_numbers = Column(String)  # CSV “74500.2,10255”

    sym = Column(Integer)
    run_time_mins = Column(Float)
    uph = Column(Float)
