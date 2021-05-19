### Final Project for DSCI 558 (Fall 2020)

Artist Recommendations based on an artist's touring data (Songkick), discography (MusicBrainz), general info (Wikipedia and MusicBrainz), popularity (Billboard Top 100 and 200) and award show performance (Wikipedia -- AMA, Grammys, Billboard).

Key Concepts: Knowledge Graphs (KG), KG Embeddings, Triplet Loss, Peaguses Summarization model, Scraping, Entity Linking

### Folder Structure:

* Rahul_Folder -- ipython notebooks for doing entity linking and analyzing artist review text. Includes python driver for generating summaries of text (`summary_driver.py`)
* schemas -- schema used for our KG
* scrapers -- some of the scrapers used to pull data (rest of scrapers can be found in `jerry` branch)
* training -- ipython notebooks used to create dataset for training of embeddings and then compressing of embeddings. 
    - base_embedding_driver.py -- creates initial artist embeddings using ComplEx method
    - EmbeddingDriver.py -- pushes similar artists together via a triplet loss, also compresses dimensionality of artist embeddings

### Authors

Rahul Khanna

Zerui Xie
