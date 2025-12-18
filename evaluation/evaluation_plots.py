import os
import matplotlib.pyplot as plt
import networkx as nx
from collections import Counter
import numpy as np

IMAGES_DIR = os.path.join("paper", "images")
os.makedirs(IMAGES_DIR, exist_ok=True)


# 1. Distribuição de grau
def plot_degree_distribution(G):
    degrees = [d for _, d in G.degree() if d > 0]

    plt.figure(figsize=(8, 6))
    plt.hist(degrees, bins=20, edgecolor="black")
    plt.yscale("log")
    plt.xlabel("Grau do nó")
    plt.ylabel("Frequência (escala log)")
    plt.title("Distribuição de Grau da Rede País–Gênero")
    plt.grid(alpha=0.3)
    plt.tight_layout()

    path = os.path.join(IMAGES_DIR, "distribuicao_grau.png")
    plt.savefig(path, dpi=300)
    plt.close()








# 2. Centralidade de gêneros
def plot_centralidade_generos(G, top_n=10):
    from collections import defaultdict

    genre_strength = defaultdict(float)

    for u, v, d in G.edges(data=True):
        weight = d.get("weight", 1)
        if G.nodes[u]["type"] == "genre":
            genre_strength[u] += weight
        elif G.nodes[v]["type"] == "genre":
            genre_strength[v] += weight

    genres = sorted(
        genre_strength.items(),
        key=lambda x: x[1],
        reverse=True
    )[:top_n]

    labels, values = zip(*genres)

    plt.figure(figsize=(10, 6))
    plt.barh(labels, values, color="#DD8452")
    plt.xlabel("Frequência ponderada (nº de títulos)")
    plt.title("Centralidade de Gêneros (ponderada)")
    plt.gca().invert_yaxis()
    plt.grid(axis="x", alpha=0.3)
    plt.tight_layout()

    path = os.path.join(IMAGES_DIR, "centralidade_generos.png")
    plt.savefig(path, dpi=300)
    plt.close()




# 3. Distribuição de gêneros por região

def plot_genero_regiao(G, regiao_nome):
    genre_weights = Counter()

    for u, v, d in G.edges(data=True):
        if G.nodes[u]["type"] == "genre":
            genre_weights[u] += d.get("weight", 1)
        elif G.nodes[v]["type"] == "genre":
            genre_weights[v] += d.get("weight", 1)

    genres, values = zip(*genre_weights.most_common(10))

    plt.figure(figsize=(10, 6))
    plt.barh(genres, values, color="#55A868")
    plt.xlabel("Frequência")
    plt.title(f"Gêneros mais representados – {regiao_nome}")
    plt.gca().invert_yaxis()
    plt.grid(axis="x", alpha=0.3)
    plt.tight_layout()

    path = os.path.join(IMAGES_DIR, f"genero_{regiao_nome.lower()}.png")
    plt.savefig(path, dpi=300)
    plt.close()



# 4. Comparação estrutural entre regiões

def plot_comparacao_regioes(region_graphs):
    nomes = []
    nos = []
    arestas = []

    for nome, G in region_graphs.items():
        nomes.append(nome)
        nos.append(G.number_of_nodes())
        arestas.append(G.number_of_edges())

    x = np.arange(len(nomes))

    plt.figure(figsize=(10, 6))
    plt.bar(x - 0.2, nos, 0.4, label="Nós")
    plt.bar(x + 0.2, arestas, 0.4, label="Arestas")
    plt.xticks(x, nomes)
    plt.ylabel("Quantidade")
    plt.title("Comparação Estrutural entre Regiões")
    plt.legend()
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    path = os.path.join(IMAGES_DIR, "comparacao_regioes.png")
    plt.savefig(path, dpi=300)
    plt.close()


# 5. Avaliação do sistema de recomendação 
def plot_avaliacao_recomendacao(G_full, recommender_fn, sample_size=100):
    titles = [
        n for n, d in G_full.nodes(data=True)
        if d.get("type") == "title"
    ][:sample_size]

    scores = []

    for title in titles:
        recs = recommender_fn(G_full.nodes[title]["label"], G_full)
        scores.append(len(recs))

    plt.figure(figsize=(8, 6))
    plt.hist(scores, bins=10, edgecolor="black")
    plt.xlabel("Número de recomendações")
    plt.ylabel("Frequência")
    plt.title("Avaliação do Sistema de Recomendação")
    plt.grid(alpha=0.3)
    plt.tight_layout()

    path = os.path.join(IMAGES_DIR, "avaliacao_recomendacao.png")
    plt.savefig(path, dpi=300)
    plt.close()


# Função principal
def generate_all_plots_extended(
    G_country_genre,
    G_full,
    recommender_fn,
    region_graphs
):
    print("\n=== Gerando gráficos do projeto ===")

    plot_degree_distribution(G_country_genre)
    plot_centralidade_generos(G_country_genre)

    for nome, G in region_graphs.items():
        plot_genero_regiao(G, nome)

    plot_comparacao_regioes(region_graphs)
    plot_avaliacao_recomendacao(G_full, recommender_fn)

    print("=== Todos os gráficos foram gerados com sucesso ===")
