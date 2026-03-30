from typing import List, Tuple


BULLSEYE_SEGMENT_COUNT_ATTR = "_aha_bullseye_segment_count"
VALID_SEGMENT_COUNTS = (16, 17)


def validate_segment_count(segment_count: int) -> int:
    if segment_count not in VALID_SEGMENT_COUNTS:
        raise ValueError(f"values must contain 16 or 17 entries; got {segment_count}")
    return segment_count


def ring_bounds(segment_count: int) -> List[Tuple[int, int, float, float]]:
    validate_segment_count(segment_count)

    if segment_count == 17:
        rings = [(0, 6), (6, 12), (12, 16), (16, 17)]
    else:
        rings = [(0, 6), (6, 12), (12, 16)]

    edge_step = 1.0 / len(rings)
    ring_edges = [edge_step * idx for idx in range(len(rings) + 1)]

    bounds = []
    for ring_index, (start_idx, end_idx) in enumerate(rings):
        r0 = ring_edges[len(rings) - ring_index - 1]
        r1 = ring_edges[len(rings) - ring_index]
        bounds.append((start_idx, end_idx, r0, r1))
    return bounds


def infer_segment_count(ax) -> int:
    segment_count = getattr(ax, BULLSEYE_SEGMENT_COUNT_ATTR, None)
    if segment_count in VALID_SEGMENT_COUNTS:
        return int(segment_count)

    patch_count = len(getattr(ax, "patches", ()))
    if patch_count in VALID_SEGMENT_COUNTS:
        return patch_count

    raise ValueError(
        "could not determine bullseye layout from axes; use an axes returned by bullseye()"
    )
