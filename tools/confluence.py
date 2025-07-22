import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import re
import requests
import urllib3
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth
from spellchecker import SpellChecker
from difflib import get_close_matches
from config import ATLASSIAN_API_BASE_URL, ATLASSIAN_BASE_URL_WIKI, ATLASSIAN_PASSWORD, ATLASSIAN_USERNAME

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



# Stopwords and tech terms
STOPWORDS = {
    "how", "to", "in", "on", "the", "a", "an", "is", "of", "and", "for", "with", "by", "at", "from", "that",
    "what", "are", "was", "were", "will", "can", "should", "could", "would", "do", "does", "did", "has", "have", "had",
    "i", "am", "facing", "you", "your", "we", "our", "it", "this", "those", "these", "as", "be", "if", "or", "working", "work"
}

TECH_TERMS = {
    "gitlab", "ssh", "key", "token", "pipeline", "deployment", "authentication", "authorization",
    "ssl", "certificate", "login", "logout", "session", "cache", "database", "query", "search",
    "page", "space", "label", "title", "content", "update", "create", "delete", "api", "proxy",
    "roles", "permissions", "jira", "confluence"
}

spell = SpellChecker()

def smart_correct_query(query):
    words = re.findall(r'\w+', query.lower())
    corrected = []
    for word in words:
        if word in TECH_TERMS:
            corrected.append(word)
        else:
            close_matches = get_close_matches(word, TECH_TERMS, n=1, cutoff=0.8)
            if close_matches:
                corrected.append(close_matches[0])
            else:
                suggestion = spell.correction(word)
                corrected.append(suggestion if suggestion else word)
    return ' '.join(corrected)

def normalize_query(query):
    words = re.findall(r'\w+', query.lower())
    return [word for word in words if word not in STOPWORDS]

def build_cql_query(words):
    title_conditions = ' AND '.join([f'title ~ "{word}"' for word in words])
    text_conditions = ' AND '.join([f'text ~ "{word}"' for word in words])
    return f'(({title_conditions}) OR ({text_conditions})) AND type=page'

def get_page_views(page_id):
    analytics_url = f"{ATLASSIAN_BASE_URL_WIKI}/rest/api/analytics/content/{page_id}/views"
    response = requests.get(
        analytics_url,
        auth=HTTPBasicAuth(ATLASSIAN_USERNAME, ATLASSIAN_PASSWORD),
        verify=False
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("count", 0)
    else:
        print(f"Failed to fetch analytics for page {page_id}: {response.status_code}")
        return 0

def normalize_scores(scores):
    min_score = min(scores)
    max_score = max(scores)
    if max_score == min_score:
        return [0.5] * len(scores)
    return [(s - min_score) / (max_score - min_score) for s in scores]

def compute_combined_score(date_scores, view_scores, date_weight=0.35, view_weight=0.65):
    norm_date = normalize_scores(date_scores)
    norm_views = normalize_scores(view_scores)
    return [
        date_weight * d + view_weight * v
        for d, v in zip(norm_date, norm_views)
    ]

def search_confluence(cql_query):
    search_url = f'{ATLASSIAN_API_BASE_URL}/content/search'
    params = {
        'cql': f'({cql_query})',
        'expand': 'version,body.storage',
        'limit': 2
    }
    response = requests.get(
        search_url,
        params=params,
        auth=HTTPBasicAuth(ATLASSIAN_USERNAME, ATLASSIAN_PASSWORD),
        verify=False
    )
    

    print("Status Code:", response.status_code)
    print("Response Text:", response.text)


    results_data = []

    if response.status_code == 200:
        results = response.json().get('results', [])
        for result in results:
            title = result.get('title', 'No Title')
            last_updated = result.get('version', {}).get('when', 'Unknown Date')
            page_id = result.get('id')
            views = get_page_views(page_id)
            content_url = f"{ATLASSIAN_BASE_URL_WIKI}/wiki/pages/viewpage.action?pageId={page_id}"

            html_content = result.get("body", {}).get("storage", {}).get("value", "")
            text_content = BeautifulSoup(html_content, 'html.parser').get_text(separator="\n")

            results_data.append({
                'title': title,
                'last_updated': last_updated,
                'views': views,
                'content': text_content,
                'url': content_url
            })

    return results_data

def fetch_confluence_pages(query):
    corrected_query = smart_correct_query(query)
    words = normalize_query(corrected_query)

    if not words:
        return []

    combined_query = build_cql_query(words)
    return search_confluence(combined_query)