import random


class Neighbor:
    def __init__(self, node, is_path_free):
        self.node = node
        self.is_path_free = is_path_free


class Node:
    def __init__(self, left_node, up_node, right_node, down_node, x, y):
        self.visited = False
        self.left_node = Neighbor(left_node, False)
        self.up_node = Neighbor(up_node, False)
        self.right_node = Neighbor(right_node, False)
        self.down_node = Neighbor(down_node, False)
        self.x = x
        self.y = y

    def is_dead_end(self):
        for link in (self.left_node, self.up_node, self.right_node, self.down_node):
            if link.node is not None and not link.node.visited:
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


class Maze:
    def __init__(self, w, h, builder, solver):
        first = None
        last = None
        previous_line = None
        self.nodes = []

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

            self.nodes.extend(ith_line)
            previous_line = ith_line

        self.first = first
        self.last = last
        self.end = last
        self.solver = solver

        builder(first)
        self.clear_visited()

    def clear_visited(self):
        # Zera visited em todas as celulas. self.nodes guarda a grade inteira,
        # entao nao precisa percorrer os vizinhos (o que fica caro em labirintos grandes).
        for node in self.nodes:
            node.visited = False

    def open_entrance_and_exit(self, exit_open=True):
        self.first.up_node.is_path_free = True

        if exit_open:
            self.last.down_node.is_path_free = True

    def apply_for_each_node(self, visit):
        self.clear_visited()

        start = self.first
        start.visited = True
        stack = [start]

        while stack:
            node = stack.pop()
            visit(node)

            neighbors = [
                node.left_node.node,
                node.right_node.node,
                node.up_node.node,
                node.down_node.node,
            ]

            for neighbor in neighbors:
                if neighbor is not None and not neighbor.visited:
                    neighbor.visited = True
                    stack.append(neighbor)

    def pick_end(self, random_end=False, rng=random):
        # Escolhe a celula de saida. Por padrao e a do canto inferior direito.
        # Com random_end=True, sorteia qualquer celula, menos a entrada.
        # rng permite passar um random.Random proprio para sortear sem mexer
        # na semente global (o benchmark usa isso).
        if not random_end:
            return self.last

        # nodes[0] e a entrada; sortear entre os demais sem montar uma lista nova
        # (rng.choice sobre a lista sem a entrada consome o mesmo numero aleatorio)
        return self.nodes[1 + rng.randrange(len(self.nodes) - 1)]

    def solve(self, draw_node, random_end=False, rng=random):
        # A entrada e sempre o canto superior esquerdo. A saida (self.end) e o
        # canto inferior direito, ou uma celula sorteada se random_end=True.
        self.clear_visited()
        self.end = self.pick_end(random_end, rng)
        return self.solver(self.first, self.end, draw_node)
