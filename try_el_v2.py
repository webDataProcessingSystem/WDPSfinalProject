import spacy
from typing import Tuple, List
from titlecase import titlecase
from SPARQLWrapper import SPARQLWrapper, JSON
import time
import requests
from Levenshtein import distance as l_distance
import numpy as np

wiki_url = "https://en.wikipedia.org/w/api.php"
# Mapping of NER tag to SPARQL query group.
# spacy tag_list at: https://github.com/explosion/spaCy/blob/master/spacy/glossary.py  line329
rdf_type_dict = {
    "PERSON"        : "dbo:Person",
    #"NORP"          : "",
    #"FACILITY"      : "",
    "FAC"           : "geo:SpatialThing",
    "ORG"           : "dbo:Organisation",
    "GPE"           : "geo:SpatialThing",
    "LOC"           : "geo:SpatialThing",
    "PRODUCT"       : "owl:Thing",
    "EVENT"         : "dbo:Event",
    "WORK_OF_ART"   : "dbo:Work",
    #"LAW"           : "",
    "LANGUAGE"      : "dbo:Language",    
    "DATE"          : "owl:Thing",
    #"TIME"          : "",
    #"PERCENT"       : "",
    #"MONEY"         : "",
    #"QUANTITY"      : "",
    #"ORDINAL"       : "",
    #"CARDINAL"      : "",
    "NORP"          : "owl:Thing",
}

# TO BE Modified Here
sample_text = "Yes, Managua is the capital city of Nicaragua. It is located in the southwestern part of the country and is home to many important government buildings and institutions, including the President's office and the National Assembly. The city has a population of over one million people and is known for its vibrant cultural scene, historic landmarks, and beautiful natural surroundings."

sample2 = "Barack Hussein Obama II (Honolulu, 4 augustus 1961) is een Amerikaans politicus, advocaat, en schrijver. Hij was de 44e president van de Verenigde Staten, in functie van 20 januari 2009 tot 20 januari 2017 gedurende twee ambtsperiodes. Hij was de eerste Amerikaanse president van (deels) Afrikaanse afkomst."



def spacy_ner(text:str):
    """
    -> Using spacy trf library to extract entities.
    INPUT : [text](str) => string for extracting entities
    OUTPUT: (list)(entity_string, entity_label)  
    """

    nlp = spacy.load("en_core_web_trf")
    doc = nlp(text)
    #filtered_doc = [token.text for token in doc if not token.is_stop]
    ents = [[e.text, e.label_] for e in doc.ents]
    return ents

def build_SPARQL_query(entity_string: str, type: str) -> str:
    """
    -> Build query for SPARQL wrapper.
    INPUT : [entity_string](str) => entity, [type](str) => rdf type of entity
    OUTPUT: (str) query sentence for SPARQL query 
    """
    entity1 = ' '.join(entity_string.strip().strip("'\"").split()) 
    entity2 = entity1.replace(' ', '_')
    entity3 = titlecase(entity1)          # This Is A Title Case
    entity4 = entity3.replace(' ', '_')

    return f"""
     PREFIX owl:     <http://www.w3.org/2002/07/owl#>
            PREFIX xsd:     <http://www.w3.org/2001/XMLSchema#>
            PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX foaf:    <http://xmlns.com/foaf/0.1/>
            PREFIX dc:      <http://purl.org/dc/elements/1.1/>
            PREFIX dbr:     <http://dbpedia.org/resource/>
            PREFIX dpr:     <http://dbpedia.org/property/>
            PREFIX dbpedia: <http://dbpedia.org/>
            PREFIX skos:    <http://www.w3.org/2004/02/skos/core#>
            PREFIX dbo:     <http://dbpedia.org/ontology/>


            SELECT DISTINCT ?item ?name ?page (COUNT(?source) as ?count) WHERE {{
            {{
                # [Case 1] no disambiguation at all (eg. Twitter)
                ?item rdfs:label "{entity3}"@en .
            }}
            UNION
            {{
                # [Case 1] lands in a redirect page (eg. "Google, Inc." -> "Google")
                ?temp rdfs:label "{entity3}"@en .
                ?temp dbo:wikiPageRedirects ? ?item .   
            }}
            UNION
            {{
                # [Case 2] a dedicated disambiguation page (eg. Michael Jordan)
                <http://dbpedia.org/resource/{entity4}_(disambiguation)> dbo:wikiPageDisambiguates ?item.
            }}
            UNION
            {{
                # [Case 3] disambiguation list within entity page (eg. New York)
                <http://dbpedia.org/resource/{entity4}> dbo:wikiPageDisambiguates ?item .
            }}

            # Filter by entity class
            ?item rdf:type {type} .

            ?source dbo:wikiPageWikiLink ?item .

            # Grab wikipedia link
            ?item foaf:isPrimaryTopicOf ?page .

            # Get name
            ?item rdfs:label ?name .
            FILTER (langMatches(lang(?name),"en"))
        }}
    """

