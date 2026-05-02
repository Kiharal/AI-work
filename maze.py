import sys

class Node:
    def __init__(self, state, parent, action, cost, steps):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost
        self.steps = steps
    
    def __repr__(self):
        return f"{self.state}: {self.cost}"

class StackFrontier:
    def __init__(self):
        self.frontier = []

    def contains_state(self, state):
        return any([state == node.state for node in self.frontier])
    
    def add(self, node):
        self.frontier.append(node)
    
    def empty(self):
        return len(self.frontier) == 0
    
    def remove(self):
        node = self.frontier[-1]
        self.frontier.pop(-1)
        return node

class QueueFrontier(StackFrontier):
    def remove(self):
        node = self.frontier[0]
        self.frontier.pop(0)
        return node

class KnownFrontier(QueueFrontier):
    #Keep track of lowest heusristic cost value
    n = 0
    
    #Intelligent choice of node as per the cost of travel
    def remove(self):
        #Check if the frontier has more than 1 value
        if len(self.frontier) > 1:
            #Checks if the previous heuristic cost value(N-1) is less the current value
            if KnownFrontier.n != 0:
                if ((self.frontier[KnownFrontier.n-1].cost + self.frontier[KnownFrontier.n-1].steps) <=
                (self.frontier[KnownFrontier.n].cost + self.frontier[KnownFrontier.n].steps)):
                    KnownFrontier.n-=1

            #In the event the value ahead(N+1) has a lower heuristic cost    
            elif (self.frontier[KnownFrontier.n+1].cost + self.frontier[KnownFrontier.n+1].steps < 
                  self.frontier[KnownFrontier.n].cost + self.frontier[KnownFrontier.n].steps):
                KnownFrontier.n+=1
        
        node = self.frontier[KnownFrontier.n]
        self.frontier.pop(KnownFrontier.n)
        return node
    
    def __repr__(self):
        values = [x for x in self.frontier]
        return f"[{values}]"


class Maze:
    def __init__(self, filename):
        with open(filename) as f:
            contents = f.read()
        
        #validate maze goal and initial point
        if contents.count('A') != 1 and contents.count('B') != 1:
            raise Exception('The maze must have only one start and goal')
        maze = contents.splitlines()
        self.height = len(maze)
        self.width = max(len(rw) for rw in maze)

        #define walls
        self.walls = []
        for i, row in enumerate(maze):
            rows = []
            for j in (range(self.width)):
                try:
                    if maze[i][j] == 'A':
                        self.start = (i, j)
                        rows.append(False)
                    elif maze[i][j] == 'B':
                        self.goal = (i, j)
                        rows.append(False)
                    elif maze[i][j] == ' ':
                        rows.append(False)
                    else:
                        rows.append(True)
                except IndexError:
                    rows.append(True)
                
            self.walls.append(rows)
        

        self.solution = None # stores array of actions [0] and array of cells to move through(state) [1]
    
    def neighbours(self, state):
        row, col = state
        candidates = [
            ((row -1, col),"up"),
            ((row + 1, col), "down"),
            ((row, col - 1), "left"),
            ((row, col + 1), "right")
        ]

        result = []
        for (i, j), action in candidates:
            
            if 0<= i < self.height and 0 <= j < self.width and not self.walls[i][j]:
                result.append(((i, j), action))
        
        return result
    


    def print(self):
        solution = self.solution[1] if self.solution is not None else None

        #printing full maze
        print()
        for i, row in enumerate(self.walls):
            print()
            for j, col in enumerate(row):
                if col:
                    print("#",end="")
                elif (i, j) == self.start:
                    print("A", end="")
                elif (i, j) == self.goal:
                    print("B", end="")
                elif solution is not None and (i, j) in solution:
                    print("*", end="")
                else:
                    print(" ", end="")
        print()


    def solve(self):
        #define empty frontier
        self.frontier = KnownFrontier()
        #set empty explored set and no_ of explored sets

        self.num_explored = 0

        self.explored = set()
        #initialise the start state
        self.frontier.add(Node(state=self.start,
                                parent= None,
                                action=None,
                                cost=(
                                    abs(self.start[0] - self.goal[0]) + abs(self.start[1] - self.goal[1])
                                    ),
                                steps = 0
                                    ))
        print('Solving...')

        while True:

            if self.frontier.empty():
                raise Exception("No solution exists")

            #expand Node
            print(self.frontier)
            node = self.frontier.remove()
            self.num_explored +=1
            #analyze Node
            if node.state == self.goal:
                action = []
                cells = []
                while node.parent is not None:
                    action.append(node.action)
                    cells.append(node.state)
                    node = node.parent

                action.reverse()
                cells.reverse()
                self.solution = (action, cells)
                return
            else:
                #Expand Node
                self.explored.add(node.state)

                for (i, j), action in self.neighbours(node.state):
                    if (i, j) not in self.explored and not self.frontier.contains_state((i, j)):
                        new_node = Node(
                            state=(i, j),
                            parent=node,
                            action=action,
                            cost=(
                                abs(i - self.goal[0]) + abs(j - self.goal[1])
                                ),
                            steps=node.steps+1
                            )
                        self.frontier.add(new_node)
                        

    def output_image(self, filename, show_solution=True, show_explored=False):
        from PIL import Image, ImageDraw
        cell_size = 50
        cell_border = 2

        #Create blank canvas
        img = Image.new(
            "RGBA",
            (self.width * cell_size, self.height * cell_size),
            "black"
        )
        draw = ImageDraw.Draw(img)

        solution = self.solution[1] if self.solution is not None else None
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):

                #if wall
                if col:
                    fill = (40, 40, 40)
                
                #Start
                elif (i, j) == self.start:
                    fill = (255, 0, 0)
                
                #End/Goal
                elif (i, j) == self.goal:
                    fill = (0, 171, 28)
                
                #Solution
                elif solution is not None and  (i, j) in solution:
                    fill = (220, 235, 113)
                
                #Explored
                elif solution is not None and show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)
                
                #Empty cell
                else:
                    fill = (237, 240, 252)

                #Draw cell
                draw.rectangle(
                    ([(j * cell_size + cell_border, i * cell_size + cell_border),
                      ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)]),
                      fill=fill
                )

        img.save(filename)


if len(sys.argv) != 2:
    sys.exit("Usage: python maze.py maze.txt")

m = Maze(sys.argv[1])
print("Maze:")
m.print()
print("Solving...")
m.solve()
print("States Explored: ", m.num_explored)
print("Solution:")
m.print()
m.output_image("maze.png", show_explored=True)
