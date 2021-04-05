import numpy as np
import pandas as pd
import ampligraph
from ampligraph.evaluation import train_test_split_no_unseen
from ampligraph.latent_features import TransE, DistMult, ComplEx
import tensorflow as tf
from ampligraph.evaluation import evaluate_performance
from ampligraph.evaluation import mr_score, mrr_score, hits_at_n_score
from ampligraph.datasets import load_from_csv

X = load_from_csv('.', 'data/graph_relations.csv', sep=',')

# we create a 10% test set split
X_train, X_test = train_test_split_no_unseen(X, test_size=int(X.shape[0]/10))

EmbeddingMethod = ComplEx

model = EmbeddingMethod(batches_count=100, 
                seed=0, 
                epochs=200, 
                k=250, 
                eta=5,
                optimizer='adam', 
                optimizer_params={'lr':1e-3},
                loss='multiclass_nll', 
                regularizer='LP', 
                regularizer_params={'p':3, 'lambda':1e-5}, 
                verbose=True)

positives_filter = X

tf.logging.set_verbosity(tf.logging.ERROR)

model.fit(X_train, early_stopping = False)

ranks = evaluate_performance(X_test, 
                             model=model, 
                             filter_triples=positives_filter,
                             use_default_protocol=True,
                             verbose=True)


mrr = mrr_score(ranks)
print("MRR: %.2f" % (mrr))

hits_10 = hits_at_n_score(ranks, n=10)
print("Hits@10: %.2f" % (hits_10))
hits_3 = hits_at_n_score(ranks, n=3)
print("Hits@3: %.2f" % (hits_3))
hits_1 = hits_at_n_score(ranks, n=1)
print("Hits@1: %.2f" % (hits_1))

