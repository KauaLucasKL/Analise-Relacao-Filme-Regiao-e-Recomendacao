import networkx as nx
from collections import defaultdict

def project_country_genre(G):
    """
    Cria um grafo Country–Genre projetado a partir do grafo original.
    O peso da aresta representa o número de títulos compartilhados.
    """
    H = nx.Graph()

    # Mapeia filmes por país
    country_to_titles = defaultdict(set)
    genre_to_titles = defaultdict(set)

    for node, data in G.nodes(data=True):
        if data.get("type") == "country":
            for neighbor in G.neighbors(node):
                if G.nodes[neighbor].get("type") == "title":
                    country_to_titles[node].add(neighbor)

        elif data.get("type") == "genre":
            for neighbor in G.neighbors(node):
                if G.nodes[neighbor].get("type") == "title":
                    genre_to_titles[node].add(neighbor)

    # Cria projeção
    for country, titles_c in country_to_titles.items():
        H.add_node(country, type="country", label=country)

        for genre, titles_g in genre_to_titles.items():
            intersecao = titles_c & titles_g
            peso = len(intersecao)

            if peso > 0:
                H.add_node(genre, type="genre", label=genre)
                H.add_edge(country, genre, weight=peso)

    print(
        f"Projeção criada: {H.number_of_nodes()} nós, "
        f"{H.number_of_edges()} arestas"
    )

    return H
