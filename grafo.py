import math
from collections import defaultdict

class Grafo:
    def __init__(self):
        self.vertices = set()          # Conjunto de vértices
        self.arestas = []              # Lista de arestas (não direcionadas)
        self.arcos = []               # Lista de arcos (direcionados)
        self.VR = set()               # Vértices requeridos
        self.ER = []                  # Arestas requeridas
        self.AR = []                  # Arcos requeridos
        self.depot = None             # Vértice depósito
        self.capacidade = None       # Capacidade do veículo
        self._vizinhos = defaultdict(list)  # Estrutura auxiliar para vizinhos

    def adicionar_vertice(self, v):
        self.vertices.add(v)

    def adicionar_aresta(self, u, v, peso=1):
        self.arestas.append((u, v, peso))
        self._vizinhos[u].append((v, peso))
        self._vizinhos[v].append((u, peso))

    def adicionar_arco(self, u, v, peso=1):
        self.arcos.append((u, v, peso))
        self._vizinhos[u].append((v, peso))

    def adicionar_vertice_requerido(self, v):
        self.VR.add(v)

    def adicionar_aresta_requerida(self, u, v, peso=1):
        self.ER.append((u, v, peso))

    def adicionar_arco_requerido(self, u, v, peso=1):
        self.AR.append((u, v, peso))

    def definir_deposito(self, v):
        self.depot = v

    def definir_capacidade(self, capacidade):
        self.capacidade = capacidade

    def estatisticas(self):
        stats = {
            "qtd_vertices": len(self.vertices),
            "qtd_arestas": len(self.arestas),
            "qtd_arcos": len(self.arcos),
            "qtd_vr": len(self.VR),
            "qtd_er": len(self.ER),
            "qtd_ar": len(self.AR),
            "depot": self.depot,
            "capacidade": self.capacidade,
        }
        
        # Calcula densidade
        qtd_total_arestas = stats["qtd_arestas"] + stats["qtd_arcos"]
        n = stats["qtd_vertices"]
        stats["densidade"] = (2 * qtd_total_arestas) / (n * (n - 1)) if n > 1 else 0
        
        # Componentes conectados
        stats["componentes"] = len(self.componentes_conectados())
        
        # Grau mínimo e máximo
        grau_min, grau_max = self.grau_min_max()
        stats["grau_min"] = grau_min
        stats["grau_max"] = grau_max
        
        # Caminho médio e diâmetro
        distancias, _ = self.matriz_caminhos_mais_curto()  # Agora pegamos apenas distancias
        soma_distancias = 0
        qtd_caminhos = 0
        maior_distancia = 0
    
        for i in range(len(distancias)):
            for j in range(len(distancias)):
                if i != j and distancias[i][j] != math.inf:
                    soma_distancias += distancias[i][j]
                    qtd_caminhos += 1
                    if distancias[i][j] > maior_distancia:
                        maior_distancia = distancias[i][j]
        
        stats["caminho_medio"] = soma_distancias / qtd_caminhos if qtd_caminhos > 0 else 0
        stats["diametro"] = maior_distancia
        
        return stats

    def componentes_conectados(self):
        visitados = set()
        componentes = []

        def dfs(v, componente):
            stack = [v]
            while stack:
                node = stack.pop()
                if node not in visitados:
                    visitados.add(node)
                    componente.append(node)
                    for (vizinho, _) in self._vizinhos[node]:
                        if vizinho not in visitados:
                            stack.append(vizinho)

        for v in self.vertices:
            if v not in visitados:
                componente = []
                dfs(v, componente)
                componentes.append(componente)

        return componentes

    def grau_vertices(self):
        graus = {v: 0 for v in self.vertices}
        for u, v, _ in self.arestas:
            graus[u] += 1
            graus[v] += 1
        for u, v, _ in self.arcos:
            graus[u] += 1
        return graus

    def grau_min_max(self):
        graus = self.grau_vertices()
        return min(graus.values()), max(graus.values())

    def matriz_caminhos_mais_curto(self):
        n = len(self.vertices)
        vertices_list = sorted(self.vertices)
        index = {v: i for i, v in enumerate(vertices_list)}
        dist = [[math.inf] * n for _ in range(n)]
        pred = [[None] * n for _ in range(n)]

        for i in range(n):
            dist[i][i] = 0

        for u, v, peso in self.arestas:
            i, j = index[u], index[v]
            dist[i][j] = peso
            dist[j][i] = peso
            pred[i][j] = u
            pred[j][i] = v

        for u, v, peso in self.arcos:
            i, j = index[u], index[v]
            dist[i][j] = peso
            pred[i][j] = u

        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if dist[i][k] + dist[k][j] < dist[i][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
                        pred[i][j] = pred[k][j]

        return dist, pred  # Agora retorna ambos

    def calcular_intermediacao(self):
        n = len(self.vertices)
        vertices_list = sorted(self.vertices)
        index = {v: i for i, v in enumerate(vertices_list)}
        betweenness = {v: 0 for v in self.vertices}
        
        # Agora recebemos ambos dist e pred da matriz_caminhos_mais_curto
        dist, pred = self.matriz_caminhos_mais_curto()

        for s in range(n):
            for t in range(n):
                if s != t and dist[s][t] != math.inf:
                    current = t
                    path = []
                    while current != s and current is not None:
                        path.append(vertices_list[current])
                        current = index.get(pred[s][current], None)
                    if current == s:
                        path.append(vertices_list[s])
                        for node in path[1:-1]:  # Exclui os nós de origem e destino
                            betweenness[node] += 1

        return betweenness

    def ler_arquivo(self, caminho_arquivo):
        with open(caminho_arquivo, 'r') as f:
            secao_atual = None
            
            for linha in f:
                linha = linha.strip()
                if not linha or linha.startswith('#'):
                    continue
                
                if linha.startswith('VERTICES'):
                    secao_atual = 'VERTICES'
                elif linha.startswith('EDGES'):
                    secao_atual = 'EDGES'
                elif linha.startswith('ARCS'):
                    secao_atual = 'ARCS'
                elif linha.startswith('REQUIRED_VERTICES'):
                    secao_atual = 'REQUIRED_VERTICES'
                elif linha.startswith('REQUIRED_EDGES'):
                    secao_atual = 'REQUIRED_EDGES'
                elif linha.startswith('REQUIRED_ARCS'):
                    secao_atual = 'REQUIRED_ARCS'
                elif linha.startswith('DEPOT'):
                    secao_atual = 'DEPOT'
                elif linha.startswith('CAPACITY'):
                    secao_atual = 'CAPACITY'
                else:
                    itens = linha.split()
                    if secao_atual == 'VERTICES':
                        for v in itens:
                            self.adicionar_vertice(v)
                    elif secao_atual == 'EDGES':
                        u, v, peso = itens[0], itens[1], float(itens[2])
                        self.adicionar_aresta(u, v, peso)
                    elif secao_atual == 'ARCS':
                        u, v, peso = itens[0], itens[1], float(itens[2])
                        self.adicionar_arco(u, v, peso)
                    elif secao_atual == 'REQUIRED_VERTICES':
                        for v in itens:
                            self.adicionar_vertice_requerido(v)
                    elif secao_atual == 'REQUIRED_EDGES':
                        u, v = itens[0], itens[1]
                        peso = float(itens[2]) if len(itens) > 2 else 1
                        self.adicionar_aresta_requerida(u, v, peso)
                    elif secao_atual == 'REQUIRED_ARCS':
                        u, v = itens[0], itens[1]
                        peso = float(itens[2]) if len(itens) > 2 else 1
                        self.adicionar_arco_requerido(u, v, peso)
                    elif secao_atual == 'DEPOT':
                        self.definir_deposito(itens[0])
                    elif secao_atual == 'CAPACITY':
                        self.definir_capacidade(float(itens[0]))