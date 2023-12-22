import requests
#from questionClassify import QuestionClassify
import spacy

nlp = spacy.load("en_core_web_sm")


def verify_yes_no_answer_with_wikipedia(question, user_answer):

    response = requests.get(f"https://en.wikipedia.org/w/api.php",
                            params={"action": "query", "list": "search", "srsearch": question, "format": "json"})
    if response.status_code != 200:
        return False

    search_results = response.json().get("query", {}).get("search", [])
    if not search_results:
        return False

    for result in search_results:
        page_id = result.get("pageid")
        page_response = requests.get(f"https://en.wikipedia.org/w/api.php",
                                     params={"action": "query", "prop": "extracts", "pageids": page_id, "format": "json"})
        page_content = page_response.json().get("query", {}).get("pages", {}).get(str(page_id), {}).get("extract", "")
        doc = nlp(page_content)
        
        if user_answer.lower() in ["yes", "no"]:
            if user_answer.lower() == "yes" and question.lower() in page_content.lower():
                return True
            elif user_answer.lower() == "no" and question.lower() not in page_content.lower():
                return True
    return False

#fact check question with entity
def verify_answer_with_wikipedia(question, user_answer):
    # use Wikipedia API
    response = requests.get(f"https://en.wikipedia.org/w/api.php",
                            params={"action": "query", "list": "search", "srsearch": question, "format": "json"})
    if response.status_code != 200:
        return False

    search_results = response.json().get("query", {}).get("search", [])
    if not search_results:
        return False

    for result in search_results:
        page_id = result.get("pageid")
        page_response = requests.get(f"https://en.wikipedia.org/w/api.php",
                                     params={"action": "query", "prop": "extracts", "pageids": page_id, "format": "json"})
        page_content = page_response.json().get("query", {}).get("pages", {}).get(str(page_id), {}).get("extract", "")
        doc = nlp(page_content)
        for sentence in doc.sents:
            if user_answer.lower() in sentence.text.lower():
                return True
    return False

# test
# question = "Where is the capital of France?"
# user_answer = "Paris"
# print(verify_answer_with_wikipedia(question, user_answer))  # output: True or False


# # test
# question = "Is London the capital of France?"
# user_answer = "no"
# print(verify_yes_no_answer_with_wikipedia(question, user_answer))  # output: True or False

"""
sample_question = [{'q_id': 'question-001', 'question': 'Is Managua the capital of Nicaragua?', 'user_answer': 'yes'}, \
{'q_id': 'question-002', 'question': 'the capital of nicaragua is...', 'user_answer': 'Managua'}]

qc = QuestionClassify()
for item in sample_question:
    if qc.classify_question(item['question']) == 0:
        print(verify_yes_no_answer_with_wikipedia(item['question'], item['user_answer']))
    else:
        print(verify_answer_with_wikipedia(item['question'], item['user_answer']))
"""