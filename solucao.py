import math
from grafo import Graph
import os # Import the os module

class ConstructiveSolver:
    def __init__(self, graph):
        self.graph = graph
        self.routes_data = []
        self.total_solution_cost = 0
        self.unserved_required_nodes = set(graph.required_nodes.keys())
        self.unserved_required_arcs = {k for k, v in graph.arcs.items() if v['demand'] > 0}
        self.all_shortest_paths = self.graph.get_shortest_path_costs()

    def get_travel_cost(self, u, v):
        return self.all_shortest_paths.get((u, v), math.inf)

    def solve(self):
        route_id_counter = 1
        while self.unserved_required_nodes or self.unserved_required_arcs:
            current_node = self.graph.depot_node
            current_demand = 0
            total_cost = 0
            services = []
            depot = self.graph.depot_node
            services.append(f"(D 0,{depot},{depot})")

            while True:
                best = None
                min_cost = math.inf
                kind = None

                for arc in self.unserved_required_arcs:
                    u, v = arc
                    info = self.graph.arcs[arc]
                    if current_demand + info['demand'] <= self.graph.capacity:
                        cost = self.get_travel_cost(current_node, u) + info['cost']
                        if cost < min_cost:
                            best = arc
                            kind = 'arc'
                            min_cost = cost

                for node in self.unserved_required_nodes:
                    info = self.graph.required_nodes[node]
                    if current_demand + info['demand'] <= self.graph.capacity:
                        cost = self.get_travel_cost(current_node, node)
                        if cost < min_cost:
                            best = node
                            kind = 'node'
                            min_cost = cost

                if best is None:
                    break

                if kind == 'arc':
                    u, v = best
                    info = self.graph.arcs[best]
                    total_cost += self.get_travel_cost(current_node, u) + info['cost'] + info['service_cost']
                    services.append(f"(S {info['id']},{u},{v})")
                    current_node = v
                    current_demand += info['demand']
                    self.unserved_required_arcs.remove(best)
                else:
                    info = self.graph.required_nodes[best]
                    total_cost += self.get_travel_cost(current_node, best) + info['service_cost']
                    services.append(f"(S {best},{best},{best})")
                    current_node = best
                    current_demand += info['demand']
                    self.unserved_required_nodes.remove(best)

            total_cost += self.get_travel_cost(current_node, depot)
            services.append(f"(D 0,{depot},{depot})")

            self.routes_data.append({
                'route_id': route_id_counter,
                'demand_used': current_demand,
                'total_cost': total_cost,
                'num_services': len(services),
                'services': services
            })
            self.total_solution_cost += total_cost
            route_id_counter += 1

    def write_solution(self, instance_name, output_dir="."):
        if math.isinf(self.total_solution_cost):
            print("Erro: a solução contém custos infinitos. Verifique conectividade do grafo.")
            return

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True) # Create the directory if it doesn't exist

        path = f"{output_dir}/sol-{instance_name}.dat"
        with open(path, 'w') as f:
            f.write(f"{int(self.total_solution_cost)}\n")
            f.write(f"{len(self.routes_data)}\n")
            for r in self.routes_data:
                line = (
                    f" 0 1 {r['route_id']} {r['demand_used']} {int(r['total_cost'])} "
                    f"{r['num_services']} {' '.join(r['services'])}\n"
                )
                f.write(line)

if __name__ == "__main__":
    instance_folder = 'instancia'  # Folder containing instance files
    solution_folder = 'solucoes'   # Folder for solution files

    # Create the solution folder if it doesn't exist
    os.makedirs(solution_folder, exist_ok=True)

    # Iterate over files in the instance folder
    for filename in os.listdir(instance_folder):
        if filename.endswith(".dat"):  # Process only .dat files
            instance_file_path = os.path.join(instance_folder, filename)
            instance_name = os.path.splitext(filename)[0] # Get filename without extension

            print(f"Processing instance: {filename}")

            graph = Graph()
            graph.read_instance(instance_file_path)

            solver = ConstructiveSolver(graph)
            solver.solve()
            solver.write_solution(instance_name, output_dir=solution_folder)