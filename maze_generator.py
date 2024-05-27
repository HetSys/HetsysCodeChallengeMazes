import numpy as np
import matplotlib.pyplot as plt

def gen_valid_neighs(idx, maze, dims):
    '''
    Get bits of the maze neighbouring idx that are inbounds walls

    idx: Index of the center
    maze: array storing the full maze
    dims max value for a valid index in each dim
    '''
    neighs = [
        (idx[0] - 1, idx[1]),
        (idx[0] + 1, idx[1]),
        (idx[0], idx[1] - 1),
        (idx[0], idx[1] + 1)
    ]

    inbounds_neighs = [neigh for neigh in neighs if 
                    neigh[0] >= 0 and neigh[0] < dims[0] and # 1st idx in bounds
                    neigh[1] >= 0 and neigh[1] < dims[1]] # 2nd idx in bounds
    
    valid_neighs = [neigh for neigh in inbounds_neighs if 
                    maze[neigh[0], neigh[1]]] # Neigh is a wall

    np.random.shuffle(valid_neighs)
    return valid_neighs, len(inbounds_neighs)


def gen_maze_mst(N, M, maxiter=1000):
    '''
    Generate a random "Minimum Spanning Tree" type maze (i.e. one which corresponds to a graph which is a minimum spanning tree)

    N, M: Dimensions of the maze
    maxiter: Max number of steps to generate the maze. Will warn if reached
    
    '''
    maze = np.ones((N, M), dtype=bool)

    start_idx_i = np.random.randint(1, N-2)
    start_idx_j = np.random.randint(1, M-2)
    start_idx = (start_idx_i, start_idx_j)

    maze[start_idx[0], start_idx[1]] = False
    neigh_list = []

    neigh_list.extend(gen_valid_neighs(start_idx, maze, [N, M])[0])

    for i in range(maxiter):
        if len(neigh_list) < 1:
            break

        #Shuffle neigh list
        np.random.shuffle(neigh_list)

        candidate = neigh_list.pop()

        if not maze[candidate]:
            # Skip wall if it's already been made into a cell
            continue
        
        # Get all neighs that are still walls
        valid_neighs, num_poss = gen_valid_neighs(candidate, maze, [N, M])

        if len(valid_neighs) == 3:
            # 3 neighs needed to allow current cell to be part of maze, not wall
            maze[candidate[0], candidate[1]] = False
            neigh_list.extend(valid_neighs)
    
    if len(neigh_list):
        print("Warning: max iterations reached, maze not finished")

    top_mask = ~maze[1, :]

    top_idx = np.random.choice(np.arange(M), size=1, p=top_mask / np.sum(top_mask))

    maze[0, top_idx] = False


    bottom_mask = ~maze[-2, :]

    bottom_idx = np.random.choice(np.arange(M), size=1, p=bottom_mask / np.sum(bottom_mask))

    maze[-1, bottom_idx] = False
    
    return maze

def count_squares(idx, maze):
    '''
    Count number of squares that would be formed if maze[idx] was made a cell
    Used to avoid blobs of maze, as we want longer loops separated by walls,
    rather than lots of small cycles
    '''

    square_transforms = [
        [[-1, -1], [0, -1], [0, 0], [-1, 0]],
        [[0, -1], [1, -1], [1, 0], [0, 0]],
        [[0, 0], [1, 0], [1, 1], [0, 1]],
        [[-1, 0], [0, 0], [0, 1], [-1, 1]]
    ]

    square_idxs = [
        np.array([(idx[0] + tr[0], idx[1] + tr[1]) for tr in square]) for square in square_transforms
    ]

    square_counts = 0
    for square in square_idxs:
        s = np.sum(maze[square[:, 0], square[:, 1]].astype(int))
        if s < 2: # Adding maze[idx] would create a square
            square_counts += 1
    return square_counts

def add_paths(maze, p=0.5):
    '''
    Add extra paths (thus making loops) to an existing maze
    
    p controls the probability of an extra path being added
    '''

    # Index transforms to get neighbour cells
    neigh_transforms = [
        [-1, 0], [1, 0], [0, -1], [0, 1]
    ]

    # Try to find spaces in the inner part of the maze (i.e. not the border)
    # Where we could randomly decide to add extra maze to create loops
    for i in range(1, maze.shape[0]-2):
        for j in range(1,  maze.shape[1]-2):
            if not maze[i, j]:
                # Skip bits that aren't walls       
                continue
            
            if np.all([maze[i + tr[0], j+tr[1]] for tr in neigh_transforms]):
                # Skip walls that have walls on adjacent cells
                # (to avoid creating inaccessible parts of the maze)
                continue

            if count_squares((i, j), maze) == 0 and np.random.rand() < p:
                # Need to not create squares
                # Add loop with probability p
                maze[i, j] = False
    return maze

def generate_maze(N, M, p=0.0, maxiter=10**9):
    '''
    Generate a maze with dimensions (N, M). The maze has a solid border, aside from a top entrance and a bottom exit.

    N, M: Dimensions of the maze

    p: Probability used to determine creation of loops in the maze (higher p has more loops, and is more difficult)
        p=0.0 produces a Minimum Spanning Tree, p>1.0 creates maximum amount of loops
    
    maxiter: Maximum loop iterations for initial MST maze algorithm. Will warn if maxiter reached before maze is fully created
            (see gen_maze_mst())

    returns a bool np.array of shape (N, M) defining the maze
    '''

    maze = gen_maze_mst(N, M, maxiter)

    if p > 0.0:
        maze = add_paths(maze, p)

    return maze