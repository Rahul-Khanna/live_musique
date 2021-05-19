import pickle
import torch
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from tqdm import tqdm

def build_data_loader(path, batch_size, train=1):
    with open(path, "rb") as f:
        data_dict = pickle.load(f)
    # wrap tensors
    dataset = TensorDataset(data_dict["a_ids"], data_dict["p_ids"], data_dict["n_ids"])

    # sampler for sampling the data during training
    if train:
        sampler = RandomSampler(dataset)
    else:
        sampler = SequentialSampler(dataset)

    # dataLoader for train set
    dataloader = DataLoader(dataset, sampler=sampler, batch_size=batch_size)

    return dataloader

def evaluate_model(data_path, model, loss_function, batch_size=128):
    dataloader = build_data_loader(data_path, batch_size=batch_size, train=0)
    # deactivate dropout layers
    model.eval()
    
    if torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")
    
    total_loss = 0

    # iterate over batches
    for step, batch in enumerate(tqdm(dataloader)):

        # push the batch to gpu
        batch = [t.to(device) for t in batch]

        a_ids, p_ids, n_ids = batch

        # deactivate autograd
        with torch.no_grad():

            # model predictions
            anchor_vectors = model(a_ids)
            positive_vectors = model(p_ids)
            negative_vectors = model(n_ids)

            # compute the validation loss between actual and predicted values
            loss = loss_function(anchor_vectors, positive_vectors, negative_vectors)

            total_loss = total_loss + loss.item()

    # compute the validation loss of the epoch
    avg_loss = total_loss / len(dataloader) 

    return avg_loss
