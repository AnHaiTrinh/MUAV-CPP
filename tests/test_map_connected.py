import os

import numpy as np

from src.core.utils import load_map_from_file
from src.core.uav import UAV
from src.core.cell import CellType
from src.planner.cpp.multi.planner import MultiCoveragePathPlannerFactory

# _base_dir = os.path.dirname(__file__)
# images_root = os.path.join(_base_dir, "..", "images_filled")
images_root = "images_filled"
for img in os.listdir(images_root):
    print(f"Testing {img}")
    try:
        uav = UAV(has_color=False)
        test_map = load_map_from_file(os.path.join(images_root, img))
        planner = MultiCoveragePathPlannerFactory.get_planner(
            "Single", [uav], test_map, single_planner="STC"
        )
        planner.plan()
        trajectory = uav.trajectory
        assert trajectory is not None, "Trajectory is not set"
        n = len(trajectory)
        trajectory_cells = set(cell.coordinate for cell in trajectory)
        assert all(
            free_cell.coordinate in trajectory_cells
            for free_cell in test_map.free_cells
        ), "Not complete coverage"

        for i in range(n):
            assert (
                test_map.get_cell(*trajectory[i].coordinate).cell_type == CellType.FREE
            ), f"Covers occupied cell: {trajectory[i]}"
            assert trajectory[i].distance(trajectory[(i + 1) % n]) <= np.sqrt(
                2
            ), f"Not adjacent cells: {trajectory}"
    except ValueError as err:
        print(f"Failed to run: {err.args[0]}")
        continue
    except AssertionError as exp:
        print(f"Invalid trajectory: {exp.args[0]}")
        continue
