from typing import List, Sequence, Tuple

def snap_to_grid(value: float, grid_size: float) -> float:
    if grid_size <= 0:
        return value
    return round(value / grid_size) * grid_size

def snap_vector(vector: Sequence[float], grid_size: float) -> List[float]:
    return [snap_to_grid(v, grid_size) for v in vector]

def clamp_value(value: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(value, max_val))

def calculate_bounds(pos: Sequence[float], size: Sequence[float]) -> Tuple[List[float], List[float]]:
    half_size = [s / 2 for s in size]
    min_bounds = [pos[i] - half_size[i] for i in range(len(pos))]
    max_bounds = [pos[i] + half_size[i] for i in range(len(pos))]
    return min_bounds, max_bounds

def is_point_in_bounds(point: Sequence[float], min_bounds: Sequence[float], max_bounds: Sequence[float]) -> bool:
    for i in range(len(point)):
        if point[i] < min_bounds[i] or point[i] > max_bounds[i]:
            return False
    return True