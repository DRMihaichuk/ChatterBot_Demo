import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import argparse
import json
import openai
import time
from openai.error import RateLimitError, APIError
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key
parser = argparse.ArgumentParser(description="For scraping wbesites and generating training data on them")
parser.add_argument("url", help="what url should be scraped")
args = parser.parse_args()

def extract_h1_and_paragraphs(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    entries = []

    content = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p'])
    i = 0

    while i < len(content):
        tag = content[i]

        if tag.name == 'h1':
            heading_text = tag.get_text(strip=True)
            summary_parts = []
            i += 1

            # Collect all paragraphs until the next header
            while i < len(content) and content[i].name == 'p':
                summary_parts.append(content[i].get_text(strip=True))
                i += 1

            if summary_parts:
                summary = ' '.join(summary_parts)
                entries.append({
                    "heading": heading_text,
                    "summary": summary,
                    "url": url
                })
        else:
            i += 1

    return entries

def generate_questions(heading):
    prompt = f"Generate only a Python array of different natural questions a user might ask if they were looking for information under the heading: '{heading}'."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        # Extract content from response and eval to turn into actual Python list
        content = response.choices[0].message['content'].strip()
        questions = eval(content) if content.startswith("[") else [content]
        return questions
    except RateLimitError:
        print("⚠️ Rate limit or quota reached. Waiting 3 seconds before retrying...")
        time.sleep(3)
        return generate_questions(heading)  # Retry recursively
    except APIError as e:
        print(f"⚠️ OpenAI API error: {e}")
        return []
    except Exception as e:
        print(f"⚠️ Unexpected error in generate_questions: {e}")
        return []

def generate_summary(content):
    prompt = f"Generate a summary of the information in this content: '{content}'"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message['content'].strip()
    except RateLimitError:
        print("⚠️ Rate limit or quota reached. Waiting 3 seconds before retrying...")
        time.sleep(3)
        return generate_summary(content)  # Retry recursively
    except APIError as e:
        print(f"⚠️ OpenAI API error: {e}")
        return "Summary unavailable."
    except Exception as e:
        print(f"⚠️ Unexpected error in generate_summary: {e}")
        return "Summary unavailable."

def build_training_data(url):
    scraped_data = extract_h1_and_paragraphs(url)
    chatbot_entries = []

    for entry in scraped_data:
        summary = generate_summary(entry['summary'])
        brief_answer = f"{summary} For more details, visit {entry['url']}."
        user_questions = generate_questions(entry['heading'])

        for question in user_questions:
            chatbot_entries.append({
                "aPrompt": question,
                "bResponse": brief_answer,
                "cSubject": '',
                "dLanguage": 'English',
                "eVerified Language": 'Yes',
                "fStatus": 'Imported'
            })

    return chatbot_entries

data = build_training_data(args.url)
with open("scrape_data.json", "w", encoding='utf-8') as f:
    json.dump(data, f, indent=4)
