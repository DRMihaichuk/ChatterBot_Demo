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
from urllib.parse import urlparse

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key

def extract_h1_and_paragraphs(url, format):
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

    if format == "JSON":
        question_number = int(18 / len(entries))
        if question_number <= 0:
            entries = entries[:18]
            question_number = 1
        # print(len(entries), question_number)
        return entries, question_number
    return entries, "many"

def generate_questions(heading, question_number):
    prompt = f"""
    Generate exactly {question_number} short, distinct questions a user might ask under the heading: '{heading}'.

    Return only a valid Python list of strings. 
    Each item should be a clean question in quotes, with no numbering or line breaks in the list elements.
    Example format: ["What is X?", "How does Y work?", "Why is Z important?"]
    """

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
    prompt = f"Answer the question '{question}' using the information stated here: '{content}' in a brief response"

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

def build_training_data(url, format):
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip('/').split('/')
    if path_parts and len(path_parts) > 0:
        if path_parts == 'ro':
            language = "Romanian"
        elif path_parts == 'ru':
            language = "Russian"
        elif path_parts == 'uk':
            language = "Ukrainian"
        elif path_parts == 'en':
            language = "English"
        else:
            language = "Unrecognized"

    scraped_data, qs = extract_h1_and_paragraphs(url, format)

    if format == "JSON":
        chatbot_entries = []
    else:
        chatbot_entries = ''

    for entry in scraped_data:
        user_questions = generate_questions(entry['heading'], qs)
        # print(user_questions)

        for question in user_questions:
            answer = f"{generate_answer(question, entry['summary'])} For more details, visit {entry['url']}."
            if format == "JSON":
                chatbot_entries.append({
                    "aPrompt": question,
                    "bResponse": answer,
                    "cSubject": '',
                    "dLanguage": language,
                    "eVerified Language": 'Yes',
                    "fStatus": 'Scraped'
                })
            else:
                chatbot_entries += f'"{question}","{answer}","","{language}","Yes","Scraped"\n'

    return chatbot_entries

if __name__ == "__main__":
    # Only runs when executed directly, not when imported
    parser = argparse.ArgumentParser(description="Scrape for training")
    parser.add_argument("url", help="URL to scrape")
    parser.add_argument("--format", help="the format of the information given", default="JSON")
    args = parser.parse_args()
    args.format = args.format.upper()
    data = build_training_data(args.url, args.format)
    if args.format == "JSON":
        with open("scrape_data.json", "w") as f:
            json.dump(data, f, indent=2)
    else:
        with open("scrape_data.csv", "w") as f:
            f.write(data)