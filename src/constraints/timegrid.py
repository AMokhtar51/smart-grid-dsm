SLOTS_PER_DAY = 24


def validate_slot(slot):
    if not isinstance(slot, int) or isinstance(slot, bool):
        raise TypeError(f"slot must be an int, got {slot!r}")
    if not 0 <= slot < SLOTS_PER_DAY:
        raise ValueError("slot %d out of range 0..%d" % (slot, SLOTS_PER_DAY - 1))  # noqa: UP031
    return slot
