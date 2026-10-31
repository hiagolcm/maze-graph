import random


class Neighbor:
    def __init__(self, node, is_path_free):
        self.node = node
        self.is_path_free = is_path_free


class Node:
    def __init__(self, left_node, up_node, right_node, down_node, x, y):
        self.visited = 0
        self.left_node = Neighbor(left_node, False)
        self.up_node = Neighbor(up_node, False)
        self.right_node = Neighbor(right_node, False)
        self.down_node = Neighbor(down_node, False)
        self.x = x
        self.y = y

    def is_dead_end(self, ref_visited_num):
        for link in (self.left_node, self.up_node, self.right_node, self.down_node):
            if link.node is not None and link.node.visited != ref_visited_num:
                return False
        return True

    def open_passage(self, link: Neighbor):
        link.is_path_free = True
        other = link.node
        for back in (other.left_node, other.up_node, other.right_node, other.down_node):
            if back.node is self:
                back.is_path_free = True
                return

    def get_links(self):
        neighbors = [
            self.left_node,
            self.right_node,
            self.up_node,
            self.down_node,
        ]

        random.shuffle(neighbors)

        return neighbors


    def get_reachable_neighbors(self):
        links = [
            self.left_node,
            self.right_node,
            self.up_node,
            self.down_node,
        ]

        reachable = []

        for l in links:
            if l.node != None and l.is_path_free:
                reachable.append(l.node)

        random.shuffle(reachable)

        return reachable


def navigate(start: Node, visit):
    ref_visited_num = start.visited + 1

    stack = [start]

    while stack:
        node = stack.pop()
        node.visited = ref_visited_num
        visit(node)

        neighbors = [
            node.left_node.node,
            node.right_node.node,
            node.up_node.node,
            node.down_node.node,
        ]

        for neighbor in neighbors:
            if neighbor is not None and neighbor.visited != ref_visited_num:
                stack.append(neighbor)


class Maze:
    def __init__(self, w, h):
        first = None
        last = None
        previous_line = None

        for i in range(h):
            ith_line = []

            for j in range(w):
                left_node = None if j == 0 else ith_line[j - 1]
                up_node = None if i == 0 else previous_line[j]

                new_node = Node(left_node, up_node, None, None, j, i)
                last = new_node

                if i == 0 and j == 0:
                    first = new_node

                if left_node:
                    left_node.right_node = Neighbor(new_node, False)
                if up_node:
                    up_node.down_node = Neighbor(new_node, False)
                ith_line.append(new_node)

            previous_line = ith_line

        self.first = first
        self.last = last

    def open_entrance_and_exit(self):
        self.first.up_node.is_path_free = True
        self.last.down_node.is_path_free = True
