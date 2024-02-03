import google.generativeai as genai
import json
import time 
import google.generativeai as genai
import json
import time 

# Or use `os.getenv('GOOGLE_API_KEY')` to fetch an environment variable.

genai.configure(api_key=GOOGLE_API_KEY)

for m in genai.list_models():
  if 'generateContent' in m.supported_generation_methods:
    print(m.name)

model = genai.GenerativeModel('gemini-pro')

def get_first_prompt(scenario):
    """
    Generates the entire conversation given a scenario

    """
    text = f"""
    Given the below scenario, you need to generate a convesation between 2 people. It needs to be in beginner english, to help a learner to learn the language.
    Output a JSON list.

    Example:
    Scenario: Conversation between a person and a waiter, where person is ordering food:
    JSON response:
    [{{"user1": "person1", "text": "Hello, what would you like to eat"}}, {{"user2": "person2", "text": "i would like to order pasta"}}, {{"user1": "person1", "text": "sure, would you like anything else"}}, {{"user2": 'person2', "text": "no thank you, i dont want anything else"}}]

    Generate a conversation with 10 responses for the below with each person speaking more than two words
    {scenario}
    """
    
    return text
    
def get_bard_response(prompt):
    """
    Given prompt, calls bard and gets the response 
    """

    generation_config = {'temperature': 0.95}
    completion = model.generate_content(prompt, generation_config=generation_config)
    
    completion_text = completion.text

    time.sleep(1)
    
    return completion_text

def get_user2_text(parsed_response):
    user1 = [] 
    user2 = [] 
    user2_text = []
    
    for row in parsed_response: 
        if 'user1' in row:
            user1.append(row)
        elif 'user2' in row:
            user2.append(row)
            user2_text.append(row['text'])
        else:
            print('Missing key')

    return user1, user2, user2_text

def get_prompt_blankout(list_of_sentences):
    text = f"""
    Given a list of strings, you need to blank out one word from each string. You are a language learning assistant, so you have to blank out
    the word that a person should be learning. 

    Example Input:
    ["I would like to order pasta', "I would like to sit on that table"]
    Output:
    ["I would like to BLANK pasta", "I would like to BLANK on that table"]

    For each item in INPUT, blank out only one word according to the above rules and output a list:
    {list_of_sentences} 
    """
    
    return text


def extract_text_between_backticks(text):
    import re
    pattern = r'```([\s\S]*?)```'
    matches = re.findall(pattern, text)
    if matches:
        return matches[0]
    return ''

def parse_json(response):

    try:
        output = json.loads(response)
        return output
    except:
        pass

    try:
        output = eval(response)
    except:
        
        print('direct json parsing failed removing backticks')

        try:
            response2 = extract_text_between_backticks(response)
            if response2[:4].strip() == 'JSON': 
                response2 = response2.strip()[4:]
            output = json.loads(response2)
            return output
        except: 
            raise ValueError('Parsing failed for\n', response)
            
    return output 

def get_grade_prompt(question, response):
    prompt = f"""
You are a language learning assistant. You have to grade a response to a question as good or bad given level of english fluency. Judge the grammar and word usage of the response and give the rating.
For example: 

Question: Can I start you off with a drink?
Response: I will have a table of water for now
Output: bad

For the below input, output good or bad according to the above rules:
Question: {question}
Response: {response}

Output:
"""
    return prompt
    
def grade_response(question, prompt):
    prompt = get_grade_prompt(question, response)
    rating = get_bard_response(prompt)
    return 'good' in rating.lower() 


def get_dataset(user1, user2, blanked_sentences_parsed):
    dataset = []
    correct_dataset = [] 
    for i in range(len(user1)):
        row = user1[i]
    
        dataset.append({ **user1[i], 'messageType': 'QUESTION'})
        correct_dataset.append(user1[i])

        if i < len (user2):
            # dataset.append(user2[i])
            dataset.append({'user2': 'person2', 'messageType': 'ANSWER', 'aiAnswer': blanked_sentences_parsed[i]})
            correct_dataset.append({'user2': 'person2', 'text': user2[i]['text']})

    for k in range(len(dataset)):
        dataset[k]['id'] = k 
    
    return dataset, correct_dataset
    

def run_pipeline(scenario = 'Conversation between waiter and customer'):
    # generate scenario for conversation 
    prompt_scenario = get_first_prompt(scenario)
    prompt_response = get_bard_response(prompt_scenario)
    # parse the scenario with json 
    parsed_response = parse_json(prompt_response)
    # blank out sentences from user 2 
    user1, user2, user2_text = get_user2_text(parsed_response)
    prompt_blankout = get_prompt_blankout(user2_text)
    blanked_sentences = get_bard_response(prompt_blankout)
    blanked_sentences_parsed = parse_json(blanked_sentences)

    # if len(blanked_sentences_parsed) != len(user2):
    #     import pdb
    #     pdb.set_trace() 
        
    dataset, correct_dataset = get_dataset(user1, user2, blanked_sentences_parsed)
    return dataset, correct_dataset
    
    
    
