import os
from grafo import Grafo
from solucao import SolucaoInicial  # Classe que implementa o algoritmo

# Diretório das instâncias
instancias_dir = "./instancias/"
saida_dir = "./solucoes/"

# Lista de arquivos .dat
instancias = [f for f in os.listdir(instancias_dir) if f.endswith(".dat")]


# Processar cada instância
for instancia in instancias:
    print(f"Processando instância: {instancia}")
    grafo = Grafo()
    grafo.ler_arquivo(os.path.join(instancias_dir, instancia))
    
    # Construir solução
    solucao = SolucaoInicial(grafo)
    solucao.construir_solucao()
    
    # Salvar a solução
    nome_saida = f"sol-{instancia}"
    solucao.salvar_solucao(os.path.join(saida_dir, nome_saida))
    print(f"Solução salva em: {nome_saida}")

    nome_completo_arquivo = os.path.join(saida_dir, nome_saida)
    print(f"DEBUG: Tentando salvar em: {nome_completo_arquivo}")
    solucao.salvar_solucao(nome_completo_arquivo)
    print(f"Solução salva em: {nome_saida}")