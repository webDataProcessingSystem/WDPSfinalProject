for item in self._entity_list:   # TODO
            extension = item['entity'] if item['entity'] != entity else ''   
            wiki_candidates = self.search_wiki(entity, extension)
            rank_score = len(wiki_candidates) + 1   # TODO  not sure
            #candidates = search_and_score()
            #rank_candidate = rank_other_ent_by_distances(entity)
            
            for cand in wiki_candidates:
                if cand['pageid'] not in candidates:
                    candidates[cand['pageid']] ={
                    'title': cand['title'], # may contain () as disambiguation
                    'score': rank_score
                    }
                else:
                    candidates[cand['pageid']]['score'] += rank_score
                rank_score -= 1
        
        sorted_candidates =sorted(candidates.items(), key = lambda item: item[1]['score'], reverse = True)
        #print(list(candidates.values()).sort(key=sort_by_score))
        #print(candidates.values())
        