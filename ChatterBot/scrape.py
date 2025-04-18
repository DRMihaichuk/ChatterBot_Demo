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

def generate_answer(question, content):
    prompt = f"Answer the question '{question}' using the information stated here: '{content}'"

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
        return generate_answer(question, content)  # Retry recursively
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
        user_questions = generate_questions(entry['heading'])

        for question in user_questions:
            answer = f"{generate_answer(question, entry['summary'])} For more details, visit {entry['url']}."
            chatbot_entries.append({
                "aPrompt": question,
                "bResponse": answer,
                "cSubject": '',
                "dLanguage": 'English',
                "eVerified Language": 'Yes',
                "fStatus": 'Imported'
            })

    return chatbot_entries

if __name__ == "__main__":
    # Only runs when executed directly, not when imported
    parser = argparse.ArgumentParser(description="Scrape for training")
    parser.add_argument("url", help="URL to scrape")
    args = parser.parse_args()
    data = build_training_data(args.url)
    print(json.dumps(data, indent=2))