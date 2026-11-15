import json
from dataclasses import asdict, dataclass

from .timegrid import SLOTS_PER_DAY

APPLIANCES_FILE = "data/processed/appliances.json"


@dataclass(frozen=True)
class Appliance:
    name: str
    power_kw: float
    duration_slots: int
    interruptible: bool = False
    earliest_start: int = 0
    latest_end: int = SLOTS_PER_DAY
    min_run_slots: int | None = None

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("name must be a non-empty string")
        _require_number(self.power_kw, "power_kw")
        if self.power_kw <= 0:
            raise ValueError(
                f"{self.name}: power_kw must be positive, got {self.power_kw!r}"
            )
        _require_int(self.duration_slots, "duration_slots")
        if self.duration_slots <= 0:
            raise ValueError(
                f"{self.name}: duration_slots must be positive, got {self.duration_slots!r}"
            )
        _require_int(self.earliest_start, "earliest_start")
        _require_int(self.latest_end, "latest_end")
        if not 0 <= self.earliest_start < self.latest_end <= SLOTS_PER_DAY:
            raise ValueError(
                f"{self.name}: need 0 <= earliest_start < latest_end <= {SLOTS_PER_DAY}, got {self.earliest_start}..{self.latest_end}"
            )
        if self.duration_slots > self.latest_end - self.earliest_start:
            raise ValueError(
                f"{self.name}: window {self.earliest_start}..{self.latest_end} too short for duration_slots={self.duration_slots}"  # noqa: UP031
            )
        if not isinstance(self.interruptible, bool):
            raise ValueError(f"{self.name}: interruptible must be a bool")  # noqa: TRY004
        if self.min_run_slots is not None:
            if not self.interruptible:
                raise ValueError(
                    f"{self.name}: min_run_slots only applies to interruptible appliances"
                )
            _require_int(self.min_run_slots, "min_run_slots")
            if self.min_run_slots <= 0 or self.min_run_slots > self.duration_slots:
                raise ValueError(
                    f"{self.name}: min_run_slots must be in 1..duration_slots, got {self.min_run_slots!r}"
                )

    @classmethod
    def from_dict(cls, d):
        known = {
            "name",
            "power_kw",
            "duration_slots",
            "interruptible",
            "earliest_start",
            "latest_end",
            "min_run_slots",
        }
        missing = known - {"min_run_slots"} - set(d)
        if missing:
            raise ValueError(f"missing fields: {sorted(missing)}")
        return cls(
            name=d["name"],
            power_kw=d["power_kw"],
            duration_slots=d["duration_slots"],
            interruptible=d.get("interruptible", False),
            earliest_start=d.get("earliest_start", 0),
            latest_end=d.get("latest_end", SLOTS_PER_DAY),
            min_run_slots=d.get("min_run_slots"),
        )

    def to_dict(self):
        d = asdict(self)
        if d["min_run_slots"] is None:
            del d["min_run_slots"]
        return d


def load_appliances(path=None):
    path = _appliances_path(path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"{path} not found - generate it with: python -m src.data.collect"
        )
    if cfg.get("slots_per_day", SLOTS_PER_DAY) != SLOTS_PER_DAY:
        raise ValueError(f"appliances file slots_per_day != {SLOTS_PER_DAY}")
    return [Appliance.from_dict(d) for d in cfg["appliances"]]


def _appliances_path(path):
    from pathlib import Path

    if path is not None:
        return Path(path)
    return Path(__file__).resolve().parents[2] / APPLIANCES_FILE


def _require_number(v, field):
    if not isinstance(v, (int, float)) or isinstance(v, bool):
        raise ValueError(f"{field} must be a number, got {v!r}")  # noqa: TRY004


def _require_int(v, field):
    if not isinstance(v, int) or isinstance(v, bool):
        raise ValueError(f"{field} must be an int, got {v!r}")  # noqa: TRY004
