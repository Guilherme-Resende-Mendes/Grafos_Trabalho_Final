import math

class Graph:
    def __init__(self):
        self.nodes = set()
        self.edges = {}
        self.arcs = {}
        self.required_nodes = {}
        self.depot_node = -1
        self.capacity = -1
        self.adj = {}
        self._next_arc_id = 1

    def add_node(self, node_id):
        self.nodes.add(node_id)
        if node_id not in self.adj:
            self.adj[node_id] = {}

    def add_edge(self, u, v, cost, demand=0, service_cost=0):
        self.add_node(u)
        self.add_node(v)
        self.edges[(u, v)] = {'cost': cost, 'demand': demand, 'service_cost': service_cost}
        self.edges[(v, u)] = {'cost': cost, 'demand': demand, 'service_cost': service_cost}
        self.adj[u][v] = cost
        self.adj[v][u] = cost

    def add_arc(self, u, v, cost, demand=0, service_cost=0, arc_id=None):
        self.add_node(u)
        self.add_node(v)
        if arc_id is None:
            arc_id = self._next_arc_id
            self._next_arc_id += 1
        self.arcs[(u, v)] = {'cost': cost, 'demand': demand, 'service_cost': service_cost, 'id': arc_id}
        self.adj[u][v] = cost

    def set_required_node(self, node_id, demand, service_cost):
        self.required_nodes[node_id] = {'demand': demand, 'service_cost': service_cost}

    def read_instance(self, file_path):
        with open(file_path, 'r') as f:
            lines = f.readlines()

        section = None
        self._next_arc_id = 1

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if "Capacity:" in line:
                self.capacity = int(line.split(':')[1].strip())
            elif "Depot Node:" in line:
                self.depot_node = int(line.split(':')[1].strip())
            elif "#Required N:" in line:
                section = "ReN"
            elif "#Required E:" in line:
                section = "ReE"
            elif "#Required A:" in line:
                section = "ReA"
            elif "ReN." in line:
                section = "ReN_data"
                continue
            elif "ReE." in line:
                section = "ReE_data"
                continue
            elif "ReA." in line:
                section = "ReA_data"
                continue
            elif "ARC	FROM" in line or "ARC FROM" in line:
                section = "Travel_only_arc"
                continue
            elif "EDGE	FROM" in line or "EDGE FROM" in line:
                section = "Travel_only_edge"
                continue

            parts = line.split()
            if section == "ReN_data" and len(parts) >= 3:
                try:
                    node_id = int(parts[0].replace('N', ''))
                    demand = int(parts[1])
                    service_cost = int(parts[2])
                    self.set_required_node(node_id, demand, service_cost)
                except (ValueError, IndexError):
                    continue

            elif section == "ReE_data" and len(parts) >= 6:
                try:
                    u = int(parts[1])
                    v = int(parts[2])
                    cost = int(parts[3])
                    demand = int(parts[4])
                    service_cost = int(parts[5])
                    self.add_edge(u, v, cost, demand, service_cost)
                except (ValueError, IndexError):
                    continue

            elif section == "ReA_data" and len(parts) >= 6:
                arc_label = parts[0]
                if arc_label.startswith('A') and arc_label[1:].isdigit():
                    try:
                        arc_id = int(arc_label[1:])
                        u = int(parts[1])
                        v = int(parts[2])
                        cost = int(parts[3])
                        demand = int(parts[4])
                        service_cost = int(parts[5])
                        self.add_arc(u, v, cost, demand, service_cost, arc_id=arc_id)
                    except (ValueError, IndexError):
                        continue

            elif section == "Travel_only_arc" and len(parts) >= 4:
                try:
                    u = int(parts[1])
                    v = int(parts[2])
                    cost = int(parts[3])
                    self.add_arc(u, v, cost, arc_id=self._next_arc_id)
                    self._next_arc_id += 1
                except (ValueError, IndexError):
                    continue

            elif section == "Travel_only_edge" and len(parts) >= 4:
                try:
                    u = int(parts[1])
                    v = int(parts[2])
                    cost = int(parts[3])
                    self.add_edge(u, v, cost)
                except (ValueError, IndexError):
                    continue

        # Adiciona todos os nós mencionados
        for u, v in self.edges:
            self.add_node(u)
            self.add_node(v)
        for u, v in self.arcs:
            self.add_node(u)
            self.add_node(v)
        for node_id in self.required_nodes:
            self.add_node(node_id)
        self.add_node(self.depot_node)

    def get_shortest_path_costs(self):
        dist = {}
        for u in self.nodes:
            for v in self.nodes:
                dist[(u, v)] = 0 if u == v else math.inf
            for v, cost in self.adj.get(u, {}).items():
                dist[(u, v)] = cost

        for k in self.nodes:
            for i in self.nodes:
                for j in self.nodes:
                    if dist[(i, k)] + dist[(k, j)] < dist[(i, j)]:
                        dist[(i, j)] = dist[(i, k)] + dist[(k, j)]
        return dist
