import jsonlines
import tqdm
import pickle
from transformers import PegasusForConditionalGeneration, PegasusTokenizer
import torch

artist_reviews = {}
with jsonlines.open('../data_for_558_proj/songkick.jl') as reader:
    for obj in reader:
        if len(obj["reviews"]) > 0:
            text = " ".join(obj["reviews"])
            text = " ".join(text.split()).strip()
            artist_reviews[obj["url"]] = {"text" : text,
                                          "count" : len(obj["reviews"]),
                                          "name" : obj["name"]}

src_text = [artist_reviews[key]["text"] for key in artist_reviews]

batch_size = 32
model_name = 'google/pegasus-xsum'
torch_device = 'cuda' if torch.cuda.is_available() else 'cpu'
tokenizer = PegasusTokenizer.from_pretrained(model_name)
model = PegasusForConditionalGeneration.from_pretrained(model_name)

model.to(torch_device)

summary_text = []
for i in tqdm.tqdm(range(0, len(src_text), batch_size)):
    batch = src_text[i:i+batch_size]
    batch = tokenizer.prepare_seq2seq_batch(batch, truncation=True, padding='longest').to(torch_device)
    translated = model.generate(**batch)
    tgt_text = tokenizer.batch_decode(translated, skip_special_tokens=True)
    summary = summary + tgt_text

summary_dictionary = {}
for i, key in enumerate(artist_reviews):
    summary_dictionary[key] = {"summary" : summary_text[i]}


with open("nlp_data/summary.p", "wb") as f:
    pickle.dump(summary_dictionary, f)