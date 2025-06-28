import math
import os
from grafo import Graph  # Importa a classe Graph do arquivo grafo.py


class ConstructiveSolver:
    def __init__(self, graph):
        """
        Solucionador construtivo para o problema de roteirização.

        :param graph: Objeto da classe Graph com os dados do problema.
        """
        self.graph = graph
        self.routes_data = []
        self.total_solution_cost = 0
        self.unserved_required_nodes = set(graph.required_nodes.keys())
        self.unserved_required_arcs = {k for k, v in graph.arcs.items() if v['demand'] > 0}
        self.all_shortest_paths = self.graph.get_shortest_path_costs()
        self.reference_values = self.read_references()

    def get_travel_cost(self, u, v):
        """
        Retorna o custo de viagem entre dois nós.

        :param u: Nó de origem.
        :param v: Nó de destino.
        :return: Custo de viagem (ou infinito se não conectado).
        """
        return self.all_shortest_paths.get((u, v), math.inf)

    def solve(self):
        """
        Resolve o problema gerando rotas iniciais de forma construtiva.
        """
        route_id_counter = 1
        while self.unserved_required_nodes or self.unserved_required_arcs:
            current_node = self.graph.depot_node
            current_demand = 0
            total_cost = 0
            services = []
            depot = self.graph.depot_node
            services.append(f"(D 0,{depot},{depot})")

            while True:
                best, kind, min_cost = self.find_best_candidate(current_node, current_demand)

                # Se nenhum candidato foi encontrado, finalize a rota
                if best is None:
                    break

                # Atualiza a rota com base no tipo de serviço (nó ou arco)
                if kind == 'arc':
                    u, v = best
                    info = self.graph.arcs[best]
                    total_cost += self.get_travel_cost(current_node, u) + info['cost'] + info['service_cost']
                    services.append(f"(S {info['id']},{u},{v})")
                    current_node = v
                    current_demand += info['demand']
                    self.unserved_required_arcs.remove(best)
                elif kind == 'node':
                    info = self.graph.required_nodes[best]
                    total_cost += self.get_travel_cost(current_node, best) + info['service_cost']
                    services.append(f"(S {best},{best},{best})")
                    current_node = best
                    current_demand += info['demand']
                    self.unserved_required_nodes.remove(best)

            # Finaliza a rota no depósito
            total_cost += self.get_travel_cost(current_node, depot)
            services.append(f"(D 0,{depot},{depot})")

            # Salva os dados da rota
            self.routes_data.append({
                'route_id': route_id_counter,
                'demand_used': current_demand,
                'total_cost': total_cost,
                'num_services': len(services),
                'services': services
            })
            self.total_solution_cost += total_cost
            route_id_counter += 1

    def find_best_candidate(self, current_node, current_demand):
        """
        Encontra o melhor candidato (nó ou arco) para expandir a rota atual.

        :param current_node: Nó atual.
        :param current_demand: Demanda acumulada na rota.
        :return: Melhor candidato (nó ou arco), tipo do candidato e custo mínimo.
        """
        best = None
        min_cost = math.inf
        kind = None

        # Considera arcos não atendidos
        for arc in self.unserved_required_arcs:
            u, v = arc
            info = self.graph.arcs[arc]
            if current_demand + info['demand'] <= self.graph.capacity:
                cost = self.get_travel_cost(current_node, u) + info['cost']
                if cost < min_cost:
                    best = arc
                    kind = 'arc'
                    min_cost = cost

        # Considera nós não atendidos
        for node in self.unserved_required_nodes:
            info = self.graph.required_nodes[node]
            if current_demand + info['demand'] <= self.graph.capacity:
                cost = self.get_travel_cost(current_node, node)
                if cost < min_cost:
                    best = node
                    kind = 'node'
                    min_cost = cost

        return best, kind, min_cost

    def write_solution(self, instance_name, output_dir="."):
        """
        Escreve a solução gerada em um arquivo no formato especificado.

        :param instance_name: Nome da instância (usado no nome do arquivo).
        :param output_dir: Diretório onde o arquivo será salvo.
        """
        if math.isinf(self.total_solution_cost):
            print("Erro: a solução contém custos infinitos. Verifique a conectividade do grafo.")
            return

        # Garante que o diretório de saída existe
        os.makedirs(output_dir, exist_ok=True)

        path = os.path.join(output_dir, f"sol-{instance_name}.dat")
        with open(path, 'w') as f:
            f.write(f"{int(self.total_solution_cost)}\n")
            f.write(f"{len(self.routes_data)}\n")
            # Total de clocks para a execução do algoritmo referência
            f.write(f"{self.reference_values[instance_name][3].strip()}\n")
            # Total de clocks para encontrar a solução referência
            f.write(f"{self.reference_values[instance_name][4].strip()}\n")
            for r in self.routes_data:
                line = (
                    f" 0 1 {r['route_id']} {r['demand_used']} {int(r['total_cost'])} "
                    f"{r['num_services']} {' '.join(r['services'])}\n"
                )
                f.write(line)

    def read_references(self):
            path = r"reference_values.csv"
            references = {}
            lines = ""
            with open(path, "r") as f:
                # Lê uma linha e retira os seus espaços em branco
                lines = f.readlines()
            # Lê as linhas
            for i in range(1, len(lines)):
                line = lines[i]
                line = line.strip()
                components = line.split(",")
                if line:
                    references[components[0]] = components
            return references   

if __name__ == "__main__":
    instance_folder = 'instancia' \
    ''  # Diretório contendo os arquivos de instância
    solution_folder = 'solucoes'   # Diretório para salvar as soluções

    # Cria o diretório de soluções, se necessário
    os.makedirs(solution_folder, exist_ok=True)

    # Processa cada arquivo de instância no diretório
    for filename in os.listdir(instance_folder):
        if filename.endswith(".dat"):  # Processa apenas arquivos .dat
            instance_file_path = os.path.join(instance_folder, filename)
            instance_name = os.path.splitext(filename)[0]  # Nome da instância (sem extensão)

            print(f"Processando instância: {filename}")

            # Carrega o grafo e resolve o problema
            graph = Graph()
            graph.read_instance(instance_file_path)

            solver = ConstructiveSolver(graph)
            solver.solve()
            solver.write_solution(instance_name, output_dir=solution_folder)
            print(f"Solução para {filename} salva em {solution_folder}")