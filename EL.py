import spacy
import nltk
#from typing import List
from nltk.tokenize import word_tokenize
from collections import defaultdict
from nltk.corpus import stopwords
import string
from titlecase import titlecase
from SPARQLWrapper import SPARQLWrapper, JSON
import time
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
import math

model_name = "en_core_web_trf"
wiki_url = "https://en.wikipedia.org/w/api.php"
dbpedia_url = "http://dbpedia.org/sparql"
stop_words = set(stopwords.words("english"))
# spacy tag_list at: https://github.com/explosion/spaCy/blob/master/spacy/glossary.py  line329
rdf_type_dict = {
    "PERSON"        : "dbo:Person",
    "NORP"          : "owl:Thing",
    "FACILITY"      : "owl:Thing",
    "FAC"           : "geo:SpatialThing",
    "ORG"           : "dbo:Organisation",
    "GPE"           : "geo:SpatialThing",
    "LOC"           : "geo:SpatialThing",
    "PRODUCT"       : "owl:Thing",
    "EVENT"         : "dbo:Event",
    "WORK_OF_ART"   : "dbo:Work",
    "LAW"           : "owl:Thing",
    "LANGUAGE"      : "dbo:Language",    
    "DATE"          : "owl:Thing",
    "TIME"          : "owl:Thing",
    "PERCENT"       : "owl:Thing",
    "MONEY"         : "owl:Thing",
    "QUANTITY"      : "owl:Thing",
    "ORDINAL"       : "owl:Thing",
    "CARDINAL"      : "owl:Thing",
    "NORP"          : "owl:Thing",
}
class Candidates:
    def __init__(self, word: str, w_type: str, entity_indices: dict):
        
        self._mention = word
        self._w_type = w_type

        candidate_result = self.generate_candidates(word, w_type)
        if len(candidate_result) > 0:
            self._candidates = candidate_result
        else: # do modifications on the mention
            #print(self._mention)
            if word.lower()[:4] == "the ":
                self._mention = word[4:]
                #print(self._mention)
                candidate_result = self.generate_candidates(self._mention, w_type)
                if len(candidate_result)== 0: # try another combinations 
                    #tokens = nltk.word_tokenize(self._mention)
                    #for token in tokens and token not in stop_words:
                        #print(self.search_wiki(token))  # TODO
                    
                    #sorted_entity = self.rank_other_ent_by_distances(word, entity_indices)
                    # TODO try google or wiki

                    self._candidates = dict()
                else:
                    self._candidates = candidate_result

        self._candidates_info = dict()

    def build_SPARQL_query(self, entity_string: str, rdf_type: str):
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
                ?item rdf:type {rdf_type} .

                ?source dbo:wikiPageWikiLink ?item .

                # Grab wikipedia link
                ?item foaf:isPrimaryTopicOf ?page .

                # Get name
                ?item rdfs:label ?name .
                FILTER (langMatches(lang(?name),"en"))
            }}
        """
    
    def generate_candidates(self, word: str, w_type:str):

        query = self.build_SPARQL_query(word, rdf_type_dict[w_type])
        sparql = SPARQLWrapper(dbpedia_url)
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

        result_list = results["results"]["bindings"]      # TODO: limitations
        for res in result_list:
            candidate_name = res["name"]["value"] if "value" in res["name"] else res["name"]
            dbpage = res["item"]["value"]
            wikipage = res["page"]["value"]    # TODO  if error
            candidate_dict[candidate_name] = [dbpage, wikipage]
        return candidate_dict
    
    def get_wiki_intro(self, url: str):
        """
        get the wiki introduction via bs
        """
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            intro_div = soup.find("div", {"class": "mw-content-ltr mw-parser-output"})
            intro_para = intro_div.find_all("p")[:4]

            intro_text = "\n".join([p.get_text() for p in intro_para])
            print(intro_text)
        else:
            print("error, failed to fetch wiki page.\n")
            return None

    def search_wiki(self, word: str, limitation: int = 10):
        params = {
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srwhat': 'text',
            'srsearch': f'{word}',
            'srlimit': limitation
        }
        response = requests.Session().get(url = wiki_url, params= params)
        if response.status_code == 200:
            data = response.json()
            return data["query"]["search"]
        else:
            priint("failed to access wiki content in search_wiki()...")

    def rank_other_ent_by_distances(self, word: str, entity_indices: dict):
        entity_dict = dict()
        word_index = int((entity_indices[word][1] + entity_indices[word][0])/2)
        for ent, value in entity_indices.items():
            if ent == word:
                continue
            cur_indx = int((entity_indices[ent][1] + entity_indices[ent][0])/2)
            entity_dict[ent] = abs(word_index - cur_indx)
        return dict(sorted(entity_dict.items(), key = lambda item: item[1])) # return the sorted dict

class EntityLinking:
    def __init__(self, text: str, model_name: str):  
        self._nlp = spacy.load(model_name)
        self._doc = self._nlp(text)
        self._entity_list = self.spacy_ner()
        self._context, self._occurrence = self.get_context_per_sent()
        self._entity_indices = self.get_entity_indices()

    def spacy_ner(self):
        ents = [[e.text, e.label_] for e in self._doc.ents]
        return ents

    def get_entity_indices(self):
        res_dict = dict()
        for ent in self._doc.ents:
            res_dict[ent.text] = [ent.start_char - ent.sent.start_char, ent.end_char - ent.sent.end_char]
        return res_dict

    def get_context(self, sent: str, entity: str):
        text_tokens = nltk.word_tokenize(sent)
        entity_tokens = nltk.word_tokenize(entity)
        

        context = [w for w in text_tokens if w.lower() not in stop_words \
        and w not in string.punctuation \
        and len(w) > 1 \
        and w not in entity_tokens]
        return context

    def get_context_per_sent(self):

        context = defaultdict(list)
        occurrence = dict()
        for ent in self._entity_list:
            for sent in self._doc.sents:     # DO MODification                
                if ent[0] in sent.text:
                    context[ent[0]].append(self.get_context(sent.text, ent[0]))
                    occurrence[ent[0]] = 1 if ent[0]  not in occurrence else occurrence[ent[0]] + 1
        return context, occurrence

    

sample_text = "Yes, Managua is the capital city of Nicaragua. It is located in the southwestern part of the country and is home to many important government buildings and institutions, including the President's office and the National Assembly. The city has a population of over one million people and is known for its vibrant cultural scene, historic landmarks, and beautiful natural surroundings."

sample2 = "Barack Hussein Obama II (Honolulu, 4 augustus 1961) is een Amerikaans politicus, advocaat, en schrijver. Hij was de 44e president van de Verenigde Staten, in functie van 20 januari 2009 tot 20 januari 2017 gedurende twee ambtsperiodes. Hij was de eerste Amerikaanse president van (deels) Afrikaanse afkomst."

el = EntityLinking(sample_text, model_name)
#print(el._entity_list)
for ent in el._entity_list:
    cand = Candidates(ent[0], ent[1], el._entity_indices)
    #print(cand._candidates)
#print(el.get_context_per_sent())
#print(el._context, el._occurrence)
