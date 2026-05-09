import sys

class Node:
    def __init__(self, state, parent, action, dirty: bool, cost=None, steps=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.dirty = dirty
        self.cost = cost
        self.steps = steps
    
    def __repr__(self):
        return f"{self.state}: {self.dirty}"

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

    
    def __repr__(self):
        values = [x for x in self.frontier]
        return f"[{values}]"
    

#Frontier for return
class IntelligentFrontier(StackFrontier):
    n = 0
    
    #Smart choice of node as per the cost of travel
    def remove(self):
        #Check if the frontier has more than 1 value
        if len(self.frontier) > 1:
            #Checks if the previous heuristic cost value(N-1) is less the current value
            if IntelligentFrontier.n != 0:
                if ((self.frontier[IntelligentFrontier.n-1].cost + self.frontier[IntelligentFrontier.n-1].steps) <=
                (self.frontier[IntelligentFrontier.n].cost + self.frontier[IntelligentFrontier.n].steps)):
                    IntelligentFrontier.n-=1

            #In the event the value ahead(N+1) has a lower heuristic cost    
            elif (self.frontier[IntelligentFrontier.n+1].cost + self.frontier[IntelligentFrontier.n+1].steps < 
                  self.frontier[IntelligentFrontier.n].cost + self.frontier[IntelligentFrontier.n].steps):
                IntelligentFrontier.n+=1
        
        node = self.frontier[IntelligentFrontier.n]
        self.frontier.pop(IntelligentFrontier.n)
        return node


class Environment:
    def __init__(self, filename):
        with open(filename) as f:
            contents = f.read()
        
        #Initial state(A) is the charging or parking spot for the agent
        #B is the dirt in the environment
        if contents.count('A') != 1 and contents.count('B') == 0:
            raise Exception('The environment must have only one start and be dirty')
        environment = contents.splitlines()
        self.height = len(environment)
        self.width = max(len(rw) for rw in environment)

        #define walls
        self.perimeter = []
        self.dirt = []
        self.area = []
        for i, row in enumerate(environment):
            rows = []
            dirt = []
            for j in (range(self.width)):
                try:
                    if environment[i][j] == 'A':
                        self.start = (i, j)
                        rows.append(False)
                        dirt.append(False)
                    elif environment[i][j] == 'B':
                        self.area.append((i, j))
                        rows.append(False)
                        dirt.append(True)
                    elif environment[i][j] == ' ':
                        rows.append(False)
                        dirt.append(False)
                    else:
                        rows.append(True)
                        dirt.append(False)
                except IndexError:
                    rows.append(True)
                    dirt.append(False)
                
            self.perimeter.append(rows)
            self.dirt.append(dirt)
        

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
            
            if 0<= i < self.height and 0 <= j < self.width and not self.perimeter[i][j]:
                result.append(((i, j), action))
        
        return result
    


    def print(self):
        solution = self.solution[1] if self.solution is not None else None

        #printing full environment
        print()
        for i, row in enumerate(self.perimeter):
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


    #Fuction to return to home base/start
    def go_home(self, current):
        self.frontier = IntelligentFrontier()
        #set empty explored set and no_ of explored sets

        self.num_explored = 0

        self.explored = set()
        #initialise the start state
        self.frontier.add(Node(state=current,
                                parent= None,
                                action=None,
                                dirty=False,
                                cost=(
                                    abs(current[0] - self.start[0]) + abs(current[1] - self.start[1])
                                    ),
                                steps = 0
                                    ))

        while True:

            if self.frontier.empty():
                raise Exception("No solution exists")

            #expand Node
            print(self.frontier)
            node = self.frontier.remove()
            self.num_explored +=1
            #analyze Node
            if node.state == self.start:
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
                                abs(i - self.start[0]) + abs(j - self.start[1])
                                ),
                            steps=node.steps+1
                            )
                        self.frontier.add(new_node)

    def solve(self):
        #define empty frontier
        self.frontier = StackFrontier()
        #set empty explored set and no_ of explored sets

        self.num_explored = 0

        self.explored = set()
        #initialise the start state
        self.frontier.add(Node(state=self.start,
                                parent= None,
                                action=None,
                                dirt = False
                                    ))

        while True:

            #Check if the area is dirty
            dirt = None if len(self.area) == 0 else self.area

            if self.frontier.empty():
                raise Exception("No solution exists")

            #expand Node
            node = self.frontier.remove()
            self.num_explored +=1
            self.output_image()

            #Clean node
            if node.dirty:
                self.area.remove(node.state)

            #analyze if area is still dirty
            if dirt is None:
                print("The area is clean!")
                self.go_home(node.state)
                return
            else:
                #Expand Node
                self.explored.add(node.state)

                for (i, j), action in self.neighbours(node.state):
                    if (i, j) not in self.explored and not self.frontier.contains_state((i, j)) and (i, j) not in self.area:
                        new_node = Node(
                            state=(i, j),
                            parent=node,
                            action=action,
                            dirt=False
                            )
                    if (i, j) not in self.explored and not self.frontier.contains_state((i, j)) and (i, j) in self.area:
                        new_node = Node(
                            state=(i, j),
                            parent=node,
                            action=action,
                            dirt=True
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
        for i, row in enumerate(self.perimeter):
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
    sys.exit("Usage: python environment.py environment.txt")

###run vacuum