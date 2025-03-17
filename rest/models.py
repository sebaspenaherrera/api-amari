from pydantic import BaseModel, Field
from typing import Dict, Annotated

class ConfigPRB(BaseModel):
    rb_l_crb: int = Field(default=20, ge=1, le=106, alias="pdsch_fixed_l_crb") 
    pdsch_fixed_rb_alloc: bool = Field(default=True, alias="pdsch_fixed_rb_alloc")
    rb_start: int | None = Field(default=0, ge=0, alias="pdsch_fixed_rb_start")

class ConfigGain(BaseModel):
    gain: int = Field(default=0, ge=-30)
    cell_id: int | None = Field(default=1, ge=1)


class ConfigTimer(BaseModel):
    timer: int = Field(default=0, ge=0, alias="inactivity_timer")


class ConfigULMCS(BaseModel):
    pusch_mcs: int = Field(default=0, ge=0, le=28, alias="pusch_mcs")


class ConfigStats(BaseModel):
    samples: bool = Field(default=True, alias="samples")
    rf: bool | None = Field(default=True, alias="rf")
    initial_delay: float | None = Field(default=0.7, alias="Initial_delay")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "samples": True,
                    "rf": True,
                    "Initial_delay": 0.7
                }
            ]
        }
    }


#class ConfigCell(BaseModel):
 #   cells: Dict[] = Field(default_factory=dict, description="Dictionary where KEYS are cell IDs (as strings) and values are configurations")


class ConfigCellPRB(BaseModel):
    cells: Dict[int, ConfigPRB] = Field(default_factory=dict, description="Dictionary where KEYS are cell IDs (as strings) and values are configurations")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "cells": {"1": {"pdsch_fixed_l_crb": 20, "pdsch_fixed_rb_alloc": True, "pdsch_fixed_rb_start": 0}}
                }
            ]
        }
    }


class ConfigCellTimer(BaseModel):
    cells: Dict[int, ConfigTimer] = Field(default_factory=dict, description="Dictionary where KEYS are cell IDs (as strings) and values are configurations")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "cells": {"1": {"inactivity_timer": 60000}}
                }
            ]
        }
    }


class ConfigCellULMCS(BaseModel):
    cells: Dict[int, ConfigULMCS] = Field(default_factory=dict, description="Dictionary where KEYS are cell IDs (as strings) and values are configurations")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "cells": {"1": {"pusch_mcs": 28}}
                }
            ]
        }
    }