import pygame, random
import numpy as np
import time

col_new_fish = (0, 128, 255)
col_young_fish = (15,82,186)
col_breeding_fish = (220,35,157)

col_piranha = (255,0,0)
col_pir_old = (160, 160, 160)
col_pir_full_stomach = (0 ,0  ,0)

col_new_bear = (150,75,0) #dark brown
col_young_bear = (165,113,78) #
col_breeding_bear = (150,75,0) # dark brown


col_empty = (213, 196, 161)
col_grid = (30, 30, 60)

FRAMES_PER_SECOND = 90
SPEED = 15

ID = 0  # to identify each animal uniquely (for checking correctness)
def new_ID():
    global ID
    currentID = ID
    ID += 1
    return currentID

def new_fish():
    ID_fish = new_ID()
    fish = {'type': 'fish', 'id':ID_fish, 'col':col_new_fish, 'age': 0}
    return fish

# Bear initial definition
bear_breed_age = 8      # 8
bear_starvation = 0
def new_bear():
    ID_bear = new_ID()
    bear = {'type': 'bear', 'id':ID_bear, 'age': 0, 'col':col_new_bear, 'hunger': bear_starvation}
    return bear

limit_pir = 50
days_wo_eating = 500

# Piranha def
def new_piranha():
    ID_piranha = new_ID()
    piranha = {'type': 'piranha', 'id':ID_piranha, 'col':col_piranha, 'age': 0, 'stomach': 0, 'day' : 0 }
    return piranha

def empty():
    return {'type': 'empty'}

def init(dimx, dimy, fish, bear, piranha):
    """Creates a starting grid, of dimension dimx * dimy and inserts {fish} new fishes and {bear} new bears and Piranhas.
       The rest of the cells in the grid are filled with empty dictionaries. """
    # create a list with fish fishes, bear bears and the rest (dimx*dimy-fish-bear) are empty  and shuffle them
    content_list = []
    for i in range(fish):
        content_list.append(new_fish())
    for i in range(bear):
        content_list.append(new_bear())
    for i in range(piranha):
        content_list.append(new_piranha())
    for i in range((dimx * dimy - fish - bear - piranha)):
        content_list.append(empty())
    random.shuffle(content_list)
    # typecast the into a numpy array and reshape the 1 dimensional array to dimx * dimy
    cells_array = np.array(content_list)
    cells = np.reshape(cells_array, (dimy, dimx)) # the shape information is given in an  odd order
    return cells

# cur: the current array of cells,  r and c the row and column position which we are finding neighbours for.
def get_neighbors(cur, r, c):
    """Computes a list with the neighbouring cell positions of (r,c) in the grid {cur}"""
    r_min, c_min = 0 , 0
    r_max, c_max = cur.shape
    r_max, c_max = r_max -1 , c_max-1 # it's off by one
    # r-1,c-1 | r-1,c  | r-1,c+1
    # --------|--------|---------
    # r  ,c-1 | r  ,c  | r  ,c+1
    # --------|--------|---------
    # r+1,c-1 | r+1,c  | r+1,c+1
    neighbours = []
    # r-1:
    if r-1 >= r_min :
        if c-1 >= c_min: neighbours.append((r-1,c-1))
        neighbours.append((r-1,c))  # c is inside cur
        if c+1 <= c_max: neighbours.append((r - 1, c+1))
    # r:
    if c-1 >= c_min: neighbours.append((r,c-1))
    # skip center (r,c) since we are listing its neighbour positions
    if c + 1 <= c_max: neighbours.append((r,c+1))
    # r+1:
    if r + 1 <= r_max:
        if c - 1 >= c_min: neighbours.append((r+1,c-1))
        neighbours.append((r+1, c))  # c is inside cur
        if c + 1 <= c_max: neighbours.append((r+1,c+1))
    return neighbours

