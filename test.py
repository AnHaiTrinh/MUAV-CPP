from src.core.cell import CellType
from src.core.uav import UAV
from src.core.utils import load_map_from_file
from src.planner.cpp.single.planner import SingleCoveragePathPlannerFactory

test_map = load_map_from_file("images_filled/Paris_1.png")
for r in range(30, 36):
    for c in range(100, 106):
        print(test_map.get_cell(r, c))

uav = UAV(r=0, c=0)
for row in range(test_map.height):
    for col in range(test_map.width):
        if test_map.get_cell(row, col).cell_type == CellType.FREE:
            test_map.assign(row, col, uav)

stc = SingleCoveragePathPlannerFactory.get_planner("STC", test_map, uav)
adj_list = stc._kruskal((uav.r, uav.c))
print(adj_list[(17, 51)])
