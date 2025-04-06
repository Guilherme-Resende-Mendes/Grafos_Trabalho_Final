from grafo import Grafo  # Importa a classe do outro arquivo

# Código de teste
print("Testando a classe Grafo...")
grafo = Grafo()
grafo.ler_arquivo('exemplo.txt')

estatisticas = grafo.estatisticas()
print("\nEstatísticas do grafo:")
for chave, valor in estatisticas.items():
    print(f"{chave}: {valor}")

print("\nComponentes conectados:", grafo.componentes_conectados())
print("\nBetweenness centrality:", grafo.calcular_intermediacao())