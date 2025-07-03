import os
import json
import random
from together import Together
from typing import Literal
from urllib.parse import urlparse, parse_qs
from itertools import islice
from youtube_comment_downloader import YoutubeCommentDownloader

keys = json.loads(os.getenv('KEYS', '[]'))
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
    full_messages = [
        {"role": "system", "content": instruct}
    ] + messages + [{"role": "user", "content": prompt}]

    response = ai.chat.completions.create(
        model=model,
        messages=full_messages
    )

    data = json.loads(response.choices[0].message.content)
    return data

def ytgen(video_url: str):
    try:
        video_id = parse_qs(urlparse(video_url).query).get("v", [""])[0]

        downloader = YoutubeCommentDownloader()
        comments = []
        for comment in islice(downloader.get_comments_from_url(video_url, sort_by=0), 55):
            if "text" in comment:
                comments.append(comment["text"])

        # Trim to ~6500 chars max
        max_chars = 6500
        content = f"Top Comments:\n"
        for i, comment in enumerate(comments):
            line = f"{i+1}. {comment}\n"
            if len(content) + len(line) > max_chars:
                break
            content += line

        messages = [
            {
                "role": "system",
                "content": """You are a smart YouTube comment summarizer 🤖.
Your job is to write a <b>brief</b>, concise summary of a YouTube video's comments and reactions.
Use <b>HTML tags</b> (like <b>, <i>, <span>) for styling, and insert emojis 🎯 beside relevant words (like love ❤️, sad 😢, cringe 😬, music 🎵, edit ✂️).
Don't use Markdown or JSON. Just return a styled, emoji-enhanced HTML string.
Just the summary no extra system texts, and keep the emoji use subtle!"""
            },
            {
                "role": "user",
                "content": f"""{content}"""
            }
        ]

        ai = Together(api_key=random.choice(keys))
        response = ai.chat.completions.create(
            model=model,
            messages=messages
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return str(e)
