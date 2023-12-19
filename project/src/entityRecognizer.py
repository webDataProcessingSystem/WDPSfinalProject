import spacy
import nltk
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
from IOFunc import verbose

MODEL_NAME = "en_core_web_trf" # trf
wiki_url = "https://en.wikipedia.org/w/api.php"
dbpedia_url = "http://dbpedia.org/sparql"
stop_words = set(stopwords.words("english"))

THRESHOLD = 0.34

useless_word = ['disambiguation', 'list of']
num_related_label = ['ORDINAL', 'CARDINAL', 'TIME', 'QUANTITY', 'MONEY', 'PERCENT']
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
class EntityRecognizer:
    """
    Steps:
    1. Extract entities from text using spacy model
    2. Generate candidates for each candidate
    3. Rank candidates using its context-depedent and context-indepent feactures
    4. Return the disambiguated entity
    """
    def __init__(self, text: str, is_verbosed: bool, q_id: str):
        # constructor
        self._nlp = spacy.load(MODEL_NAME)
        self._q_id = q_id
        self._is_verbosed = is_verbosed
        self._text = text
        self._doc = self._nlp(text)
        self._entity_list = []
        self._entity_indices = {}
    
    def get_context(self, sentence:str, entity:str) -> list:
        """
        Get the context(in the sentence, without entity) of the entity
        """
        text_tokens = nltk.word_tokenize(sentence)
        entity_tokens = nltk.word_tokenize(entity)
        context = [w for w in text_tokens if w.lower() not in stop_words \
        and w not in string.punctuation \
        and len(w) > 1 \
        and w not in entity_tokens]
        return context

    def entity_extraction(self):
        verbose("### Starting entity_extraction for "+ self._q_id, self._is_verbosed)
        for ent in self._doc.ents:
            if ent.label_ in num_related_label: # Not deal with entity in num_related_label
                continue
            context = self.get_context(ent.sent.text, ent.text)
            entity_name = ent.text if (ent.text).lower()[:4] != "the " else ent.text[4:]
            self._entity_list.append({
                'entity': entity_name,
                'label': ent.label_,
                'context': context,
                'occurrence': self._text.count(entity_name)
            })
            self._entity_indices[entity_name] = [ent.start_char - ent.sent.start_char, ent.end_char - ent.sent.end_char]
            #print(ent.text, context)
            #print(ent.text, ent.sent)
        #print(self._entity_list)
        #return ents

    
    def build_SPARQL_query(self, entity_string: str, rdf_type: str):

        """
        -> Build query for SPARQL wrapper for DBpedia.
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
    def search_wiki(self, word: str,  extension: str , limitation: int) -> list:
        params = {
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srwhat': 'text',
            'srsearch': f'{word}' + '+' + f'{extension}',
            'srlimit': limitation
        }
        response = requests.Session().get(url = wiki_url, params= params)
        if response.status_code == 200:
            data = response.json()
            return data["query"]["search"]
        else:
            priint("failed to access wiki content in search_wiki()...")
    
    def generate_candidate_by_WIKI(self, entity:str, limitation: int = 3, bonus_score: int=1):
        """
        Generate candidates by searching wiki in keywords "entity" and "entity + other entity" separately,
        default grad the top 3 items(can set it as limitation), store top 3 items in each group in the candidates
        returned the sorted candidates dict by score (descent order)
        """
        verbose("### Generate candidates for "+ self._q_id + ": [ " + entity +" ].. Please wait...", self._is_verbosed)
        candidates = {}

        # generate candidates for entity and give a primary score
        for item in self._entity_list:   
            # searching keywords: entity + extension(other entities)
            extension = item['entity'] if item['entity'] != entity else ''   
            wiki_candidates = self.search_wiki(entity, extension, limitation)
            # if solely search entity word without extension, give 1 point bonus score (can be modified if wish)
            rank_score = len(wiki_candidates) + 1 + bonus_score  if extension == ''  else len(wiki_candidates) + 1 # TODO            
            for cand in wiki_candidates:
                if cand['pageid'] not in candidates:
                    candidates[cand['pageid']] ={
                    'title': cand['title'], 
                    'rank_score': rank_score
                    }
                else:
                    candidates[cand['pageid']]['rank_score'] += rank_score
                rank_score -= 1
        
        sorted_candidates = dict(sorted(candidates.items(), key = lambda item: item[1]['rank_score'], reverse = True))
        return sorted_candidates

    def generate_candidate_by_DBPEDIA(self, entity: str, w_type: str, limitations: int = 12):
        query = self.build_SPARQL_query(entity, rdf_type_dict[w_type])
        sparql = SPARQLWrapper(dbpedia_url)
        sparql.setReturnFormat(JSON)

        verbose("### Generate candidates for "+ self._q_id + ": [ " + entity +" ].. Please wait...", self._is_verbosed)
        sparql.setQuery(query)
        sparql.setTimeout(120)

        results = None
        for _ in range(2):
            try:
                results = sparql.query().convert()     
            except (ConnectionError, TimeoutError):
                return results
            except Exception as e:
                return results
            time.sleep(2)

        candidate_dict = dict()

        result_list = results["results"]["bindings"]      
        for res in result_list:
            candidate_name = res["name"]["value"] if "value" in res["name"] else res["name"]
            dbpage = res["item"]["value"]
            wikipage = res["page"]["value"]    # TODO  if error
            candidate_dict[candidate_name] = [dbpage, wikipage]
        return candidate_dict
    
    def rank_other_ent_by_distances(self, word: str):
        """
        return the sorted entities(other than word) ordered by distances
        """
        entity_dict = dict()
        word_index = int((self._entity_indices[word][1] + self._entity_indices[word][0])/2)
        for ent, value in self._entity_indices.items():
            if ent == word:
                continue
            cur_indx = int((self._entity_indices[ent][1] + self._entity_indices[ent][0])/2)
            entity_dict[ent] = abs(word_index - cur_indx)
        return dict(sorted(entity_dict.items(), key = lambda item: item[1])) 

  
    def cal_jaccard(self, token_list1: list, token_list2: list) -> float:
        if len(token_list1) == 0 or len(token_list2) == 0:
            return 0
        token_set1 = set(token_list1)
        token_set2 = set(token_list2)
        min_value = len(token_set1.intersection(token_set2))
        max_value = len(token_set2.union(token_set2))
        return min_value/max_value
    
    def get_wiki_intro(self, pageid: str) -> str:
        """
        get the wiki introduction via bs
        """
        url = "http://en.wikipedia.org/?curid=" + str(pageid)
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            intro_div = soup.find("div", {"class": "mw-content-ltr mw-parser-output"})
            intro_para = intro_div.find_all("p")[:4]

            intro_text = "\n".join([p.get_text() for p in intro_para])
            return intro_text
        else:
            print("error, failed to fetch wiki page.\n")
            return ''

    def get_wiki_link_by_pageid(self, pageid: int):
        link = "https://en.wikipedia.org/w/api.php?action=query&pageids=" + str(pageid) + \
        "&format=json&formatversion=2&prop=info|extracts&inprop=url"
        response = requests.Session().get(url = link)
        if response.status_code == 200:
            data = response.json()
            return data['query']['pages'][0]['fullurl']
        return ''


    def num_of_results(self, entity: str):
        headers = {'User-Agent': UserAgent().firefox}
        #time.sleep()
        response = requests.get("https://www.google.com/search?q={}".format(entity.replace(" ", "+")), headers= headers)

        soup = BeautifulSoup(response.text, "lxml")
        res = soup.find('div', {'id': 'result-stats'})
        if res == None: # try agian  TODO
            self.num_of_results(entity)
        else:
            return int(res.text.replace(".", "").split()[1])
        

    def cal_coherence_ngd(self, w1: str, w2: str):
        """
        Not scalable features for None result returned from Google
        """
        # N = number of results("the")
        N = 25270000000.0
        N = math.log(N, 2)
        if w1 != w2:
            f_w1 = math.log(self.num_of_results(w1), 2)
            f_w2 = math.log(self.num_of_results(w2), 2)
            f_w1_w2 = math.log(self.num_of_results(w1 + " " + w2), 2)
            res = (max(f_w1, f_w2) - f_w1_w2) / (N - min(f_w1, f_w2))
            return res
        else:
            return 0

    def cal_entity_hit(self, entity:str, other_entities:dict, candidate_title: str)-> int:
        entity_token = word_tokenize(entity)
        #candidate_token = word_tokenize(entity)
        candidate_token = [w for w in word_tokenize(candidate_title) if w.lower() not in stop_words and w not in string.punctuation]
        hit_score = 0
        len_candidate = len(candidate_token)
        for token in entity_token:
            hit_score += 1/len_candidate if token in candidate_token else 0
        
        for ent in other_entities.keys():
            other_ent_token = [w for w in word_tokenize(ent) if w.lower() not in stop_words and w not in string.punctuation]
            for tt in other_ent_token:
                hit_score += 1/len_candidate if tt in candidate_token else 0
        return hit_score

    def ranking_candidate(self, entity:str, candidates:dict, top_num: int=3):
        """
        Principle of ranking :
            1. Rank score in the wiki searching results (decremented) (0~1)
                - Calculated by score/sum_of_score
            2. Jaccord similarity (0~1): greater = better
            3. Hit score(0~1): =hit_number/lenght_of_candidate, if hit score lower than threshold, ignore it
        """
        if len(candidates) == 1:   # although the possibility is extremely low
            return candidates
        
        temp_num = top_num
        for ent in self._entity_list:
            if ent['entity'] == entity:
                entity_context = ent['context']
        #print(entity_context)
        last_score = 0
        
        ranked_candidates = dict()
        sum_score = 0
        weight_dict = dict()

        other_entities = self.rank_other_ent_by_distances(entity)
        for pageid, item in candidates.items():

            if  item['title'].lower() in useless_word: 
                continue
            hit_score = self.cal_entity_hit(entity, other_entities, item['title'])

            # filter out unrelated candidates
            if hit_score <= THRESHOLD:
                continue

            wiki_text = self.get_wiki_intro(pageid)
            wiki_context = self.get_context(wiki_text, item['title'])
            jaccard_similarity = self.cal_jaccard(wiki_context, entity_context)
            
            ranked_candidates[pageid] = {
                'title': item['title'],
                'jaccard': jaccard_similarity,
                'hit_score': hit_score,
                'rank_score': item['rank_score']
            }
            sum_score += item['rank_score']

            weight_dict[pageid] = round((item['rank_score']/sum_score) + (jaccard_similarity) + (hit_score), 2)
    
            if last_score != item['rank_score']:
                last_score = item['rank_score']
                temp_num -= 1

            if temp_num == 0:
                break
        weighted_dict = dict(sorted(weight_dict.items(), key = lambda item: item[1], reverse = True))
        return ranked_candidates, weighted_dict
    
    def get_highest_weight_entity(self, entity: str, candidates: dict)-> dict:
        """
        Rank the candidates according their weights, return the highest one
        return {'entity': entity_name, 'entity_link': entity_link}
        """
        ranked_candidates, weighted_dict = self.ranking_candidate(entity, candidates)
        verbose(">>>>>> Ranked candidates of " + entity, self._is_verbosed)
        verbose(ranked_candidates, self._is_verbosed)
        verbose(">>>>>> Weighted score of candidates", self._is_verbosed)
        verbose(weighted_dict, self._is_verbosed)
        for k, v in weighted_dict.items():
            entity_name = ranked_candidates[k]['title']
            entity_link = self.get_wiki_link_by_pageid(k)
            return {'entity': entity_name, 'entity_link': entity_link}
        return {}

    def entity_linking(self):
        for item in self._entity_list:
            candidates = self.generate_candidate_by_WIKI(item['entity'])
            #verbose(candidates, self._is_verbosed)
            res = self.get_highest_weight_entity(item['entity'], candidates)
            verbose(">>>>>> Disambiguated entity: ", self._is_verbosed)
            verbose(res, self._is_verbosed)

        
    
    
