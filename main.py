import requests
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return "Thanks for using"


@app.get("/items/num_4")
def num_4(label: str):
    query = """PREFIX fo: <http://www.w3.org/1999/XSL/Format#>
        PREFIX my: <http://www.mobile.com/model/>
        PREFIX sc: <http://purl.org/science/owl/sciencecommons/>
        prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        prefix xsd: <http://www.w3.org/2001/XMLSchema#>
        prefix foaf: <http://xmlns.com/foaf/spec/>
        prefix schema: <http://schema.org/>
        prefix dbo: <http://dbpedia.org/ontology/>
        prefix my_ns: <http://dsci558.org/rahul-zerui-project/>

        SELECT ?subject ?name
        WHERE {

          ?subject a my_ns:MusicalEntity;
                   schema:name ?name ;
                   dbo:recordLabel [schema:name '""" + label + """' ] .
        }
        LIMIT 100"""

    response = requests.post('http://localhost:3030/558proj/sparql',
                             data={'query': query})
    data_return = response.json()
    data_list = data_return['results']['bindings']

    result = []
    for item in data_list:
        uri = item['subject']['value']
        name = item['name']['value']
        result.append({'uri': uri, 'name': name}.copy())
    return result


@app.get("/items/num_5")
def num_5(artist_name: str):
    query = """PREFIX fo: <http://www.w3.org/1999/XSL/Format#>
PREFIX my: <http://www.mobile.com/model/>
PREFIX sc: <http://purl.org/science/owl/sciencecommons/>

prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix xsd: <http://www.w3.org/2001/XMLSchema#>
prefix foaf: <http://xmlns.com/foaf/spec/>
prefix schema: <http://schema.org/>
prefix dbo: <http://dbpedia.org/ontology/>
prefix my_ns: <http://dsci558.org/rahul-zerui-project/>

SELECT ?subject ?zscore ?adj_name
WHERE {

  ?subject a my_ns:AggregateLiveReview ;
           my_ns:sentimentZScore ?zscore ;
           my_ns:musicalEntity [ schema:name '""" + artist_name + """' ] ;
  		   my_ns:topAdjective [ schema:name ?adj_name; dbo:rank ?rank ] .
  FILTER( ?rank <= '9' )

}
LIMIT 10"""
    response = requests.post('http://localhost:3030/558proj/sparql',
                             data={'query': query})
    data_return = response.json()
    data_list = data_return['results']['bindings']
    result = {}
    i = 0
    for item in data_list:
        uri = item['subject']['value']
        zscore = item['zscore']['value']
        adj_name = item['adj_name']['value']
        if "uri" and "zscore" not in result:
            result = {'uri': uri, 'zscore': zscore}.copy()

        adj_name_key = 'adjectives_' + str(i)
        result[adj_name_key] = adj_name
        i += 1
    return result


@app.get("/items/num_6")
def num_6(city: str, genre: str):
    query = """PREFIX fo: <http://www.w3.org/1999/XSL/Format#>
PREFIX my: <http://www.mobile.com/model/>
PREFIX sc: <http://purl.org/science/owl/sciencecommons/>

prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix xsd: <http://www.w3.org/2001/XMLSchema#>
prefix foaf: <http://xmlns.com/foaf/spec/>
prefix schema: <http://schema.org/>
prefix dbo: <http://dbpedia.org/ontology/>
prefix my_ns: <http://dsci558.org/rahul-zerui-project/>

SELECT ?subject ?zscore ?name
WHERE {

  ?subject a my_ns:AggregateLiveReview ;
           my_ns:sentimentZScore ?zscore ;
           my_ns:musicalEntity ?ME .

  ?ME schema:name ?name ;
      my_ns:playsOftenIn [ schema:name '""" + city + """'];
      dbo:genre [schema:name '""" + genre + """'].
}
Order by ?zscore
LIMIT 100"""

    response = requests.post('http://localhost:3030/558proj/sparql',
                             data={'query': query})
    data_return = response.json()
    data_list = data_return['results']['bindings']

    result = []
    for item in data_list:
        uri = item['subject']['value']
        name = item['name']['value']
        zscore = item['zscore']['value']
        result.append({'uri': uri, 'name': name, 'zscore': zscore}.copy())
    return result


@app.get("/items/num_7")
def num_7(artist_name: str):
    query = """PREFIX fo: <http://www.w3.org/1999/XSL/Format#>
PREFIX my: <http://www.mobile.com/model/>
PREFIX sc: <http://purl.org/science/owl/sciencecommons/>

prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix xsd: <http://www.w3.org/2001/XMLSchema#>
prefix foaf: <http://xmlns.com/foaf/spec/>
prefix schema: <http://schema.org/>
prefix dbo: <http://dbpedia.org/ontology/>
prefix my_ns: <http://dsci558.org/rahul-zerui-project/>

SELECT ?subject ?rank ?gender ?is_band ?city ?start_year ?genre ?AMA_count ?wikiurl ?mb_id
WHERE {

  ?subject a my_ns:MusicalEntity;
  	  schema:name '""" + artist_name + """' ;
      my_ns:songKickRank ?rank;
      my_ns:playsOftenIn [ schema:name ?city];
      dbo:genre [schema:name ?genre] ;
  	  foaf:gender ?gender;
      schema:activeYearsStartYear ?start_year;
      my_ns:isBand ?is_band;
      my_ns:wikipediaUrl ?wikiurl;
  	  my_ns:musicBrainzId ?mb_id.
  {
    SELECT (count(?award) as ?AMA_count)
    WHERE{
    	?award a my_ns:MusicAward;
        schema:name 'American_Music_Award';
        my_ns:musicalEntity [schema:name '""" + artist_name + """'].
    }
  }

}"""

    response = requests.post('http://localhost:3030/558proj/sparql',
                             data={'query': query})
    data_return = response.json()
    data_list = data_return['results']['bindings']
    result = {}

    for item in data_list:
        uri = item['subject']['value']
        gender = item['gender']['value']
        rank = item['rank']['value']
        is_band = item['is_band']['value']
        start_year = item['start_year']['value']
        AMA_count = item['AMA_count']['value']
        wikiurl = item['wikiurl']['value']
        mb_id = item['mb_id']['value']
        genre = item['genre']['value']
        city = item['city']['value']
        if "uri" not in result:
            result = {'uri': uri, 'gender': gender, 'rank': rank, 'is_band': is_band, 'start_year': start_year,
                      'American_Music_Award_count': AMA_count, 'genre': [genre],
                      'Often_plays_in': [city], 'wikiurl': wikiurl, 'mb_id': mb_id}.copy()

        else:
            if city not in result['Often_plays_in']:
                result['Often_plays_in'].append(city)
            if genre not in result['genre']:
                result['genre'].append(genre)

    return result
