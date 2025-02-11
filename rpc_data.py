# ----------------------------------------------------------------------------
# File: <rpc_data>.py
#
# Description:
# <Dataclasses for main gEMA functionality>.
#
# Contact:
# For inquiries, please contact Alex Manley (amanley97@ku.edu).
#
# License:
# This project is licensed under the MIT License. See the LICENSE file
# in the repository root for more information.
# ----------------------------------------------------------------------------

from dataclasses import (
    dataclass,
    field,
    asdict
)
from typing import Optional
from pathlib import Path

@dataclass
class GemaBoard:
    type: Optional[str] = None
    clk: Optional[float] = None


@dataclass
class GemaProcessor:
    isa: Optional[str] = None
    type: Optional[str] = None
    cpu: Optional[str] = None
    ncores: Optional[int] = None


@dataclass
class GemaMemory:
    type: Optional[str] = None
    size: Optional[int] = None


@dataclass
class GemaCache:
    type: Optional[str] = None
    l1d_size: Optional[int] = None
    l1i_size: Optional[int] = None
    l2_size: Optional[int] = None
    l1d_assoc: Optional[int] = None
    l1i_assoc: Optional[int] = None
    l2_assoc: Optional[int] = None


@dataclass
class GemaConfiguration:
    config_id: int
    resource: Optional[str] = None
    board: GemaBoard = field(default_factory=GemaBoard)
    processor: GemaProcessor = field(default_factory=GemaProcessor)
    memory: GemaMemory = field(default_factory=GemaMemory)
    cache: GemaCache = field(default_factory=GemaCache)


@dataclass
class GemaSimulation:
    sim_id: int
    config: GemaConfiguration
    generated_on: str
    path: Path
    pid: Optional[int] = None

    def to_dict(self):
        data = asdict(self)
        data["path"] = str(self.path)
        return data
