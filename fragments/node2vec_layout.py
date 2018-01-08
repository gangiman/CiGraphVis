import numpy as np
from gensim.models import Word2Vec
from sklearn.manifold import TSNE

def make_walk(v, l, adj_list):
    if l == 0:
        return [v]
    i = np.random.randint(len(adj_list[v]))
    suffix = make_walk(adj_list[v][i], l - 1, adj_list)
    return [v] + suffix


def node2vec_layout(adj_list, is_directed = True, num_walks = 50, walk_length = 10, perplexity = 35):
    # augment edges for directed graph (by looking at it as at undirected one)
    if is_directed:
        augmented_adj_list = {v:[] for v in adj_list}
        for v in adj_list:
            for u in adj_list[v]:
                augmented_adj_list[u].append(v)
        for v in augmented_adj_list:
            adj_list[v] = list(set(adj_list[v]) | set(augmented_adj_list[v]))
            
    # walks gneration
    walks = []
    np.random.seed(0)
    for walk_num in range(num_walks):
        for v in np.random.choice(list(adj_list.keys()), len(adj_list), replace=False):
            if len(adj_list[v]) > 0:
                walks.append(make_walk(v, walk_length, adj_list))
                
    model = Word2Vec(walks, size=50, window=5, min_count=0, sg=1, workers=1, iter=1)
    word_vectors = model.wv
    word_vectors_dict = {v:word_vectors[v] for v in adj_list if v in word_vectors}
    
    # put isolated nodes close to center of coordinates
    good_keys = list(filter(lambda v: v in word_vectors_dict, adj_list.keys()))
    np.random.seed(0)
    max_norm = np.max([np.linalg.norm(x) for x in word_vectors_dict.values()])
    margin_factor = 0.01
    for v in adj_list:
        if v not in word_vectors_dict:
            u1 = good_keys[np.random.randint(len(good_keys))]
            u2 = good_keys[np.random.randint(len(good_keys))]
            while u2 == u1: # resample in case they are the same
                u2 = good_keys[np.random.randint(len(good_keys))]
            word_vectors_dict[v] = (word_vectors_dict[u1] + word_vectors_dict[u2])
            word_vectors_dict[v] *= margin_factor * np.linalg.norm(word_vectors_dict[v])/max_norm
        else:
            word_vectors_dict[v] = word_vectors_dict[v]/np.linalg.norm(word_vectors_dict[v])

    # make embedding
    embedding = TSNE(n_components=2, perplexity=perplexity, learning_rate = 200, n_iter = 500)
    Y = np.array([word_vectors_dict[v] for v in adj_list])
    Y = embedding.fit_transform(Y)
    
    # collect layout
    layout_positions = {}
    for i, v in enumerate(adj_list.keys()):
        layout_positions[v] = Y[i]
        
    return layout_positions