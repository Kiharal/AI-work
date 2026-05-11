import sys
import time

class Node:
    def __init__(self, state, parent, action, dirty: bool, cost=None, steps=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.dirty = dirty
        self.cost = cost
        self.steps = steps
    
    def __repr__(self):
        return f"{self.state}: {self.action}"
    
    def clean(self):
        self.dirty = True
    
    def __eq__(self, other):
        return self.state == other.state

class StackFrontier:
    def __init__(self):
        self.frontier = []

    def contains_state(self, state):
        return any([state == node.state for node in self.frontier])
    
    def add(self, node):
        self.frontier.append(node)
    
    def addleft(self, node):
        self.frontier.insert(0,node)


    def empty(self):
        return len(self.frontier) == 0
    
    def remove(self):
        node = self.frontier[-1]
        self.frontier.pop(-1)
        return node

    def refresh(self):
        self.frontier.clear()
    
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
        self.walls = []
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
                
            self.walls.append(rows)
            self.dirt.append(dirt)
        

        self.cleaned = None #stores all passed values
    
    def horizontal_action(self, state):
        row, col = state
        candidates = [
            ((row, col - 1), "left"),
            ((row, col + 1), "right")
        ]

        result = []
        for (i, j), action in candidates:
            
            if 0<= i < self.height and 0 <= j < self.width and not self.walls[i][j]:
                result.append(((i, j), action))
        
        return result
    
    def vertical_action(self, state):
        row, col = state
        candidates = [
            ((row -1, col),"up"),
            ((row + 1, col), "down"),
        ]

        result = []
        for (i, j), action in candidates:
            
            if 0<= i < self.height and 0 <= j < self.width and not self.walls[i][j]:
                result.append(((i, j), action))
        
        return result if len(result) != 0 else None
    
    def action(self, state):
        row, col = state
        candidates = [
            ((row, col - 1), "left"),
            ((row -1, col),"up"),
            ((row, col + 1), "right"),
            ((row + 1, col), "down"),
        ]

        result = []
        for (i, j), action in candidates:
            
            if 0<= i < self.height and 0 <= j < self.width and not self.walls[i][j]:
                result.append(((i, j), action))
        
        return result


    def print(self):
        cleaned = self.cleaned if self.cleaned is not None else None

        #printing full environment
        print()
        for i, row in enumerate(self.walls):
            print()
            for j, col in enumerate(row):
                if col:
                    print("#",end="")
                elif (i, j) == self.start:
                    print("A", end="")
                elif (i, j) in self.area:
                    print("B", end="")
                elif cleaned is not None and (i, j) in cleaned:
                    print("*", end="")
                else:
                    print(" ", end="")
        print()


    #Fuction to return to home base/start
    def go_home(self, current):
        self.frontier = IntelligentFrontier()
        #set empty explored set and no_ of explored sets

        self.num_explored = 0

        self.cleaned = set()
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
                raise Exception("No cleaned exists")

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
                self.cleaned = (action, cells)
                return
            else:
                #Expand Node
                self.cleaned.add(node.state)

                for (i, j), action in self.action(node.state):
                    if (i, j) not in self.cleaned and not self.frontier.contains_state((i, j)):
                        new_node = Node(
                            state=(i, j),
                            parent=node,
                            action=action,
                            dirty=False,
                            cost=(
                                abs(i - self.start[0]) + abs(j - self.start[1])
                                ),
                            steps=node.steps+1
                            )
                        self.frontier.add(new_node)

    def solve(self):
        #has no frontier since it can't jump from place to place. Instead it'll look at horizontal_action alone
        
        self.cleaned = set()
        self.frontier = StackFrontier()
        node = Node(
            state=self.start,
            parent=None,
            action=None,
            dirty=False,
        )
        self.frontier.add(node)
        
            
        round = 0
        while True:
            #Check if there are any valid steps to make or return home (but for now)
            if self.frontier.empty():
                print("the house is clean!")
                return

            #Check if house/environment is clean
            if len(self.area) == 0:
                print("the house is clean!")
                return
            
            #Remove a node from the frontier
            node = self.frontier.remove()
            self.frontier.refresh()



            #Clean surface
            if node.dirty:
                self.area.remove(node.state)

            self.cleaned.add(node.state)
            
            #Determine if vacuum hits a wall
            i, j = node.state
            if(self.walls[i][j+1] or self.walls[i][j-1]) and node.action is not None:
                #Should move up or down
                print("wall!")
            print(f"Cleaned: {self.cleaned}")
            print(node.state)
            for state, action in self.horizontal_action(node.state):
                if ((state not in self.cleaned and not self.frontier.contains_state(state) and state not in self.area)):
                    new_node = Node(
                        state=state,
                        parent=node,
                        action=action,
                        dirty=False,
                        steps=1,
                    )
                elif ((state not in self.cleaned and not self.frontier.contains_state(state) and state in self.area)):
                    new_node = Node(
                        state=state,
                        parent=node,
                        action=action,
                        dirty=True,
                        steps=1
                    )
                self.frontier.add(new_node)
                print(self.frontier)
            if len(self.frontier.frontier) >1 and self.frontier.frontier[0] == self.frontier.frontier[1]:
                self.frontier.refresh()
                print("They are the same")


            if len(self.frontier.frontier) <= 1 and round != 0:
                for state, action in self.vertical_action(node.state):
                    if ((state not in self.cleaned and not self.frontier.contains_state(state) and state not in self.area)):
                        new_node = Node(
                            state=state,
                            parent=node,
                            action=action,
                            dirty=False,
                            steps=1,
                        )
                    elif ((state not in self.cleaned and not self.frontier.contains_state(state) and state in self.area)):
                        new_node = Node(
                            state=state,
                            parent=node,
                            action=action,
                            dirty=True,
                            steps=1
                        )
                    self.frontier.add(new_node)
                    round = 0
            round +=1
            self.output_image("cleaned.png")


                        

    def output_image(self, filename, show_cleaned=True):
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

        cleaned = self.cleaned if self.cleaned is not None else None
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):

                #if wall
                if col:
                    fill = (40, 40, 40)
                
                #Start
                elif (i, j) == self.start:
                    fill = (255, 0, 0)
                
                #End/Goal
                elif (i, j) in self.area:
                    fill = (220, 235, 113)
                
                #cleaned
                elif cleaned is not None and (i, j) in self.cleaned:
                    fill = (6, 109, 250)
                
                #Empty cell
                else:
                    fill = (237, 240, 252)

                #Draw cell
                draw.rectangle(
                    ([(j * cell_size + cell_border, i * cell_size + cell_border),
                      ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)]),
                      fill=fill
                )

        time.sleep(0.5)
        img.save(filename)


if len(sys.argv) != 2:
    sys.exit("Usage: python vacuum.py environment.txt")

###run vacuum
house = Environment("environment.txt")
house.print()
print("Its cleaning time!")
house.solve()
house.print()
house.output_image("cleaned.png")