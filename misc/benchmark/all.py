import argparse
import random

from misc.benchmark._utils import get_logger, movements, setup, time_func
from src.core.uav import uav_name_generator
from src.planner.cpp.continuous.planner import ContinuousCoveragePathPlanner
from src.planner.cpp.utils import get_assign_count, map_to_assignment_matrix

random.seed(42069)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", default="all.log", help="Output log file")
    parser.add_argument("-n", "--num-uavs", type=int, default=8, help="Number of UAVs")
    parser.add_argument(
        "-c", "--change", type=int, default=5, help="Number of UAV changes"
    )
    parser.add_argument("--planner", help="multi UAV planner")
    parser.add_argument("--handler", help="UAV change handler's name")

    args = parser.parse_args()
    logger = get_logger(args.output)
    test_cases = setup(args.num_uavs)
    moves = movements(args.change)
    planner, handler = args.planner, args.handler
    for map_name, _map, _uavs in test_cases:
        continuous_planner = ContinuousCoveragePathPlanner(
            _uavs, _map, multi_planner=planner, handler=handler
        )
        init_plan_time, success = time_func(continuous_planner.plan)
        assigned = map_to_assignment_matrix(_map, _uavs)
        assign_count = get_assign_count(assigned, len(_uavs))
        logger.info(
            "%s,%d,%s,%s,%s,%.4f,%s,%s",
            map_name,
            0,
            planner,
            handler,
            success,
            init_plan_time,
            "|".join([f"{uav.trajectory_length:.4f}" for uav in _uavs]),
            "|".join([str(count) for count in assign_count]),
        )

        for i, (movement, add_new) in enumerate(moves):
            for _ in range(movement):
                for uav in _uavs:
                    uav.move()
            if add_new:
                replan_time, success = time_func(
                    continuous_planner.handle_new_uav, uav_name_generator()
                )
            else:
                remove_uav = random.choice(_uavs)
                replan_time, success = time_func(
                    continuous_planner.handle_removed_uav, remove_uav.name
                )
            assigned = map_to_assignment_matrix(_map, _uavs)
            assign_count = get_assign_count(assigned, len(_uavs))
            logger.info(
                "%s,%d,%s,%s,%s,%.4f,%s,%s",
                map_name,
                i + 1,
                planner,
                handler,
                success,
                replan_time,
                "|".join([f"{uav.trajectory_length:.4f}" for uav in _uavs]),
                "|".join([str(count) for count in assign_count]),
            )
            if not success:
                break
