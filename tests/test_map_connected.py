import os

from src.core.utils import load_map_from_file
from src.core.uav import UAV
from src.planner.cpp.continuous.planner import ContinuousCoveragePathPlannerFactory

_base_dir = os.path.dirname(__file__)
images_root = os.path.join(_base_dir, "..", "images_filled")
for img in os.listdir(images_root):
    try:
        test_map = load_map_from_file(os.path.join(images_root, img))
        planner = ContinuousCoveragePathPlannerFactory.get_planner(
            "Single",
            [UAV()],
            test_map,
            single_planner="STC"
        )
    except ValueError as err:
        print(f"Failed to load {img}: {err.args[0]}")
        continue
