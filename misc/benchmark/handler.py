import argparse
import random

from misc.benchmark._utils import setup, get_logger, movements, time_func
from src.core.uav import uav_name_generator
from src.planner.cpp.continuous.planner import ContinuousCoveragePathPlanner
from src.planner.cpp.utils import map_to_assignment_matrix, get_assign_count

random.seed(42069)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--handlers",
        nargs="+",
        default=["W_Transfer", "Redistribute", "Propagation"],
        help="UAV change handler",
    )
    parser.add_argument("-o", "--output", default="handler.log", help="Output log file")
    parser.add_argument("-n", "--num-uavs", default=8, type=int, help="Number of UAVS")
    parser.add_argument("-c", "--change", default=5, type=int, help="Number of changes")
    args = parser.parse_args()
    logger = get_logger(args.output)
    test_cases = setup(args.num_uavs)
    moves = movements(args.change)
    for handler in args.handlers:
        for map_name, _map, _uavs in test_cases:
            continuous_planner = ContinuousCoveragePathPlanner(
                _uavs, _map, multi_planner="Transfer", handler=handler
            )
            continuous_planner.plan()

            for i, (movement, add_new) in enumerate(moves):
                for _ in range(movement):
                    for uav in _uavs:
                        uav.move()
                if add_new:
                    replan_time, success = time_func(
                        continuous_planner.handle_new_uav, uav_name_generator()
                    )
                else:
                    removed_uav = random.choice(_uavs)
                    replan_time, success = time_func(
                        continuous_planner.handle_removed_uav, removed_uav.name
                    )
                assigned = map_to_assignment_matrix(_map, _uavs)
                assign_count = get_assign_count(assigned, len(_uavs))
                logger.info(
                    "%s,%d,%s,%s,%.4f,%s,%s",
                    map_name,
                    i + 1,
                    handler,
                    success,
                    replan_time,
                    "|".join([f"{uav.trajectory_length:.4f}" for uav in _uavs]),
                    "|".join([str(count) for count in assign_count]),
                )
