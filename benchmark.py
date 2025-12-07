import time
import random
from queue import PriorityQueue

# --- SETUP ---
class Node:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.neighbors = []
        self.is_barrier = False

    def get_pos(self):
        return self.row, self.col

    def __lt__(self, other):
        return False

def heuristic(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def create_grid(rows):
    grid = []
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j)
            # 15% barrier chance
            if random.random() < 0.15: 
                node.is_barrier = True
            grid[i].append(node)
    return grid

def update_neighbors(grid, rows):
    for row in grid:
        for node in row:
            if node.is_barrier:
                continue
            r, c = node.row, node.col
            if r < rows - 1 and not grid[r + 1][c].is_barrier:
                node.neighbors.append(grid[r + 1][c])
            if r > 0 and not grid[r - 1][c].is_barrier:
                node.neighbors.append(grid[r - 1][c])
            if c < rows - 1 and not grid[r][c + 1].is_barrier:
                node.neighbors.append(grid[r][c + 1])
            if c > 0 and not grid[r][c - 1].is_barrier:
                node.neighbors.append(grid[r][c - 1])

def run_search(grid, start, end, algo_type="A_Star"):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    
    f_score = {node: float("inf") for row in grid for node in row}
    
    h = heuristic(start.get_pos(), end.get_pos())
    
    if algo_type == "Dijkstra":
        f_score[start] = 0
    elif algo_type == "Greedy":
        f_score[start] = h
    else: # A_Star
        f_score[start] = h

    open_set_hash = {start}
    nodes_visited = 0 

    while not open_set.empty():
        current = open_set.get()[2]
        open_set_hash.remove(current)
        nodes_visited += 1

        if current == end:
            return True, nodes_visited, g_score[end]

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                g_score[neighbor] = temp_g_score
                
                h_val = heuristic(neighbor.get_pos(), end.get_pos())
                
                if algo_type == "Dijkstra":
                    f_score[neighbor] = temp_g_score
                elif algo_type == "Greedy":
                    f_score[neighbor] = h_val
                else: # A_Star
                    f_score[neighbor] = temp_g_score + h_val
                
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
    
    return False, nodes_visited, 0

# --- EXPERIMENT RUNNER ---
def run_experiment():
    # --- TABLE FORMATTING ---
    w_grid = 6
    w_algo = 10
    w_time = 10
    w_nodes = 13
    w_len = 11

    # header that displays the time, nodes visited, and path length   
    header = (f"| {'Grid':^{w_grid}} | {'Algorithm':<{w_algo}} | "
              f"{'Time (ms)':>{w_time}} | {'Nodes Visited':>{w_nodes}} | {'Path Length':>{w_len}} |")
    
    separator = "-" * len(header)

    print(separator)
    print(header)
    print(separator)

    # Varying grid sizes
    sizes = [50, 100, 150, 200, 250] 
    
    for size in sizes:
        valid_trials = 0
        while valid_trials < 1: 
            grid = create_grid(size)
            update_neighbors(grid, size)
            
            start = grid[0][0]
            end = grid[size-1][size-1]
            start.is_barrier = False
            end.is_barrier = False

            # 1. RUN DIJKSTRA
            t0 = time.perf_counter()
            found_d, visited_d, len_d = run_search(grid, start, end, "Dijkstra")
            t1 = time.perf_counter()
            time_d = (t1 - t0) * 1000

            if not found_d or visited_d < size * 2: 
                continue 

            # 2. RUN A*
            t0 = time.perf_counter()
            found_a, visited_a, len_a = run_search(grid, start, end, "A_Star")
            t1 = time.perf_counter()
            time_a = (t1 - t0) * 1000

            # 3. RUN GREEDY
            t0 = time.perf_counter()
            found_g, visited_g, len_g = run_search(grid, start, end, "Greedy")
            t1 = time.perf_counter()
            time_g = (t1 - t0) * 1000

            # --- PRINT ROWS ---
            # Dijkstra
            print(f"| {size:^{w_grid}} | {'Dijkstra':<{w_algo}} | {time_d:>{w_time}.4f} | {visited_d:>{w_nodes}} | {len_d:>{w_len}} |")
            
            # A*
            print(f"| {size:^{w_grid}} | {'A*':<{w_algo}} | {time_a:>{w_time}.4f} | {visited_a:>{w_nodes}} | {len_a:>{w_len}} |")
            
            # Greedy
            print(f"| {size:^{w_grid}} | {'Greedy':<{w_algo}} | {time_g:>{w_time}.4f} | {visited_g:>{w_nodes}} | {len_g:>{w_len}} |")
            
            print(separator)
            
            valid_trials += 1

if __name__ == "__main__":
    run_experiment()