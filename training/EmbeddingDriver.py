import torch
from transformers import AdamW
import sys
sys.path.append(".")
from utils import build_data_loader, evaluate_model
from GraphEmbeddingEncoder import GraphEmbeddingEncoder
import pickle
from tqdm import tqdm
import torch.nn as nn
import numpy as np
import argparse
import csv
import pickle

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_batch_size",
                        default=128,
                        type=int,
                        help="Total batch size for train.")
    parser.add_argument("--eval_batch_size",
                        default=128,
                        type=int,
                        help="Total batch size for eval.")
    parser.add_argument("--learning_rate",
                        default=1e-5,
                        type=float,
                        help="The initial learning rate for Adam.")
    parser.add_argument("--epochs",
                        default=10,
                        type=int,
                        help="Number of Epochs for training")
    parser.add_argument('--seed',
                        type=int,
                        default=42,
                        help="random seed for initialization")
    parser.add_argument('--model_save_dir',
                        type=str,
                        default="",
                        help="where to save the model")
    parser.add_argument('--embedding_dim',
                        type=int,
                        default=500,
                        help="initial embedding dim")
    parser.add_argument('--compressed_dim',
                        type=int,
                        default=400,
                        help="compressed embedding dim")
    parser.add_argument('--final_dim',
                        type=int,
                        default=100,
                        help="final embedding dim")
    parser.add_argument("--experiment_name",
                        type=str)
    parser.add_argument("--embedding_pct", type=float, default=0.2)


    args = parser.parse_args()

    torch.manual_seed(args.seed)


    train_dataloader = build_data_loader("data/og_train.p", batch_size=args.train_batch_size)

    if torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")

    with open("data/embeddings.p", "rb") as f:
        embeddings = pickle.load(f)
    
    embeddings = torch.tensor(embeddings)

    model = GraphEmbeddingEncoder(embeddings, args.embedding_dim, args.compressed_dim, args.final_dim, args.embedding_pct)
    model = model.to(device)

    # define the optimizer
    optimizer = AdamW(model.parameters(), lr=args.learning_rate)   

    loss_function  = nn.TripletMarginLoss(margin=1.0, p=2)

    # number of training epochs
    epochs = args.epochs

    epoch_losses = []
    best_eval_loss = float('inf') 

    for epoch in range(epochs):
        print('\n Epoch {:} / {:}'.format(epoch + 1, epochs))

        total_loss, total_accuracy = 0, 0
        model.train()

        # iterate over batches
        for step, batch in enumerate(tqdm(train_dataloader)):
            # push the batch to gpu
            batch = [r.to(device) for r in batch]

            a_ids, p_ids, n_ids = batch

            # clear previously calculated gradients 
            model.zero_grad()        

            # get model predictions for the current batch
            anchor_vectors = model(a_ids)
            positive_vectors = model(p_ids)
            negative_vectors = model(n_ids)

            # compute the loss between actual and predicted values
            loss = loss_function(anchor_vectors, positive_vectors, negative_vectors)

            # add on to the total loss
            total_loss = total_loss + loss.item()

            # backward pass to calculate the gradients
            loss.backward()

            # clip the the gradients to 1.0. It helps in preventing the exploding gradient problem
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)

            # update parameters
            optimizer.step()

        # compute the training loss of the epoch
        train_avg_loss = total_loss / len(train_dataloader)

        print("Starting Evaluation")
        dev_avg_loss = evaluate_model("data/og_dev.p", model, loss_function)
        print("Finished Evaluation")
        
        if dev_avg_loss < best_eval_loss:
            print("Saving Model")
            if len(args.model_save_dir) > 0:
                dir_name = args.model_save_dir
            else:
                dir_name = "saved_models/"
            torch.save(model.state_dict(), '{}EmbeddingEncoder-ft_{}.pt'.format(dir_name, args.experiment_name))
            best_eval_loss = dev_avg_loss

        epoch_losses.append((train_avg_loss, dev_avg_loss))

        print(epoch_losses)

    epoch_string = str(epochs)
    with open("data/result_data/loss_per_epoch_{}_{}.csv".format(args.experiment_name, epoch_string), "w") as f:
        writer=csv.writer(f)
        writer.writerow(['train_loss','eval_loss'])
        for row in epoch_losses:
            writer.writerow(row)

if __name__ == "__main__":
    main()
