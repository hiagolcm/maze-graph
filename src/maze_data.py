from maze import Maze, Node


def average_corridor_length(nodes):
    neighbors = {}
    degree = {}

    for node in nodes:
        reachable = node.get_reachable_neighbors()
        neighbors[id(node)] = reachable
        degree[id(node)] = len(reachable)

    lengths = []
    seen = set()

    for node in nodes:
        node_id = id(node)
        if degree[node_id] == 2:
            continue

        for start in neighbors[node_id]:
            if (node_id, id(start)) in seen or (id(start), node_id) in seen:
                continue

            if degree[id(start)] != 2:
                seen.add((node_id, id(start)))
                continue

            length = 0
            prev = node
            current = start
            chain = set()

            while degree[id(current)] == 2 and id(current) not in chain:
                chain.add(id(current))
                length += 1
                seen.add((id(prev), id(current)))

                nxt = None
                for candidate in neighbors[id(current)]:
                    if candidate is not prev:
                        nxt = candidate
                        break

                if nxt is None:
                    break

                prev = current
                current = nxt

            seen.add((id(prev), id(current)))

            if degree[id(current)] != 2:
                lengths.append(length)

    if not lengths:
        return 0.0

    return sum(lengths) / len(lengths)


class MazeData:
    def __init__(self):
        self.total_nodes = 0
        self.expanded_nodes = 0
        self.discovered_nodes = 0
        self.total_edges = 0
        self.degrees = [0, 0, 0, 0, 0]
        self.average_degree = 0.0
        self.average_corridor_length = 0.0
        self.build_time = 0.0
        self.solve_time = 0.0
        self.total_dead_ends = 0
        self.total_junctions = 0

    def collect_from(self, maze: Maze):
        nodes = []

        def collect(node: Node):
            self.total_nodes += 1
            nodes.append(node)

            if node.state == "DISCOVERED":
                self.discovered_nodes += 1
            elif node.state == "EXPANDED":
                self.expanded_nodes += 1
                self.discovered_nodes += 1

            degree = len(node.get_reachable_neighbors())
            if 0 <= degree <= 4:
                self.degrees[degree] += 1
            self.total_edges += degree

        maze.apply_for_each_node(lambda node: collect(node))

        self.average_degree = (
            self.total_edges / self.total_nodes if self.total_nodes else 0.0
        )
        self.average_corridor_length = average_corridor_length(nodes)
        self.build_time = maze.build_time
        self.solve_time = maze.solve_time
        self.total_dead_ends = self.degrees[1]
        self.total_junctions = self.degrees[3] + self.degrees[4]

    def print_data(self):
        print(self.degrees)
        print(
            f"expanded: {self.expanded_nodes}\n"
            f"discovered: {self.discovered_nodes}\n"
            f"edges: {self.total_edges}\n"
            f"total_dead_ends: {self.total_dead_ends}\n"
            f"total_junctions: {self.total_junctions}\n"
            f"average_degree: {self.average_degree}\n"
            f"average_corridor_length: {self.average_corridor_length}\n"
            f"solve_time: {self.solve_time}\n"
            f"build_time: {self.build_time}"
        )

    def as_dict(self):
        return {
            "build_time_ms": self.build_time,
            "solve_time_ms": self.solve_time,
            "total_nodes": self.total_nodes,
            "expanded_nodes": self.expanded_nodes,
            "discovered_nodes": self.discovered_nodes,
            "total_edges": self.total_edges,
            "average_degree": self.average_degree,
            "average_corridor_length": self.average_corridor_length,
            "dead_ends": self.total_dead_ends,
            "junctions": self.total_junctions,
            "degree_0": self.degrees[0],
            "degree_1": self.degrees[1],
            "degree_2": self.degrees[2],
            "degree_3": self.degrees[3],
            "degree_4": self.degrees[4],
        }
