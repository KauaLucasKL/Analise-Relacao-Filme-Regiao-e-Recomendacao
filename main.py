import os
import math
import networkx as nx
import matplotlib.pyplot as plt


from src.data_loader import load_data
from src.graph_builder import (
    build_full_graph,
    build_country_genre_graph,
    build_region_country_genre_graph
)
from src.recommender import recommend_titles
from evaluation.evaluation_plots import generate_all_plots_extended

# Configurações
CSV_PATH = os.path.join('data', 'raw', 'netflix_titles.csv')

ESTADOS_UNIDOS = {"United States"}
EUROPA = {
    "United Kingdom", "France", "Germany", "Spain", "Italy",
    "Netherlands", "Sweden", "Norway", "Denmark", "Belgium"
}
AMERICA_LATINA = {
    "Brazil", "Mexico", "Argentina", "Colombia", "Chile", "Peru"
}



# Exportação para o gephi
def exportar_para_gephi(G, nome_arquivo):
    pasta = os.path.join('paper', 'gephi_files')
    os.makedirs(pasta, exist_ok=True)
    try:
        nx.write_gexf(G, os.path.join(pasta, nome_arquivo))
        print(f"✅ Exportado: {nome_arquivo}")
    except Exception as e:
        print(f"❌ Erro ao exportar {nome_arquivo}: {e}")



# Buca de títulos
def buscar_filme_proximo(termo, G):
    termo = termo.lower()
    return [
        d['label']
        for _, d in G.nodes(data=True)
        if d.get('type') == 'title'
        and termo in d.get('label', '').lower()
    ]



# Visualização local
def visualizar_grafo_recomendacao(G, filme_alvo, recomendacoes):
    print("\n--- Gerando Visualização (Espessura por Relevância) ---")
    
    titulos_recs = [r[0] for r in recomendacoes]
    nodes_to_draw = {filme_alvo}
    
    # Adiciona nós intermediários
    for rec in titulos_recs:
        nodes_to_draw.add(rec)
        common = list(nx.common_neighbors(G, filme_alvo, rec))
        nodes_to_draw.update(common)
        
    sub = G.subgraph(list(nodes_to_draw))
    
    # Layout
    pos = nx.spring_layout(sub, k=0.9, iterations=50, seed=42)
    plt.figure(figsize=(14, 10))
    
    # Cores
    color_map = []
    for node in sub:
        tipo = G.nodes[node].get('type')
        if node == filme_alvo: color_map.append('#ff0000') # Alvo
        elif node in titulos_recs: color_map.append('#3498db') # Rec
        elif tipo == 'person': color_map.append('#2ecc71') # Ator (Verde)
        elif tipo == 'genre': color_map.append('#f39c12') # Gênero (Laranja)
        elif tipo == 'country': color_map.append('#8e44ad') # País (Roxo)
        else: color_map.append('#95a5a6')
        
    nx.draw_networkx_nodes(sub, pos, node_color=color_map, node_size=1000, alpha=0.9)
    nx.draw_networkx_labels(sub, pos, font_size=8, font_weight='bold')
    
    # Arestas com espessura variável
    edges_list = list(sub.edges())
    widths = []
    
    for u, v in edges_list:
        tipo_u = G.nodes[u].get('type')
        # Se for link direto entre filmes (raríssimo), destaca muito
        if tipo_u == 'title' and G.nodes[v].get('type') == 'title':
            widths.append(8.0)
            continue

        target = v if tipo_u == 'title' else u
        tipo_target = G.nodes[target].get('type')
        degree = G.degree(target)
        
        # Regra de espessura visual:
        if tipo_target == 'person':
            w = 6.0  # Atores = Muito grosso
        elif tipo_target == 'genre':
            if degree < 100: w = 4.0 # Nicho = Grosso
            else: w = 2.0 # Genérico = Médio
        elif tipo_target == 'country':
            w = 0.3  # País = Muito fino
        else:
            w = 1.0
            
        widths.append(w)
    
    nx.draw_networkx_edges(sub, pos, edgelist=edges_list, width=widths, alpha=0.6, edge_color='#555555')
    
    plt.title(f"Grafo de Decisão: {filme_alvo}\n(Linhas Grossas = Atores/Nichos | Linhas Finas = Países/Genéricos)")
    plt.axis('off')
    plt.tight_layout()
    plt.show()


# Função principal

def main():
    print("=== NETFLIX ANALYTICS TOOL ===")

    try:
        df = load_data(CSV_PATH)
    except:
        print("❌ Erro ao carregar o CSV.")
        return


    # Construção dos grafos

    print("\nConstruindo grafos...")

    # Grafo completo
    G_full = build_full_graph(df)

    # Grafo global País × Gênero
    G_country_genre = build_country_genre_graph(df)

    # Grafos regionais
    G_eua = build_region_country_genre_graph(df, ESTADOS_UNIDOS)
    G_europa = build_region_country_genre_graph(df, EUROPA)
    G_latam = build_region_country_genre_graph(df, AMERICA_LATINA)


    # Menu

    while True:
        print("\n" + "=" * 50)
        print("1. 🎬 Buscar Filme e Recomendar")
        print("2. 🌍 Exportar Grafos para Gephi")
        print("3. 📊 Gerar Gráficos Estatísticos")
        print("0. Sair")

        opt = input(">> ")

        if opt == '0':
            break

        elif opt == '1':
            termo = input("Nome do filme: ")
            cands = buscar_filme_proximo(termo, G_full)

            if cands:
                filme = cands[0]
                print(f"\nAnalisando: {filme}")

                recs = recommend_titles(filme, G_full)
                for r, s in recs:
                    print(f"  • {r} (Score: {s:.2f})")

                visualizar_grafo_recomendacao(G_full, filme, recs)
            else:
                print("❌ Filme não encontrado.")

        elif opt == '2':
            exportar_para_gephi(G_full, "recomendacao.gexf")
            exportar_para_gephi(G_country_genre, "pais_genero_global.gexf")
            exportar_para_gephi(G_eua, "genero_estados_unidos.gexf")
            exportar_para_gephi(G_europa, "genero_europa.gexf")
            exportar_para_gephi(G_latam, "genero_america_latina.gexf")

        elif opt == '3':
            region_graphs = {
                "Europa": G_europa,
                "America_Latina": G_latam,
                "Estados_Unidos": G_eua
            }

            generate_all_plots_extended(
                G_country_genre=G_country_genre,
                G_full=G_full,
                recommender_fn=recommend_titles,
                region_graphs=region_graphs
            )

            print("✅ Gráficos gerados com sucesso!")

        else:
            print("❌ Opção inválida.")



if __name__ == "__main__":
    main()
