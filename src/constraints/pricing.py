import json
from dataclasses import dataclass

from .timegrid import SLOTS_PER_DAY, validate_slot

PRICING_CONFIG = "config/pricing.json"


@dataclass(frozen=True)
class Tier:
    name: str
    start_hour: int
    end_hour: int
    price_per_kwh: float


@dataclass(frozen=True)
class PricingTiers:
    tiers: tuple

    @classmethod
    def from_config(cls, cfg):
        if not isinstance(cfg, dict) or "tiers" not in cfg:
            raise ValueError("pricing config must be a dict with a 'tiers' list")
        n = cfg.get("slots_per_day", SLOTS_PER_DAY)
        if n != SLOTS_PER_DAY:
            raise ValueError("slots_per_day %r != %d" % (n, SLOTS_PER_DAY))
        tiers = []
        for t in cfg["tiers"]:
            tier = Tier(
                name=_require_str(t, "name"),
                start_hour=_require_int(t, "start_hour"),
                end_hour=_require_int(t, "end_hour"),
                price_per_kwh=_require_price(t),
            )
            if not 0 <= tier.start_hour < tier.end_hour <= SLOTS_PER_DAY:
                raise ValueError("tier %r: need 0 <= start_hour < end_hour <= %d" % (tier.name, SLOTS_PER_DAY))
            tiers.append(tier)
        tiers.sort(key=lambda t: t.start_hour)
        cursor = 0
        for t in tiers:
            if t.start_hour != cursor:
                raise ValueError("tiers must tile 0..%d contiguously; gap/overlap at hour %d" % (SLOTS_PER_DAY, cursor))
            cursor = t.end_hour
        if cursor != SLOTS_PER_DAY:
            raise ValueError("tiers must cover 0..%d; coverage ends at %d" % (SLOTS_PER_DAY, cursor))
        return cls(tiers=tuple(tiers))

    @classmethod
    def load(cls, path=None):
        path = _pricing_path(path)
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_config(json.load(f))

    def price_at(self, slot):
        validate_slot(slot)
        for t in self.tiers:
            if t.start_hour <= slot < t.end_hour:
                return t.price_per_kwh
        raise ValueError("no tier covers slot %d" % slot)

    def price_vector(self):
        return [self.price_at(s) for s in range(SLOTS_PER_DAY)]

    def to_dict(self):
        return {
            "slots_per_day": SLOTS_PER_DAY,
            "tiers": [vars(t) for t in self.tiers],
        }


def load_pricing(path=None):
    return PricingTiers.load(path)


def _pricing_path(path):
    from pathlib import Path

    if path is not None:
        return Path(path)
    return Path(__file__).resolve().parents[2] / PRICING_CONFIG


def _require_str(d, key):
    v = d.get(key)
    if not isinstance(v, str) or not v.strip():
        raise ValueError("tier %r: %s must be a non-empty string" % (d, key))
    return v


def _require_int(d, key):
    v = d.get(key)
    if not isinstance(v, int) or isinstance(v, bool):
        raise ValueError("tier %r: %s must be an int" % (d, key))
    return v


def _require_price(d):
    v = d.get("price_per_kwh")
    if not isinstance(v, (int, float)) or isinstance(v, bool):
        raise ValueError("tier %r: price_per_kwh must be a number" % d)
    if v < 0:
        raise ValueError("tier %r: price_per_kwh must be non-negative" % d)
    return float(v)