def neighbour_fish_empty_bear(cur,neighbours):
    """ Given a current grid and a set of neighbouring positions, it divides the neighbours into three lists of positions: """
    """ fish-neighbours, empty-neighbours cells and the rest"""
    # divide the neighbours into fish, empty cells and the rest
    fish_neighbours =[]
    empty_neighbours =[]
    bear_neighbours=[]
    piranha_neighbours=[]
    for neighbour in neighbours:
        if cur[neighbour]['type'] == "fish":
            fish_neighbours.append(neighbour)
        elif cur[neighbour]['type'] == "bear":
            bear_neighbours.append(neighbour)
        elif cur[neighbour]['type'] == "piranha":
            piranha_neighbours.append(neighbour)
        else:
            empty_neighbours.append(neighbour)

    return fish_neighbours, empty_neighbours, bear_neighbours, piranha_neighbours

def fish_rules(cur,r,c,neighbour_fish, neighbour_empty):
    """ Given the current grid {cur}, a position (r,c) which contains a fish, and a list of grid-positions for the
        fish-neighbours  and a list of grid-positions of empty neighbour cells. Update the grid according to the fish-rules"""

    # implement the fish rules
    cur[r, c]['age'] = cur[r, c]['age'] + 1  # update age

    # it breeds if it's been alive for 12 states
    if cur[r, c]['age'] >= 12:
        cur[r, c]['col'] = col_breeding_fish
        if neighbour_empty != []:  # check if the list is not empty
            new_location = random.choice(neighbour_empty)  # pick a random empty cell from the list
            cur[new_location] = new_fish()
            cur[new_location]['col'] = col_new_fish
            neighbour_fish.append(new_location)
            neighbour_empty.remove(new_location)
    else:
        cur[r, c]['col'] = col_young_fish

    # dies if overcrowded
    if len(neighbour_fish) >= 2:
        cur[r, c] = empty()  # fish dies

    # if it does not die, moves
    if neighbour_empty != []:  # check if the list is not empty
        new_location = random.choice(neighbour_empty)  # pick a random empty cell from the list
        cur[new_location] = cur[r, c]
        cur[r, c] = empty()

    return cur

def bear_rules(cur, r, c, neighbour_fish, neighbour_empty):
    """ Given the current grid {cur}, a position (r,c) which contains a bear, and a list of grid-positions for the
    fish-neighbours  and a list of grid-positions of empty neighbour cells. Update the grid according to the fish-rules"""

    # implement the bear rules
    cur[r, c]['age'] = cur[r, c]['age'] + 1
    cur[r, c]['hunger'] = cur[r, c]['hunger'] + 1

    # bear dies of starvation
    if cur[r, c]['hunger'] >= 10:
        print(f"bear starved until death in pos {r, c} ")
        cur[r, c] = empty()

    # bear breeds if not dead
    elif cur[r, c]['age'] >= 8 >= cur[r, c]['hunger'] and neighbour_empty != []:  # check if the list is not empty
        cur[r, c]['col'] = col_breeding_bear
        new_location = random.choice(neighbour_empty)  # pick a random empty cell from the list
        cur[new_location] = new_bear()
        cur[new_location]['col'] = col_new_bear
        cur[r, c]['col'] = col_young_bear

    # finds a fish and eats it
    elif neighbour_fish:   # check if the list is not empty
            fish_food = random.choice(neighbour_fish)  # pick a random empty cell from the list and store in fish_food
            neighbour_fish.remove(fish_food)
            neighbour_empty.append(fish_food)
            cur[fish_food] = empty()  # fish dies
            cur[r, c]['hunger'] = cur[r, c]['hunger'] - 1

    # bear moves
    if neighbour_empty:  # check if the list is not empty
        bear_moves = random.choice(neighbour_empty)  # pick a random empty cell from the list
        cur[bear_moves] = cur[r, c]   # moves to the new location
        cur[r, c] = empty()     # erase actual location

    return cur

