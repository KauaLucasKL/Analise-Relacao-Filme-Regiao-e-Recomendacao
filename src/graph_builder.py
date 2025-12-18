import networkx as nx
from itertools import product
from collections import Counter

# =====================================================
# GRAFO COMPLETO (FILMES) → RECOMENDAÇÃO
# =====================================================
def build_full_graph(df):
    G = nx.Graph()

    for _, row in df.iterrows():
        title = row['title'].strip()
        countries = [c.strip() for c in row['country'].split(',') if c.strip()]
        genres = [g.strip() for g in row['listed_in'].split(',') if g.strip()]

        G.add_node(title, type='title', label=title)

        for country in countries:
            G.add_node(country, type='country', label=country)
            G.add_edge(title, country, relation='produced_in')

        for genre in genres:
            G.add_node(genre, type='genre', label=genre)
            G.add_edge(title, genre, relation='is_genre')

    print(f"Grafo completo: {G.number_of_nodes()} nós, {G.number_of_edges()} arestas.")
    return G


# =====================================================
# GRAFO PAÍS × GÊNERO (GLOBAL)
# =====================================================
def build_country_genre_graph(df, min_edge_weight=5, top_countries=15, top_genres=15):
    edge_counter = Counter()

    for _, row in df.iterrows():
        countries = [c.strip() for c in row['country'].split(',') if c.strip()]
        genres = [g.strip() for g in row['listed_in'].split(',') if g.strip()]

        for country, genre in product(countries, genres):
            edge_counter[(country, genre)] += 1

    country_count = Counter(c for c, _ in edge_counter)
    genre_count = Counter(g for _, g in edge_counter)

    top_countries_set = set(c for c, _ in country_count.most_common(top_countries))
    top_genres_set = set(g for g, _ in genre_count.most_common(top_genres))

    G = nx.Graph()
    max_weight = max(edge_counter.values())

    for (country, genre), weight in edge_counter.items():
        if (
            country in top_countries_set and
            genre in top_genres_set and
            weight >= min_edge_weight
        ):
            G.add_node(country, type='country', label=country)
            G.add_node(genre, type='genre', label=genre)
            G.add_edge(country, genre, weight=weight / max_weight)

    print(f"Grafo País–Gênero Global: {G.number_of_nodes()} nós, {G.number_of_edges()} arestas.")
    return G


# =====================================================
# GRAFO PAÍS × GÊNERO POR REGIÃO (INDEPENDENTE)
# =====================================================
def build_region_country_genre_graph(df, region_countries, min_edge_weight=3):
    edge_counter = Counter()

    for _, row in df.iterrows():
        countries = [c.strip() for c in row['country'].split(',') if c.strip()]
        genres = [g.strip() for g in row['listed_in'].split(',') if g.strip()]

        region_only = [c for c in countries if c in region_countries]

        for country, genre in product(region_only, genres):
            edge_counter[(country, genre)] += 1

    if not edge_counter:
        return nx.Graph()

    max_weight = max(edge_counter.values())
    G = nx.Graph()

    for (country, genre), weight in edge_counter.items():
        if weight >= min_edge_weight:
            G.add_node(country, type='country', label=country)
            G.add_node(genre, type='genre', label=genre)
            G.add_edge(country, genre, weight=weight / max_weight)

    print(f"Grafo Regional ({len(region_countries)} países): {G.number_of_nodes()} nós, {G.number_of_edges()} arestas.")
    return G
