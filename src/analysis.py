import networkx as nx
import matplotlib.pyplot as plt

def analyze_centrality(G, top_n=5):
    """
    Calcula a Centralidade de Grau para identificar 'hubs' (Países e Gêneros mais influentes).
    """
    print("\n--- Iniciando Análise de Centralidade ---")
    
    # Calcula o grau de todos os nós
    degree_dict = dict(G.degree())
    
    # Separa nós por tipo
    genre_nodes = [n for n, attr in G.nodes(data=True) if attr.get('type') == 'genre']
    country_nodes = [n for n, attr in G.nodes(data=True) if attr.get('type') == 'country']

    # Ordena para achar os top N
    top_genres = sorted([(n, degree_dict[n]) for n in genre_nodes], key=lambda x: x[1], reverse=True)[:top_n]
    top_countries = sorted([(n, degree_dict[n]) for n in country_nodes], key=lambda x: x[1], reverse=True)[:top_n]

    print(f"Top {top_n} Gêneros mais comuns:")
    for genre, count in top_genres:
        print(f"   - {genre}: {count} conexões")

    print(f"Top {top_n} Países produtores:")
    for country, count in top_countries:
        print(f"   - {country}: {count} conexões")
        
    return top_genres, top_countries

def plot_subgraph(G, central_node, filename="graph_viz.png"):
    """
    Gera uma imagem do subgrafo ao redor de um nó específico e salva em arquivo.
    Ideal para colocar no artigo.
    """
    if central_node not in G:
        print(f"Nó {central_node} não encontrado para plotagem.")
        return

    # Pega vizinhos imediatos e vizinhos dos vizinhos (profundidade 2 limitada)
    subset = [central_node] + list(G.neighbors(central_node))
    subgraph = G.subgraph(subset)
    
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(subgraph, seed=42)
    
    # Cores simples
    colors = ['#1f78b4' if G.nodes[n].get('type') == 'title' else '#33a02c' for n in subgraph]
    
    nx.draw(subgraph, pos, node_color=colors, with_labels=True, font_size=8, node_size=500, alpha=0.8)
    plt.title(f"Vizinhança de: {central_node}")
    plt.savefig(filename)
    print(f"Gráfico salvo como '{filename}'")
    plt.close()