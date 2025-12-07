import pygame
from queue import PriorityQueue

# --- INITIALIZE FONTS ---
pygame.init()
pygame.font.init()
# We use a standard font, size 15 to fit inside the squares
FONT = pygame.font.SysFont('arial', 15, bold=True)

WIDTH = 600
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("RESCUE 1122: ROUTE BUILDER")

# --- COLOR DEFINITIONS ---
RED = (255, 0, 0)       # Closed nodes
GREEN = (0, 255, 0)     # Open nodes
YELLOW = (255, 255, 0)  # Path
WHITE = (255, 255, 255) # Empty
BLACK = (0, 0, 0)       # Wall
ORANGE = (255, 165, 0)  # Start
GREY = (128, 128, 128)  # Grid Lines
TURQUOISE = (64, 224, 208) # End
PURPLE = (200, 160, 255)   # Numbered Nodes (Light Purple background for visibility)

class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows
        
        # [NEW] Attribute to hold the text ("S", "E", "1", etc.)
        self.text = "" 

    def get_pos(self):
        return self.row, self.col

    def is_barrier(self):
        return self.color == BLACK

    def reset(self):
        self.color = WHITE
        self.text = ""

    # --- STATE SETTERS ---
    def make_start(self):
        self.color = ORANGE
        self.text = "S"

    def make_numbered(self, number):
        self.color = PURPLE
        self.text = str(number)

    def make_end(self):
        self.color = TURQUOISE
        self.text = "E"

    def make_barrier(self):
        self.color = BLACK
        self.text = ""

    def make_closed(self):
        if self.color not in (YELLOW, ORANGE, TURQUOISE, PURPLE):
            self.color = RED

    def make_open(self):
        if self.color not in (YELLOW, ORANGE, TURQUOISE, PURPLE):
            self.color = GREEN

    def make_path(self):
        self.color = YELLOW
        # Keep the text visible even if path goes over it
        # (We don't wipe self.text here)

    def draw(self, win):
        # 1. Draw the colored square
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))
        
        # 2. Draw the text (if any) centered in the square
        if self.text != "":
            # Render text in Black (or White if background is dark)
            text_color = (0, 0, 0)
            text_surf = FONT.render(self.text, True, text_color)
            
            # Math to center the text
            text_rect = text_surf.get_rect(center=(self.x + self.width/2, self.y + self.width/2))
            win.blit(text_surf, text_rect)

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False

def heuristic(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        # Don't overwrite the Start/End/Numbers colors with Yellow, 
        # just let the line flow through (or overwrite if you prefer standard look)
        if current.text == "": 
            current.make_path()
        draw()

def A_star_algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = heuristic(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + heuristic(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open() 

        draw()

        if current != start:
            current.make_closed() 

    return False

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    return grid

def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

def draw(win, grid, rows, width):
    win.fill(WHITE)
    for row in grid:
        for node in row:
            node.draw(win)
    draw_grid(win, rows, width)
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
    gap = width // rows
    x, y = pos
    row = x // gap
    col = y // gap
    return row, col

def main(win, width):
    ROWS = 30
    grid = make_grid(ROWS, width)
    
    stops = [] 
    
    # Modes: 'placing_stops' or 'placing_walls'
    mode = 'placing_stops'
    
    run = True
    while run:
        draw(win, grid, ROWS, width)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # --- LEFT MOUSE CLICK ---
            if pygame.mouse.get_pressed()[0]: 
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]

                # MODE 1: PLACING STOPS (Start -> 1 -> 2 -> 3...)
                if mode == 'placing_stops':
                    if node not in stops and not node.is_barrier():
                        stops.append(node)
                        
                        if len(stops) == 1:
                            node.make_start() # First click is always "S"
                        else:
                            # Use the index as the number (Start is index 0, so 1st stop is index 1)
                            # We subtract 1 so the text starts at "1"
                            number_label = len(stops) - 1 
                            node.make_numbered(number_label)

                # MODE 2: PLACING WALLS (After B is pressed)
                elif mode == 'placing_walls':
                    if node not in stops:
                        node.make_barrier()

            # --- RIGHT MOUSE CLICK (Reset Node) ---
            elif pygame.mouse.get_pressed()[2]: 
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                node.reset()
                if node in stops:
                    stops.remove(node)
                    # Note: Removing a stop mid-list might mess up numbering. 
                    # For simplicity, clear board if you make a mistake, or assume append-only.

            # --- KEYBOARD CONTROLS ---
            if event.type == pygame.KEYDOWN:
                
                # [B KEY] FINALIZE ROUTE & SWITCH TO WALL MODE
                if event.key == pygame.K_b:
                    if mode == 'placing_stops' and len(stops) > 1:
                        mode = 'placing_walls'
                        
                        # Turn the LAST clicked node into the END node ("E")
                        last_node = stops[-1]
                        last_node.make_end()
                        
                        pygame.display.set_caption("MODE: WALLS (Draw obstacles) - Press SPACE to Run")

                # [SPACE KEY] RUN A*
                if event.key == pygame.K_SPACE and len(stops) > 1:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)

                    for i in range(len(stops) - 1):
                        start_node = stops[i]
                        end_node = stops[i+1]
                        
                        A_star_algorithm(lambda: draw(win, grid, ROWS, width), grid, start_node, end_node)
                        
                        # Clean up colors to ensure text remains visible
                        if i == 0:
                            start_node.make_start()
                        elif i != len(stops) - 2: 
                            # Restore numbered look if it wasn't the final leg
                            # i is index in 0..N. stops[i] is start of leg. 
                            # We want to restore the text of the start node of this leg (unless it's S)
                            pass # The reconstruct path logic handles the yellow line

                # [C KEY] CLEAR BOARD
                if event.key == pygame.K_c:
                    stops = []
                    grid = make_grid(ROWS, width)
                    mode = 'placing_stops'
                    pygame.display.set_caption("RESCUE 1122: ROUTE BUILDER")

    pygame.quit()

main(WIN, WIDTH)