import heapq

graph = {
    'A': [(4, 'B'), (2, 'C')],
    'B': [(4, 'A'), (1, 'C'), (5, 'D')],
    'C': [(2, 'A'), (1, 'B'), (8, 'D')],
    'D': [(5, 'B'), (8, 'C'), (3, 'E')],
    'E': [(3, 'D')]
}

def get_neighbors(node):
    return graph.get(node, [])

print(get_neighbors('A'))

# file = []

# dist = [
#     (0, 'A'),
#     (float('inf'), 'B'),
#     (float('inf'), 'C'),
#     (float('inf'), 'D'),
#     (float('inf'), 'E')
# ]

# for d in dist:
#     heapq.heappush(file, d)
    
# print(file)
# print(heapq.heappop(file))
# print(file)