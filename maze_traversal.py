import numpy as np

up = 0
down = 1
left = 2
right = 3

class MazeTraverser():
    def __init__(self, maze, random_start=False):
        '''
        Maze Traversal class

        maze: maze to traverse

        random_start: whether to randomly pick the starting point inside the maze,
            or to start from the perimeter
        
        '''
        self.maze = maze

        # Find entrance, exit of maze
        start = np.array([0, np.argmin(maze[0, :])], dtype=int)
        end = np.array([maze.shape[0]-1, np.argmin(maze[-1, :])], dtype=int)

        # Randomly swap the start and end
        # So no "meta-knowledge" about the maze topology
        shuff = [start, end]
        np.random.shuffle(shuff)

        self.random_start = random_start

        if random_start:
            self.randomise_start()
            # Plug up either start or end
            # Set the other to be the actual exit
            self.maze[shuff[0][0], shuff[0][1]] = True
            self.exit = shuff[1]
        else:
            self.idx = shuff[0]
            self.exit = shuff[1]

    def randomise_start(self):
        '''
        Pick random starting point
        
        '''
        # Pick random coords inside the maze
        i = np.random.randint(1, self.maze.shape[0]-1)
        j = np.random.randint(1, self.maze.shape[0]-1)

        if self.maze[i, j]:
            # Coords map to a wall, try again
            self.randomise_start()
        else:
            self.idx = np.array([i, j], dtype=int)

    def _get_shifted_idxs(self):
        '''
        Get indexes of neighbour cells
        '''
        up_idx = self.idx + np.array([0, -1], dtype=int)
        down_idx = self.idx + np.array([0, 1], dtype=int)
        left_idx = self.idx + np.array([-1, 0], dtype=int)
        right_idx = self.idx + np.array([1, 0], dtype=int)

        return up_idx, down_idx, left_idx, right_idx

    def is_wall(self, idx):
        '''
        Check if idx is a wall
        '''
        N, M = self.maze.shape
        if idx[0] < 0:
            # Beyond entrance, return wall to make dead end
            return True
        elif idx[0] > N-1:
            # Beyond exit, return path
            return False
        else:
            return self.maze[idx[0], idx[1]]
    
    def get_surroundings(self):
        '''
        Get list of which neighbour tiles are walls

        get_surroundings()[left] gives whether left cell is a wall (True)
        
        '''
        # left, right, up, down idxs
        idxs = self._get_shifted_idxs()

        # Process each direction
        return [self.is_wall(idx) for idx in idxs]
    
    def process_response(self, response):
        '''
        Work out the move given response from the solver
        '''
        # left, right, up, down idxs
        idxs = self._get_shifted_idxs()

        if response >= 0 and response < 4 and np.issubdtype(type(response), np.integer):
            # Response was an int between 0 and 3, valid response
            self.idx = idxs[response]
            return ~self.maze[self.idx[0], self.idx[1]]
        else:
            # Invalid response, fail
            raise RuntimeError("Invalid Response")
        
    def solve_step(self, solver):
        '''
        Solve a single step of the traversal, using solver
        
        '''
        if self.maze[self.idx[0], self.idx[1]]:
            raise RuntimeError("Navigated to a wall")
        
        next_step = solver.advance(self.get_surroundings())
        return self.process_response(next_step)
        

    def solve_maze(self, solver, maxiter=1000):
        '''
        Attempt to use solver to solve maze in maxiter number of steps

        returns True is solving was successful, False if it failed
        
        '''
        for i in range(maxiter):
            if np.all(self.idx == self.exit):
                # Found exit
                return True
            
            self.solve_step(solver)

        # Maxiter reached without failure, but failed to solve maze
        return False
            
    def solve_with_plotting(self, solver, maxiter=10000, animate=True, frame_fname=None, anim_frametime=0.25):
        '''
        Perform the same solution steps, but also plot the current state at every iteration

        Extra args are:

        animate: Whether to use plt.pause to display a matplotlib plot in a new window
            which is repeatedly updated (similar to using plt.show())
        frame_fname: Root filename for saving individual frame plots
            frame_fname=None disables saving of plots to files
            plot fname for frame is frame_fname + str(i) + ".png"
        anim_frametime: Delay time fed to plt.pause(), which controls the time spent on each frame.
            Pass a lower value to speed up the animation.
        
        '''
        import matplotlib.pyplot as plt

        for i in range(maxiter):
            if np.all(self.idx == self.exit):
                # Found exit
                plt.show()
                return True
            
            self.solve_step(solver)

            plt.clf()
            plt.imshow(self.maze.T)
            plt.scatter(*self.idx, marker="x", color="r")

            if animate:
                plt.pause(anim_frametime)
            
            if frame_fname is not None:
                fname = frame_fname + str(i) + ".png"
                plt.savefig(fname)