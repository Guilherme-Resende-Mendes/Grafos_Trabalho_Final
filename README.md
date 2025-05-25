# GCC218 - Trabalho final: Algoritmos em Grafos

## Descrição
Este projeto é uma implementação prática para resolver problemas de logística utilizando algoritmos em grafos. Ele calcula estatísticas, componentes conectados, e outras métricas de um grafo representando interseções e vias.

## Estrutura do Projeto
- **`grafo.py`**:
  - Contém a implementação da classe `Grafo`, responsável pela representação de grafos.
  - Inclui métodos para cálculo de estatísticas, componentes conectados e métricas importantes.
  
- **`solucao.py`**:
  - Implementa o algoritmo construtivo para a construção de soluções iniciais.
  - Gera rotas que atendem às demandas respeitando as restrições do problema.

- **`visualizacao.ipynb`**:
  - Notebook Jupyter usado para visualizar os resultados calculados, como estatísticas dos grafos e rotas geradas.

- **`testes/`**:
  - Pasta contendo arquivos de teste para verificar o funcionamento correto dos algoritmos.

- **`padrao_escrita.dat`**:
  - Arquivo que descreve o formato de saída esperado para as soluções geradas.

- **`.gitignore`**:
  - Configuração para ignorar arquivos grandes, como as instâncias `.dat` e as soluções geradas, que não foram incluídas no repositório devido a limitações do GitHub.

---

## Como Executar
1. Clone o repositório:
   ```bash
   git clone https://github.com/Guilherme-Resende-Mendes/GCC218_Trabalho_Final.git
2. Navegue até a pasta do projeto:
   ```bash
   cd GCC218_Trabalho_Final
3. Execute os testes:
   ```bash
   python teste.py
4. Visualizar calculo de estatısticas a respeito dos grafos:
   ```bash
   jupyter notebook
   ```
   No navegador, selecione o arquivo visualizacao.ipynb.

# Gerar Soluções para as Instâncias

## ⚙️ Etapas para Gerar as Soluções

### 📥 1. Verificação das Instâncias
Certifique-se de que os arquivos de instância com extensão `.dat` estejam presentes na pasta `instancias/`.

### 🧪 2. Execução do Script
Abra um terminal ou prompt de comando na raiz do projeto e execute o seguinte comando:

```bash
python solucao.py
```

Esse comando iniciará o processo de geração das soluções.

### 📁 3. Localização das Soluções
As soluções geradas serão automaticamente salvas na pasta `solucoes/`, seguindo o formato especificado em `padrao_escrita.dat`.

---

## 📄 Formato da Solução

Cada arquivo de solução gerado em `solucoes/` contém as seguintes informações:

### 📝 Resumo da Solução
- **Custo total da solução**: Valor total do custo associado à solução encontrada.
- **Número total de rotas**: Quantidade de rotas utilizadas.
- **Clocks (tempo de execução)**: Tempo total de execução do algoritmo e tempo necessário para encontrar a solução.

### 📊 Detalhamento das Rotas
Cada rota é detalhada em uma linha separada, com o seguinte formato:

```
índice_do_depósito dia_da_roteirização identificador_da_rota demanda_total_da_rota custo_total_da_rota total_de_visitas (X i,j,k) ...
```

#### 🔹 Elementos Especiais
- `(D 0,1,1)`: Indica a presença do veículo no depósito no início ou fim da rota.
- `(S id_serviço,extremidade_1,extremidade_2)`: Indica o atendimento de um serviço específico, com identificação e extremidades.

---

### 🤖 Automação de Testes
Um script foi desenvolvido para automatizar o processamento de todas as instâncias disponíveis, salvando os arquivos diretamente em `solucoes/`.

---

## 👨‍💻 Autores
- **Guilherme Resende Mendes**
- **João Marcos Leal De Oliveira Lopes Ferreira**



