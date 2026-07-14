
from pydantic import BaseModel, Field, ValidationError, model_validator
from strenum import StrEnum
from typing import Any


class Zones(StrEnum):
    NORMAL = 'normal'
    BLOCKED = 'blocked'
    RESTRICTED = 'restricted'
    PRIORITY = 'priority'


class MetadataHub(BaseModel):

    zone: Zones = Field(default="normal")
    color: str | None = Field(default=None)
    max_drones: int = Field(default=1)

    @model_validator(mode="before")
    @classmethod
    def parser(self, data: dict[str, str]) -> dict[str, Any]:
        try:
            sol: dict[str, Any] = {}

            zone: Zones = Zones.NORMAL
            match data["zone"].lower():
                case "normal":
                    zone = Zones.NORMAL
                case "blocked":
                    zone = Zones.BLOCKED
                case "restricted":
                    zone = Zones.RESTRICTED
                case "priority":
                    zone = Zones.PRIORITY
                case _:
                    raise ValidationError("Zone not valid")
            max_drones = data["max_drones"]
            sol.update({"max_drones": int(max_drones)})
            sol.update({"zone": zone})
            return sol
        except (ValueError, TypeError, OverflowError):
            raise ValidationError("Max drones invalid")


class Hub (BaseModel):

    name: str = Field(min_length=3)
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    metadata: MetadataHub | None

    @model_validator(mode="before")
    @classmethod
    def parser(self, data: dict[str, str]) -> dict[str, Any]:
        sol: dict[str, Any] = {}

        try:
            max_drones = data["max_drones"]
            sol.update({"max_drones": int(max_drones)})
            sol.update({"zone": zone})
        except (ValueError, TypeError, OverflowError):
            raise ValidationError("Max drones invalid")


class MetadataConnect(BaseModel):
    max_link_capacity: int = Field(ge=1, default=1)


class Connection(BaseModel):

    nameFirstHub: str = Field(min_length=3)
    nameSecondHub: str = Field(min_length=3)
    metadata: MetadataConnect

    @model_validator(mode="after")
    def validator()

