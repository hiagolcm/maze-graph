import random

def solve(start: Node, end: Node, visit):
    ref_visited_num = start.visited + 1

    start.visited = ref_visited_num

    stack = [start]

    while len(stack) > 0:
        current = stack.pop()
        current.visited = ref_visited_num
        visit(current)

        if current == end:
            return True

        neighbors = current.get_reachable_neighbors()

        for n in neighbors:
            if n != None and n.visited != ref_visited_num:
                stack.append(n)

    return False