def generate_candidate(query: str) -> dict:
    """
    -> Generate candidates by querying the SPARQL on the dbpedia
    INPUT : [query](str) => query for sparql 
    OUTPUT: (dict) {cand_name1: [dbpedia_link, wiki_link]...} if there are candidates
    """
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setReturnFormat(JSON)

    sparql.setQuery(query)
    sparql.setTimeout(180)

    results = None
    for _ in range(2):
        try:
            results = sparql.query().convert()     
        except (ConnectionError, TimeoutError):
            return results
        except Exception as e:
            return results
        time.sleep(5)

    candidate_dict = dict()

    result_list = results["results"]["bindings"]
    for res in result_list:
        candidate_name = res["name"]["value"] if "value" in res["name"] else res["name"]
        dbpage = res["item"]["value"]
        wikipage = res["page"]["value"]    # TODO  if error
        candidate_dict[candidate_name] = [dbpage, wikipage]
    return candidate_dict

# TODO
def get_most_refer_cand(entity_string: str, candidates_dict: dict):

    # TODO: if no candidate generated
    
    candidates_list = candidates_dict["results"]["bindings"]
    if len(candidates_list) == 1:
        return candidates_list[0]["page"]["value"]
    # eles
    max_refer = 0
    popular_pages = []

    for cand in candidates_list:
        refer_count = int(cand["count"]["value"])

        if refer_count >= max_refer:
            max_refer = refer_count
            entity_name = cand["name"]["value"] if "value" in cand["name"] else cand["name"]

            popular_pages.append((entity_name, cand["page"]["value"], refer_count)) # append tuple
    
    # TO BE MODify
    most_popular_page = [page for page in popular_pages if page[-1] == max_refer]
    print (most_popular_page)
    if len(most_popular_page) == 1:
        return most_popular_page[0][1]
# TODO  
def get_most_popular_cand(entity_string, candidates_dict):
    popular_pages = []
    session = requests.Session()

    # TODO: if No candidate

    if len(candidates_dict) == 1:
        entity_name = candidates_dict[0]["name"]["value"] if "value" in candidates_dict[0]["name"] else candidates_dict[0]["name"]
        return [(entity_name, candidates_dict[0]["page"]["value"], candidates_dict[0]["item"]["value"])]
    
    # else
    for cand in candidates_dict["results"]["bindings"]:
        cand_name = cand["page"]["value"].split("/")[-1]

        # set the request parameters
        request_para = {          # TO BE MODify
            "action"        : "query",
            "format"        : "json",
            "list"          : "backlinks",
            "bltitle"       : cand_name, 
            "bllimit"       : 'max',
            "blnamespace"   : 4,
            "blredirect"    : "False"
        }

        # get the response
        response = session.get(url= wiki_url, params = request_para)
        if not response:  # if None, attempt once more
            time.sleep(5)
            response = session.get(url= wiki_url, params = request_para)
    
        data = response.json()
        max_backlinks = 0
        if "query" in data:
            backlinks = data["query"]["backlinks"]
            backlinks_length = len(backlinks)

            if backlinks_length > max_backlinks:
                max_backlinks = backlinks_length
                entity_name = cand["name"]["value"] if "value" in cand["name"]["value"]  else cand["name"]
                popular_pages.append((entity_name, cand["page"]["value"], cand["item"]["value"],  backlinks_length))
    if len(popular_pages) == 0:
        return popular_pages[0]
    
    if len(popular_pages) > 0:
        # TOBE MODify
        most_popular = [page for page in popular_pages if page[-1] == max_backlinks]

        # calculate the levenshtein distance between entity and page
        distances = [l_distance(entity_string, page[0]) for page in most_popular]
        if len(distances) > 0:
            best_page = np.argmin(distances)
            return most_popular[best_page]

        # TODO : alternative method # TOBEMODify
        distances = [] # similar ????
        for candidate in candidates_dict["results"]["bindings"]:
            entity_name = candidate["name"]["value"] if "value" in candidate["name"] else candidate["name"]
            distance = l_distance(entity_string, entity_name)
            if distance == 0:
                return entity_name, candidate["page"]["value"], candidate["item"]["value"]
            distances.append(distance)
        best = np.argmin(distances)
        candidate = candidates[best]
        entity_name = candidate["name"]["value"] if "value" in candidate["name"] else candidate["name"]
        return entity_name, candidate["page"]["value"], candidate["item"]["value"]
    
entity_list = spacy_ner(sample_text)
for ent in entity_list:
    if ent[0][:4] == "the " or ent[0][:4] == "The ": # TODO preprocessing
        ent[0] = ent[0][4:]
    
    query = build_SPARQL_query(ent[0], rdf_type_dict[ent[1]])
    candidate_dict = generate_candidate(query)
    print(ent[0])
    if candidat_dict is not None:
        for cand in candidate_dict.items():
            print(cand)
        #print("\n")
    #print(get_most_refer_cand(ent[0], candidate_dict))
    
