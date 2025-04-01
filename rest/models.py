from pydantic import BaseModel, Field
from typing import Dict, Annotated, Optional

class ConfigDLPRB(BaseModel):
    rb_l_crb: int = Field(default=20, ge=1, le=106, alias="pdsch_fixed_l_crb") 
    pdsch_fixed_rb_alloc: bool = Field(default=True, alias="pdsch_fixed_rb_alloc")
    rb_start: int | None = Field(default=0, ge=0, alias="pdsch_fixed_rb_start")


class ConfigULPRB(BaseModel):
    pusch_fixed_l_crb: int = Field(default=20, ge=1, le=106, alias="pusch_fixed_l_crb")
    pusch_fixed_rb_alloc: bool = Field(default=True, alias="pusch_fixed_rb_alloc")
    rb_start: int | None = Field(default=0, ge=0, alias="pusch_fixed_rb_start")


class ConfigGain(BaseModel):
    gain: int = Field(default=0, ge=-30)
    cell_id: int | None = Field(default=1, ge=1)


class ConfigNoise(BaseModel):
    noise_level: float = Field(default=-30.0, ge=-40.0, le=1.0)
    channel: int | None = Field(default=0, ge=0)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "noise_level": -30.0,
                    "channel": 0
                }
            ]
        }
    }


class ConfigTimer(BaseModel):
    timer: int = Field(default=0, ge=0, le=90000, alias="inactivity_timer")


class ConfigULMCS(BaseModel):
    pusch_mcs: int = Field(default=0, ge=0, le=28, alias="pusch_mcs")


class ConfigDLMCS(BaseModel):
    pdsch_mcs: int = Field(default=0, ge=0, le=28, alias="pdsch_mcs")


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


class Layers(BaseModel):
    level: str  = Field(default="debug")
    max_size: int = Field(default=1)
    payload: int = Field(default=False)


class ConfigPdschLog(BaseModel):
    layers: str | Dict[str, Layers] = Field(default="PHY")
    max: int = Field(default=100, ge=1, le=4096)
    min: int = Field(default=1, ge=1, le=4096)
    timeout: int | None = Field(default=None, ge=1, le=60)
    short: bool = Field(default=True)
    allow_empty: bool = Field(default=False)
    start_timestamp: Optional[float] = Field(default=None)
    end_timestamp: Optional[float] = Field(default=None)
    ue_id: int | None = Field(default=None)
    rnti: int | None = Field(default=None)
    discard_si: bool | None = Field(default=False)

    model_config = {
        "json_schema_extra":{
            "examples": [
                {
                    "layers":"PHY",
                    "max":10, 
                    "allow_empty":False, 
                    "timeout":1,
                    "short":True,
                    "discard_si":True
                }    
            ]
        }
    }


class ConfigCellAlloc(BaseModel):
    cells: Dict[int, ConfigDLPRB | ConfigULPRB] = Field(default_factory=dict, description="Dictionary where KEYS are cell IDs (as strings) and values are configurations")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "cells": {"1": {"pdsch_fixed_l_crb": 20, "pdsch_fixed_rb_alloc": True, "pdsch_fixed_rb_start": 0}}
                },
                {
                    "cells": {"1": {"pusch_fixed_l_crb": 20, "pusch_fixed_rb_alloc": True, "pusch_fixed_rb_start": 0}}
                }
            ]
        }
    }

examples_config_cell_alloc = {"DL": {
                    "summary": "DL PRB allocation",
                    "description": "Set the DL PRB allocation of the eNB",
                    "value": {
                        "cells": {"1": {"pdsch_fixed_l_crb": 20, "pdsch_fixed_rb_alloc": True, "pdsch_fixed_rb_start": 0}}
                    },
                },
                "UL": {
                    "description": "Set the UL PRB allocation of the eNB",
                    "summary": "UL PRB allocation",
                    "value": {
                        "cells": {"1": {"pusch_fixed_l_crb": 20, "pusch_fixed_rb_alloc": True, "pusch_fixed_rb_start": 0}}
                    },
                },
            }


class ConfigCellMCS(BaseModel):
    cells: Dict[int, ConfigULMCS | ConfigDLMCS] = Field(default_factory=dict, description="Dictionary where KEYS are cell IDs (as strings) and values are configurations")
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "cells": {"1": {"pusch_mcs": 28}}
                },
                {
                    "cells": {"1": {"pdsch_mcs": 28}}
                }
            ]
        }
    }

examples_config_cell_mcs = {
    "UL": {
        "summary": "UL MCS allocation",
        "description": "Set the UL MCS allocation of the eNB",
        "value": {
            "cells": {"1": {"pusch_mcs": 28}}
        },
    },
    "DL": {
        "description": "Set the DL MCS allocation of the eNB",
        "summary": "DL MCS allocation",
        "value": {
            "cells": {"1": {"pdsch_mcs": 28}}
        },
    },
}


class ConfigCellTimer(BaseModel):
    cells: Dict[int, ConfigTimer] = Field(default_factory=dict, description="Dictionary where KEYS are cell IDs (as strings) and values are configurations")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "cells": {"1": {"inactivity_timer": 2560}}
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


class ConfigCellDLMCS(BaseModel):
    cells: Dict[int, ConfigDLMCS] = Field(default_factory=dict, description="Dictionary where KEYS are cell IDs (as strings) and values are configurations")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "cells": {"1": {"pdsch_mcs": 28}}
                }
            ]
        }
    }


class UeStats(BaseModel):
    ue_id: int = Field(default=0, ge=0)
    stats: bool | None = Field(default=False)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "ue_id": 0,
                    "stats": False,
                }
            ]
        }
    }


# *********************************************** CORE MODELS ***********************************************
class UeCore(BaseModel):
    imsi: str | None = Field(default="001010123456789")
    nai: str | None = Field(default="001010123456789")
    imei: str | None = Field(default="8668870435174501")
    type: str | None = Field(default="both")
    radio_capabilities: bool | None = Field(default=False, alias="radio_capabilities")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "type":"both"
                }
            ]
        }
    }