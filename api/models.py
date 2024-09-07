from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column


# Contains the models that will be used to represent the database
# Requires creation of an engine in api.py to run


class Base(DeclarativeBase):
    pass


class Entry(Base):
    __tablename__ = "entry"

    entry_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    test_id: Mapped[int] = mapped_column(ForeignKey("test.test_id"))
    
    time_start_of_stage: Mapped[int] = mapped_column(nullable=False)
    axial_strain: Mapped[float] = mapped_column(nullable=False)
    vol_strain: Mapped[float] = mapped_column(nullable=False)
    excess_pwp: Mapped[float] = mapped_column(nullable=False)
    p: Mapped[float] = mapped_column(nullable=False)
    deviator_stress: Mapped[float] = mapped_column(nullable=False)
    void_ratio: Mapped[float] = mapped_column(nullable=False)
    shear_induced_pwp: Mapped[float] = mapped_column(nullable=False)

    def __repr__(self) -> str:
        return (
            f"<Entry(entry_id={self.entry_id}, test_id={self.test_id}, "
            f"time_start_of_stage={self.time_start_of_stage}, "
            f"axial_strain={self.axial_strain}, vol_strain={self.vol_strain}, "
            f"excess_pwp={self.excess_pwp}, p={self.p}, "
            f"deviator_stress={self.deviator_stress}, void_ratio={self.void_ratio}, "
            f"shear_induced_pwp={self.shear_induced_pwp})>"
        )

class Test(Base):
    __tablename__ = "test"

    test_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    test_value_id: Mapped[int] = mapped_column(ForeignKey("test_values.test_value_id"))
    sample_value_id: Mapped[int] = mapped_column(ForeignKey("sample_values.sample_value_id"))

    consolidation: Mapped[int] = mapped_column(nullable=False)
    anisotropy: Mapped[float] = mapped_column(nullable=False)

    def __repr__(self) -> str:
        return (
            f"<Test(test_id={self.test_id}, test_value_id={self.test_value_id}, "
            f"sample_value_id={self.sample_value_id}, consolidation={self.consolidation}, "
            f"anisotropy={self.anisotropy})>"
        )

class SampleValues(Base):
    __tablename__ = "sample_values"

    sample_value_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    density_type: Mapped[str] = mapped_column(String(20), nullable=False)
    plasticity_type: Mapped[str] = mapped_column(String(20), nullable=False)
    psd_type: Mapped[str] = mapped_column(String(20), nullable=False)

    def __repr__(self) -> str:
        return (
            f"<SampleValues(sample_value_id={self.sample_value_id}, density_type={self.density_type}, "
            f"plasticity_type={self.plasticity_type}, psd_type={self.psd_type})>"
        )

class TestValues(Base):
    __tablename__ = "test_values"

    test_value_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    drainage_type: Mapped[str] = mapped_column(String(20), nullable=False)
    shearing_type: Mapped[str] = mapped_column(String(20), nullable=False)
    availability_type: Mapped[bool] = mapped_column(nullable=False)

    def __repr__(self) -> str:
        return (
            f"<TestValues(test_value_id={self.test_value_id}, drainage_type={self.drainage_type}, "
            f"shearing_type={self.shearing_type}, anisotropy_type={self.anisotropy_type}, "
            f"availability_type={self.availability_type})>"
        )
