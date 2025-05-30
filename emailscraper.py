import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, urlunparse
from requests.exceptions import RequestException, SSLError

SOCIAL_MEDIA_DOMAINS = [
    'facebook.com', 'instagram.com', 'twitter.com',
    'linkedin.com', 'tiktok.com', 'youtube.com', 'pinterest.com'
]

def is_social_media_url(url):
    parsed = urlparse(url)
    return any(domain in parsed.netloc for domain in SOCIAL_MEDIA_DOMAINS)

def clean_email(email):
    """
    Extract the clean email from a messy string.
    Returns only the matched email address or None.
    """
    match = re.match(r'^[\w\.-]+@[\w\.-]+\.\w{2,}', email)
    return match.group(0) if match else None

def get_base_url(url):
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, '/', '', '', ''))

def scrape_emails(url, allow_social=False):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    if is_social_media_url(url) and not allow_social:
        print(f"Skipping social media URL: {url}")
        return []

    def try_fetch(u):
        try:
            response = requests.get(u, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except SSLError:
            if u.startswith("https://"):
                fallback = u.replace("https://", "http://", 1)
                print(f"SSL error. Retrying with http: {fallback}")
                try:
                    response = requests.get(fallback, headers=headers, timeout=10)
                    response.raise_for_status()
                    return response.text
                except Exception as e:
                    print(f"Error fetching fallback URL '{fallback}': {e}")
            return None
        except RequestException as e:
            print(f"Error fetching the URL '{u}': {e}")
            return None

    html = try_fetch(url)

    if html is None:
        base_url = get_base_url(url)
        if base_url != url:
            print(f"Retrying with base URL: {base_url}")
            html = try_fetch(base_url)
        if html is None:
            return []

    soup = BeautifulSoup(html, 'html.parser')
    email_addresses = set()

    # --- mailto links ---
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.lower().startswith('mailto:'):
            raw = href.split(':', 1)[1]
            email = clean_email(raw)
            if email:
                email_addresses.add(email)

    # --- extract text-based emails ---
    # This regex grabs longer junky candidates
    candidates = re.findall(r'[\w\.-]+@[\w\.-]+\.\w{2,}[^\s<>"\'\]]*', soup.text)

    for candidate in candidates:
        cleaned = clean_email(candidate)
        if cleaned:
            email_addresses.add(cleaned)

    return list(email_addresses)

def extract_valid_email(email_list):
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    
    # Filter out None or non-string values early
    clean_emails = [e for e in email_list if isinstance(e, str) and e.strip() != '']
    
    if len(clean_emails) == 1:
        # Only one candidate, check if it's valid
        if re.fullmatch(pattern, clean_emails[0]):
            return clean_emails[0]
        else:
            return None
    
    valid_emails = []
    for email in clean_emails:
        matches = re.findall(pattern, email)
        if matches:
            valid_emails.extend(matches)
    
    if valid_emails:
        return min(valid_emails, key=len)
    
    return None

def append_emails(businesses):

    for i in businesses:
        if i["website"] != None:
            
                    
            emails = (scrape_emails(i["website"]))
            
            for j in emails:
                if i["email"][0] == None:
                    i["email"].remove(None)
                if j not in i["email"]:                
                    i["email"].append(j)
    
    
    for i in businesses:
        i["email"] = extract_valid_email(i["email"])
    
    remover = []
    for i in businesses:
        if i["email"] == None:
            remover.append(i)

    for i in remover:
        businesses.remove(i)
            


    return businesses