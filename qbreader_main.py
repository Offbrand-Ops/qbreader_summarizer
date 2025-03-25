import requests
from qbreader import Sync
from openai import OpenAI
import json
from secrets import keys

def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}

# Anki Connect url
acu = "http://localhost:8765"

# ChatGPT stuff
client = OpenAI(
    api_key = keys.get("api_key"),
)

qbr = Sync()

keyword = input("What keyword would you liked searched? ")
difficulties = input("What difficulty levels would you like. Please answer with a series of digits or ALL. ")
category = input("What category would you like to search through. Please capitalize each word of category. If all, please type ALL. ")

results = qbr.query(questionType="tossup", searchType="answer", queryString=keyword, exactPhrase=True, difficulties=None if difficulties == 'ALL' else difficulties, categories=None if category == 'ALL' else category, maxReturnLength=10000)

for i in range(0, results.tossups_found-1):
    response = client.responses.create(
        model='gpt-4o-mini',
        instructions="You are a helpful AI assistant that is going to summarize all the trivia questions and answers I, the user, will give you and put them into neat flashcards. Do it for every question I provide to you. Repeat information should be skipped and not made into a new card. Unless in italics or quotes, an adjective cannot be used as a title for a piece. Please make sure every question card is only asking one thing. Do not have both \"who ___\" and \"this ___\" on the same card. Please format every flashcard with question side having \"Front\": \"Question_Text\", and the answer side have \"Back\": \"answer\". Please only place a newline character between every card. Every flashcard will only have one piece of information on the question side, and then the answer on the other. Make sure every card has a different fact on the question side. Multiple flashcards can have the same answer.",
        input=f"Here are the questions{results.tossups[i].question}, here are the answers{results.tossups[i].answer}.",
    )

    cards = response.output_text.split("\n")

    for card in cards:
        card = card.strip()
        if not card:
            continue

        if not (card.startswith('{') and card.endswith('}')):  # Ensure it's JSON-like
                print("Skipping invalid JSON line:", card)
                continue

        card_data = json.loads(card)
        front_text = card_data.get("Front")
        back_text = card_data.get("Back")
    
        if front_text and back_text:
            r = requests.post('http://localhost:8765', json={
                "action": "addNote",
                "version": 6,
                "params": {
                    "note":{
                        "deckName": "test",
                        "modelName": "Basic",
                        "fields": {
                            "Front": front_text,
                            "Back": back_text,
                        }
                    }
                }
            })
    print("Card completed. Moving on to next card.")