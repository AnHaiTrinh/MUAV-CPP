import json

from src.core.cell import CellType
from src.core.map import Map
from src.core.uav import UAV


def parse_uavs_and_map(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        uav_and_map_info = json.load(f)
        uavs = []
        for uav_info in uav_and_map_info["uavs"]:
            r = int(uav_info["r"])
            c = int(uav_info["c"])
            uav = UAV(uav_info["name"], r, c)
            uav.color = tuple(i for i in uav_info["color"])
            uavs.append(uav)

        map_info = [[int(x) for x in y] for y in uav_and_map_info["map"]]
        my_map = Map.create_empty_map(len(map_info[0]), len(map_info))
        for r, row in enumerate(map_info):
            for c, val in enumerate(row):
                if val >= 0:
                    my_map.assign(r, c, uavs[int(val)])
                else:
                    my_map.get_cell(r, c).cell_type = CellType.OCCUPIED

        return uavs, my_map


def save_uavs_and_map_info(uavs, assigned, output_file):
    save_data = {
        "uavs": [],
    }

    for uav in uavs:
        save_data["uavs"].append({
            "name": uav.name,
            "r": uav.r,
            "c": uav.c,
            "color": list(uav.color),
        })

    save_data["map"] = [[int(x) for x in y] for y in assigned]
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(save_data, f)
