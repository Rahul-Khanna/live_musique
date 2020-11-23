import torch
import torch.nn as nn

class GraphEmbeddingEncoder(nn.Module):
    def __init__(self, emb_weight, emb_dim=500, compressed_dim=400, final_dim=100, embedding_dropout_pct=0.2):
        self.embedding_dropout_pct = embedding_dropout_pct
        self.emb_dim = emb_dim
        self.compressed_dim = compressed_dim
        self.final_dim = final_dim

        self.embedding_dropout = nn.Dropout(p=self.embedding_dropout_pct)
        
        self.embeddings = nn.Embedding.from_pretrained(emb_weight, freeze=False)
        
        diagonal_vector = torch.zeros(self.emb_dim, 1)
        nn.init.xavier_uniform_(diagonal_vector)
        diagonal_vector = diagonal_vector.squeeze(1)
        self.feature_weight_matrix = nn.Parameter(torch.diag(input=diagonal_vector), requires_grad=True)
        
        self.compressing_projection = nn.Linear(self.emb_dim, self.compressed_dim)

        self.relu =  nn.ReLU()
      
        self.output_projection = nn.Linear(self.compressed_dim, self.final_dim)

    def forward(self, input_ids):
        """
            input_ids = N x 1
        """
        embeddings = self.embeddings(input_ids) # N x 1 x emb_dim
        embeddings = self.embedding_dropout(embeddings) # N x 1 x emb_dim

        updated_embeddings = self.feature_weight_matrix(embeddings) # N x 1 x emb_dim

        compressed_embeddings = self.compressing_projection(updated_embeddings) # N x 1 x compressed_dim

        non_linear_embeddings = self.relu(compressed_embeddings) # N x 1 x compressed_dim

        final_embeddings = self.output_projection(non_linear_embeddings).squeeze(1) # N x final_dim

        return final_embeddings
