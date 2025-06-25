import os
import json
import random
from together import Together
from typing import Literal

keys = f"[{os.getenv('KEYS')}]"
model = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"

instructJSON = """
You are a JSON Expert AI!
You are designed to generate any type of mock json data on any given prompt!
The prompts can be anything from a sentence to only a json data that you have to work on!
Examples:
- Sentence:
1. Menu for chinese restaurant,
2. Any mock data,
3. School Students examination,
4. Tech Products,
etc

- Json Data:
Sometimes only json data is provided with not much context, then you have to do the thinking
it could be only keys and you would have to decide the values for it:
list(name, address, email, etc)
or it could be keys with values but the values would be the description of what should be the values:
name: (any name)
address: (any authentic address)
email: (only gmail domain)
verified: (boolean)
age: (between 18 and 40)

etc
- Sometimes it could be both sentence and json data
- Sometimes you may not get any prompt, so just respond with a generic mock json data that consists of every json datatype for testing purposes!

INTRUCTIONS ON HOW TO RESPOND:
- respond only with json data
- no system texts/texts,
- no backticks,
- no codeblocks,
"""

def generate(prompt: str, mock_type: Literal["json", "xml", "yaml", "html"], messages: list) -> dict:
    mock_type = mock_type.lower()
    instruct = {
        "json": instructJSON,
    }.get(mock_type)
    
    ai = Together(api_key=random.choice(keys))
    # Combine system instruction with provided messages
    full_messages = [
        {"role": "system", "content": instruct}
    ] + messages + [{"role": "user", "content": prompt}]
    
    response = ai.chat.completions.create(
        model=model,
        messages=full_messages
    )
    
    data = json.loads(response.choices[0].message.content)
    return data
