import numpy as np
distance = 0.0
trajectory = np.array([(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (6, 5), (5, 5), (4, 5), (3, 5), (2, 5), (1, 5), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (7, 7), (6, 7), (5, 7), (4, 7), (3, 7), (2, 7), (1, 7), (0, 7), (0, 6), (0, 5), (0, 4), (1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (6, 3), (5, 3), (4, 2), (3, 2), (2, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (6, 1), (5, 1), (4, 0), (3, 0), (2, 0), (1, 0)])
trajectory_length = len(trajectory)
for i in range(trajectory_length):
    distance += np.sqrt(np.sum(np.square(trajectory[i] - trajectory[(i + 1) % trajectory_length])))
print(distance)