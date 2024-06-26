import os

from src.core.cell import CellType
from src.planner.cpp.single.planner import SingleCoveragePathPlannerFactory
from src.core.uav import UAV
from src.core.utils import load_map_from_text_file

_base_dir = os.path.dirname(__file__)
test_suite = [
    (os.path.join(_base_dir, "resources", "stc_dense.txt"), 40.0),
    (os.path.join(_base_dir, "resources", "stc_sparse.txt"), 52.0),
    (os.path.join(_base_dir, "resources", "stc_non_homogeneous.txt"), 41.66),
    (os.path.join(_base_dir, "resources", "stc_bipartite.txt"), 52.83),
    (os.path.join(_base_dir, "resources", "stc_narrow.txt"), 60.83),
]


def _assert_trajectory(_uav: UAV, length: float) -> None:
    assert _uav.trajectory is not None
    got = uav.trajectory_length
    diff = abs(got - length)
    try:
        assert diff < 1e-2
        print("OK")
    except AssertionError:
        print(f"FAILED: got {got}, want {length}")
        print([(cell.r, cell.c) for cell in _uav.trajectory])


for test_map_path, want_length in test_suite:
    test_map = load_map_from_text_file(test_map_path)
    uav = UAV(r=0, c=0)
    for row in range(test_map.height):
        for col in range(test_map.width):
            if test_map.get_cell(row, col).cell_type == CellType.FREE:
                test_map.assign(row, col, uav)

    stc = SingleCoveragePathPlannerFactory.get_planner("STC", test_map, uav)
    stc.plan()
    _assert_trajectory(uav, want_length)
