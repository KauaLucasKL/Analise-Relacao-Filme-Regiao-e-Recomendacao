import math
import networkx as nx
from collections import defaultdict
from difflib import SequenceMatcher


# Configuração de pesos para as fórmulas

WEIGHT_PERSON = 0.7    
WEIGHT_GENRE = 0.4     # Gêneros são importantes
WEIGHT_COUNTRY = 0.05  # País influencia muito pouco

# Pesos de mistura das métricas finais
ALPHA_ADAMIC = 0.4     # Peso da Raridade das conexões
BETA_JACCARD = 0.4     # Peso da Sobreposição de atributos
GAMMA_TEXT = 0.2       # Peso do Nome (Bônus de Franquia)

def get_text_similarity(a, b):
    """
    Calcula a similaridade de string (0.0 a 1.0).
    """
    if not a or not b: return 0.0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def compute_weighted_jaccard(G, node_a, node_b):
    """
    J(A,B) = (Peso da Interseção) / (Peso da União)
    Retorna 0.0 a 1.0.
    """
    neighbors_a = set(G.neighbors(node_a))
    neighbors_b = set(G.neighbors(node_b))
    
    intersection = neighbors_a & neighbors_b
    union = neighbors_a | neighbors_b
    
    if not union: return 0.0
    
    numerator = 0.0
    denominator = 0.0
    
    def get_node_weight(n):
        tipo = G.nodes[n].get("type")
        if tipo == "person": return WEIGHT_PERSON
        if tipo == "genre": return WEIGHT_GENRE
        if tipo == "country": return WEIGHT_COUNTRY
        return 0.1

    for n in intersection:
        numerator += get_node_weight(n)
        
    for n in union:
        denominator += get_node_weight(n)
        
    if denominator == 0: return 0.0
    return numerator / denominator

def compute_adamic_adar(G, node_a, node_b):
    """
    Score baseado na raridade dos vizinhos em comum.
    """
    common_neighbors = list(nx.common_neighbors(G, node_a, node_b))
    score = 0.0
    
    for neighbor in common_neighbors:
        degree = G.degree(neighbor)
        tipo = G.nodes[neighbor].get("type")
        
        if degree <= 1: continue
            
        weight_factor = 1.0
        if tipo == "person": weight_factor = 5.0
        elif tipo == "country": weight_factor = 0.1
        
        score += weight_factor * (1.0 / math.log(degree))
        
    return score

def recommend_titles(title_label, G, top_n=5):
    # 1. Localizar nó de origem
    title_node = None
    for n, d in G.nodes(data=True):
        if d.get("type") == "title" and d.get("label") == title_label:
            title_node = n
            break

    if title_node is None:
        return []

    final_scores = defaultdict(float)
    
    # 2. Identificar Candidatos
    candidate_set = set()
    source_neighbors = list(G.neighbors(title_node))
    
    for neighbor in source_neighbors:
        for candidate in G.neighbors(neighbor):
            if candidate != title_node and G.nodes[candidate].get("type") == "title":
                candidate_set.add(candidate)
    
    # 3. Calcular Métricas
    for candidate in candidate_set:
        candidate_label = G.nodes[candidate]["label"]
        
        # A. Adamic-Adar (Estrutura Topológica)
        aa_score = compute_adamic_adar(G, title_node, candidate)
        
        # B. Weighted Jaccard (Similaridade de Conteúdo)
        jac_score = compute_weighted_jaccard(G, title_node, candidate)
        
        # C. Text Similarity (Semântica/Nome)
        text_score = get_text_similarity(title_label, candidate_label)
        
        threshold_estrutural = 1.0  # Mínimo de 100% de sobreposição ponderada
        
        if jac_score < threshold_estrutural:
            # Se a estrutura não bate, ignora a semelhança de nome (evita falsos positivos)
            text_score = 0.0
        else:
            # Se passou na trava estrutural, aplica o boost de franquia se merecer
            if text_score > 0.6:
                text_score *= 8.0 
        
        # 4. Fórmula Final
        final_score = (aa_score * ALPHA_ADAMIC) + \
                      (jac_score * 10.0 * BETA_JACCARD) + \
                      (text_score * 5.0 * GAMMA_TEXT)
                      
        final_scores[candidate] = final_score

    # 5. Ordenação
    ranking = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
    
    return [(G.nodes[n]["label"], round(score, 4)) for n, score in ranking[:top_n]]