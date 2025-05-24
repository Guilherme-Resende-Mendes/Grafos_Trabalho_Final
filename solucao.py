import math
from collections import defaultdict
import heapq # Necessário para o algoritmo de Dijkstra

class SolucaoInicial:
    def __init__(self, grafo):
        self.grafo = grafo
        self.capacidade = grafo.capacidade
        self.depot = grafo.depot
        self.rotas = []  # Lista de rotas, onde cada rota é uma sequência de vértices
        self.custo_total = 0
        
        # Dicionário para armazenar as demandas dos serviços requeridos.
        # Como não podemos modificar Grafo, populamos isso aqui.
        self.demanda_servicos = defaultdict(int)
        self._popular_demandas_servicos()

        # Dicionário auxiliar para obter o peso de uma aresta/arco rapidamente
        self._pesos_arestas_arcos = self._construir_pesos_map()

    def _popular_demandas_servicos(self):
        """
        Popula o dicionário de demandas de serviços a partir do grafo.
        Assume demanda 1 para todos os serviços requeridos se não especificado.
        """
        for v in self.grafo.VR:
            self.demanda_servicos[v] = 1 # Vértice requerido tem demanda 1
        
        for u, v, _ in self.grafo.ER:
            # Arestas requeridas: usa a tupla ordenada (menor, maior) como chave
            self.demanda_servicos[tuple(sorted((u, v)))] = 1
        
        for u, v, _ in self.grafo.AR:
            # Arcos requeridos: usa a tupla (origem, destino) como chave
            self.demanda_servicos[(u, v)] = 1

    def _construir_pesos_map(self):
        """
        Constrói um mapa de pesos para acesso rápido a custos de arestas/arcos.
        Chaves: (u, v) para arcos, (sorted(u,v)) para arestas.
        """
        pesos_map = {}
        for u, v, peso in self.grafo.arestas:
            pesos_map[tuple(sorted((u, v)))] = peso
        for u, v, peso in self.grafo.arcos:
            pesos_map[(u, v)] = peso
        return pesos_map

    def _get_peso_aresta_arco(self, u, v):
        """
        Obtém o peso de uma aresta ou arco entre u e v.
        Retorna math.inf se não houver conexão direta.
        """
        # Tenta como arco (u,v)
        if (u, v) in self._pesos_arestas_arcos:
            return self._pesos_arestas_arcos[(u, v)]
        # Tenta como aresta (u,v) ou (v,u)
        sorted_edge = tuple(sorted((u, v)))
        if sorted_edge in self._pesos_arestas_arcos:
            return self._pesos_arestas_arcos[sorted_edge]
        return math.inf # Não encontrou aresta/arco entre u e v

    def _dijkstra(self, start_node):
        """
        Implementação do Dijkstra dentro da classe SolucaoInicial.
        Retorna distâncias e dicionário de predecessores.
        """
        distances = {vertex: math.inf for vertex in self.grafo.vertices}
        distances[start_node] = 0
        priority_queue = [(0, start_node)]
        previous_nodes = {vertex: None for vertex in self.grafo.vertices}

        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)

            if current_distance > distances[current_node]:
                continue

            # Iterar sobre os vizinhos do grafo (arestas e arcos)
            # A classe Grafo tem self._vizinhos
            for neighbor, weight in self.grafo._vizinhos[current_node]:
                distance = current_distance + weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous_nodes[neighbor] = current_node
                    heapq.heappush(priority_queue, (distance, neighbor))
        return distances, previous_nodes

    def _get_path(self, previous_nodes, start_node, end_node):
        """
        Reconstrói o caminho a partir do dicionário de predecessores do Dijkstra.
        """
        path = []
        current = end_node
        while current is not None and current != start_node:
            path.insert(0, current)
            current = previous_nodes[current]
        
        if current == start_node: # Adiciona o nó inicial se o caminho foi encontrado
            path.insert(0, start_node)
        
        # Garante que o caminho começa no start_node e é válido
        return path if path and path[0] == start_node else []

    def construir_solucao(self):
        # Coleta todos os serviços requeridos e os padroniza para fácil acesso
        # Vértices: string (ex: 'V1')
        # Arestas: tupla ordenada (ex: ('V1', 'V2'))
        # Arcos: tupla (ex: ('V1', 'V2'))
        
        servicos_pendentes_original = set(self.grafo.VR)
        for u, v, _ in self.grafo.ER: # ER contém (u, v, peso)
            servicos_pendentes_original.add(tuple(sorted((u, v))))
        for u, v, _ in self.grafo.AR: # AR contém (u, v, peso)
            servicos_pendentes_original.add((u, v))
            
        atendidos = set() # Serviços requeridos que já foram atendidos

        # Algoritmo construtivo guloso (greedy)
        while len(atendidos) < len(servicos_pendentes_original):
            current_node = self.depot
            current_route_path = [self.depot] # A rota é uma sequência de vértices percorridos
            current_demand = 0
            
            # Loop para construir uma única rota
            while True:
                next_service_to_visit = None
                min_cost_to_next_service_segment = math.inf
                path_to_next_service_nodes = [] # O caminho em nós para o próximo serviço

                # Encontrar o caminho mais curto do nó atual para qualquer serviço requerido não atendido
                distances, previous_nodes = self._dijkstra(current_node)
                
                # Iterar sobre uma cópia dos serviços pendentes para evitar modificação durante a iteração
                for service_req in list(servicos_pendentes_original): 
                    if service_req in atendidos:
                        continue # Serviço já atendido

                    service_demand = self.get_demanda(service_req)
                    
                    if isinstance(service_req, str): # É um vértice requerido
                        target_node_for_path = service_req
                        
                        if current_demand + service_demand <= self.capacidade:
                            if target_node_for_path in distances and distances[target_node_for_path] < min_cost_to_next_service_segment:
                                min_cost_to_next_service_segment = distances[target_node_for_path]
                                path_to_next_service_nodes = self._get_path(previous_nodes, current_node, target_node_for_path)
                                next_service_to_visit = service_req

                    elif isinstance(service_req, tuple) and len(service_req) == 2: # É um arco requerido (u, v)
                        u, v = service_req # service_req é a tupla (origem, destino)
                        
                        if current_demand + service_demand <= self.capacidade:
                            # Para atender um arco (u,v), precisamos chegar em 'u' e depois percorrer o arco para 'v'.
                            if u not in distances or distances[u] == math.inf: 
                                continue # 'u' não é alcançável

                            cost_to_u = distances[u]
                            arc_segment_cost = self._get_peso_aresta_arco(u, v)
                            
                            if arc_segment_cost == math.inf: # Arco não existe no grafo
                                continue
                            
                            total_cost_for_arc_service = cost_to_u + arc_segment_cost
                            
                            if total_cost_for_arc_service < min_cost_to_next_service_segment:
                                path_to_u = self._get_path(previous_nodes, current_node, u)
                                if path_to_u: # Se existe um caminho até 'u'
                                    min_cost_to_next_service_segment = total_cost_for_arc_service
                                    # O caminho inclui o arco (u,v) conectando u e v
                                    path_to_next_service_nodes = path_to_u + [v] 
                                    next_service_to_visit = service_req
                                    
                    elif isinstance(service_req, tuple) and len(service_req) == 3: # É uma aresta requerida (u, v, peso_ignorado)
                        # Assume que service_req original é (u, v, peso_da_aresta_no_grafo)
                        # e que a demanda é armazenada com a tupla (u,v) ordenada
                        u, v, _ = service_req 
                        canonical_edge = tuple(sorted((u, v)))
                        
                        if current_demand + service_demand <= self.capacidade:
                            edge_segment_cost = self._get_peso_aresta_arco(u, v)
                            
                            if edge_segment_cost == math.inf: # Aresta não existe
                                continue

                            # Opção 1: ir de current_node para u, depois u para v
                            if u in distances and distances[u] != math.inf:
                                cost_to_u = distances[u]
                                total_cost_u_v = cost_to_u + edge_segment_cost
                                if total_cost_u_v < min_cost_to_next_service_segment:
                                    path_to_u = self._get_path(previous_nodes, current_node, u)
                                    if path_to_u:
                                        min_cost_to_next_service_segment = total_cost_u_v
                                        path_to_next_service_nodes = path_to_u + [v] 
                                        next_service_to_visit = service_req
                                        
                            # Opção 2: ir de current_node para v, depois v para u (se for mais curto)
                            if v in distances and distances[v] != math.inf:
                                cost_to_v = distances[v]
                                total_cost_v_u = cost_to_v + edge_segment_cost
                                if total_cost_v_u < min_cost_to_next_service_segment:
                                    path_to_v = self._get_path(previous_nodes, current_node, v)
                                    if path_to_v:
                                        min_cost_to_next_service_segment = total_cost_v_u
                                        path_to_next_service_nodes = path_to_v + [u]
                                        next_service_to_visit = service_req
                                        

                if next_service_to_visit is None:
                    break # Nenhum serviço pode ser adicionado à rota atual, ou todos já foram atendidos

                # Adicionar o caminho e o serviço à rota
                # Evita duplicar o current_node se ele já for o primeiro elemento do path
                if path_to_next_service_nodes and path_to_next_service_nodes[0] == current_node:
                    current_route_path.extend(path_to_next_service_nodes[1:])
                else:
                    current_route_path.extend(path_to_next_service_nodes)
                
                current_demand += service_demand
                
                # Marcar o serviço como atendido
                if isinstance(next_service_to_visit, tuple) and len(next_service_to_visit) == 3: # Aresta
                    atendidos.add(tuple(sorted((next_service_to_visit[0], next_service_to_visit[1]))))
                elif isinstance(next_service_to_visit, tuple) and len(next_service_to_visit) == 2: # Arco
                    atendidos.add(next_service_to_visit)
                else: # Vértice
                    atendidos.add(next_service_to_visit)
                
                # O último nó visitado se torna o current_node para a próxima iteração
                current_node = current_route_path[-1] 
            
            # A rota deve retornar ao depósito se não estiver lá
            if current_node != self.depot:
                distances_to_depot, previous_nodes_to_depot = self._dijkstra(current_node)
                
                if self.depot not in distances_to_depot or distances_to_depot[self.depot] == math.inf:
                    # Se o depósito não é alcançável, pode ser um grafo desconectado
                    print(f"Aviso: Depósito '{self.depot}' não alcançável a partir de '{current_node}'. Rota pode estar incompleta.")
                else:
                    path_to_depot = self._get_path(previous_nodes_to_depot, current_node, self.depot)
                    
                    if path_to_depot and path_to_depot[0] == current_node:
                        current_route_path.extend(path_to_depot[1:])
                    else:
                        current_route_path.extend(path_to_depot)

            # Adiciona a rota construída e seu custo total à solução
            if len(current_route_path) > 1: # Adiciona a rota apenas se ela contém mais do que só o depósito
                self.rotas.append(current_route_path)
                self.custo_total += self.calcular_custo(current_route_path)

    def get_demanda(self, servico):
        """
        Retorna a demanda de um serviço (vértice, aresta ou arco).
        """
        if isinstance(servico, tuple) and len(servico) == 3: # Aresta requerida, ex: ('1', '2', 3)
            # Normaliza a aresta para a chave no dicionário de demanda (tupla ordenada)
            return self.demanda_servicos[tuple(sorted((servico[0], servico[1])))]
        elif isinstance(servico, tuple) and len(servico) == 2: # Arco requerido, ex: ('0', '2')
            return self.demanda_servicos[servico]
        else: # Vértice requerido, ex: '1'
            return self.demanda_servicos[servico]

    def calcular_custo(self, rota_path):
        """
        Calcula o custo de uma rota baseada na sequência de vértices percorridos (rota_path).
        Soma os pesos das arestas/arcos no caminho real.
        """
        cost = 0
        for i in range(len(rota_path) - 1):
            u, v = rota_path[i], rota_path[i+1]
            segment_cost = self._get_peso_aresta_arco(u, v)
            
            if segment_cost == math.inf:
                print(f"Erro: Segmento de rota ({u}, {v}) não encontrado no grafo. Custo inválido.")
                return float('inf') # Retornar infinito para indicar rota inválida
            
            cost += segment_cost
        return cost

    def salvar_solucao(self, nome_instancia):
        """
        Salva a solução no formato especificado: "sol-nome_instancia.dat".
        """
        # Remove a extensão original do nome da instância se ela existir (ex: .txt, .dat)
        base_nome_instancia = nome_instancia.split('.')[0] 
        nome_arquivo = f"sol-{base_nome_instancia}.dat"
        
        with open(nome_arquivo, "w") as f:
            f.write(f"Custo total: {self.custo_total}\n")
            for i, rota in enumerate(self.rotas):
                f.write(f"Rota {i+1}: {' '.join(rota)}\n")

    # Em solucao.py, dentro de salvar_solucao:
def salvar_solucao(self, nome_instancia):
    base_nome_instancia = nome_instancia.split('.')[0] 
    nome_arquivo = f"sol-{base_nome_instancia}.dat"

    # Adicione este print para ver o caminho final do arquivo dentro da função
    print(f"DEBUG: Salvando solução em (dentro de solucao.py): {nome_arquivo}")

    try:
        with open(nome_arquivo, "w") as f:
            f.write(f"Custo total: {self.custo_total}\n")
            print(f"DEBUG: Escrito Custo total: {self.custo_total}") # Verifique se esta linha aparece
            for i, rota in enumerate(self.rotas):
                f.write(f"Rota {i+1}: {' '.join(rota)}\n")
                print(f"DEBUG: Escrito Rota {i+1}") # Verifique se esta linha aparece para cada rota
        print(f"DEBUG: Arquivo {nome_arquivo} fechado com sucesso.") # Confirma que a escrita terminou
    except Exception as e:
        print(f"ERRO AO SALVAR ARQUIVO {nome_arquivo}: {e}") # Captura qualquer exceção durante a escrita            