def piranha_rules(cur, r, c, neighbour_fish, neighbour_empty, neighbour_bear, limit):
    # Set piranha color
    cur[r, c]['col'] = col_piranha


    # If there is a fish nearby, eat it
    if neighbour_fish != []:
        fish_location = random.choice(neighbour_fish)
        cur[fish_location] = empty()
        neighbour_fish.remove(fish_location)
        neighbour_empty.append(fish_location)
        print(f"fish eaten by pirahna --> pos {cur[r,c]}")
        cur[r, c]['stomach'] = cur[r, c]['stomach'] + 1
    elif cur[r, c]['type'] == 'piranha'  :
        cur[r, c]['day'] = cur[r, c]['day'] + 1

    # If there is a bear nearby, eat it
    if neighbour_bear != []:
        bear_location = random.choice(neighbour_bear)
        cur[bear_location] = empty()
        neighbour_bear.remove(bear_location)
        neighbour_empty.append(bear_location)
        print(f"bear eaten by piranhas --> pos {cur[r, c]}")
        cur[r, c]['stomach'] = cur[r, c]['stomach'] + 2
    elif cur[r, c]['type'] == 'piranha':
        cur[r, c]['day'] = cur[r, c]['day'] + 1

    elif cur[r, c]['type'] == 'piranha':
        if cur[r, c]['stomach'] <= (limit - 20):
            cur[r, c] ['col']= col_piranha

    elif cur[r, c]['type'] == 'piranha':
        cur[r, c]['col'] = col_pir_full_stomach

    #Pirahna dies due to overfeeding
    elif cur[r, c]['type'] == 'piranha':
        if cur[r, c]['stomach'] >= limit:
            print("overfeeding")
            cur[r, c] = empty()

    # Move piranha if there is an empty neighboring cell
    if cur[r, c]['type'] == 'piranha':
        if neighbour_empty != [] and cur[r, c]['day'] <= days_wo_eating :
            piranha_location = random.choice(neighbour_empty)
            cur[piranha_location] = cur[r, c]
            cur[r, c] = empty()
        else:
            cur[r, c]['col'] = col_pir_old

    return cur

def update(surface, cur, sz):
    # for each cell
    for r, c in np.ndindex(cur.shape):
        # if there is a bear or a fish
        if cur[r, c]['type'] == "fish" or cur[r, c]['type'] == "bear" or cur[r, c]['type'] == "piranha":
            # calculate neighbours and find the empty and the fish neighbours (other bears are not important, currently)
            neighbours = get_neighbors(cur, r, c)
            neighbour_fish, neighbour_empty, neighbour_bear, neighbour_piranha = neighbour_fish_empty_bear(cur, neighbours)
            # For checking the state of the animal (correctness)
            print(f"Pos: ({r},{c}), Animal: {cur[r, c]}")
            # if it is a fish
            if cur[r, c]['type'] == "fish":
                cur = fish_rules(cur, r, c, neighbour_fish, neighbour_empty)

            # if it is a bear
            if cur[r, c]['type'] == "bear":
                cur = bear_rules(cur, r, c, neighbour_fish, neighbour_empty)

            # if it is a piranha
            elif cur[r, c]['type'] == "piranha":
                cur = piranha_rules(cur, r, c, neighbour_fish, neighbour_empty, neighbour_bear, limit_pir)
    return cur

def draw_grid(surface,cur,sz):
    """Given a grid {cur}, the size of the drawn cells, and a surface to draw on. Draw the """
    for r, c in np.ndindex(cur.shape):
        col = col_empty # if the cell is empty, the color should be that of "empty"
        if cur[r, c]['type'] != 'empty': # if the cell is not empty update the color according to its content
            col = cur[r, c]['col']
        pygame.draw.rect(surface, col, (c * sz, r * sz, sz - 1, sz - 1))

def main(dimx, dimy, cellsize,fish,bear,piranha):
    pygame.init()
    surface = pygame.display.set_mode((dimx * cellsize, dimy * cellsize))
    pygame.display.set_caption("Animal Kingdom")

    cells = init(dimx, dimy,fish,bear,piranha) # creates the grid representation

    clock = pygame.time.Clock()
    speed_count = 0
    while True:
        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        surface.fill(col_grid)

        if speed_count % SPEED == 0:   # slows down the time step without slowing down the frame rate
            # update grid
            print(f"timestep: {speed_count // SPEED}")
            cells = update(surface, cells, cellsize)
        # draw the updated grid
        draw_grid(surface, cells, cellsize)
        pygame.display.update()
        clock.tick(FRAMES_PER_SECOND)
        speed_count = speed_count +1

if __name__ == "__main__":
    fish = 100
    bear = 8
    piranha = 2
    main(40, 10, 16,fish,bear,piranha)