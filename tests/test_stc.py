import os

from src.core.cell import CellType
from src.planner.cpp.single.planner import SingleCPPPlannerFactory
from src.core.uav import UAV
from src.core.utils import load_map_from_text_file

test_map = load_map_from_text_file(os.path.join("resources", "stc_8x8_sparse_test.txt"))
uav = UAV(r=0, c=0)
for row in test_map.cells:
    for cell in row:
        if cell.cell_type == CellType.FREE:
            cell.assign = uav.name

stc = SingleCPPPlannerFactory.get_planner("STC", test_map, uav)
stc.plan()

print(uav.trajectory)
