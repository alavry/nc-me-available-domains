import os
import requests
from http.cookies import SimpleCookie
import urllib.parse
from urllib.parse import urlparse
import time

# Config
START_LENGTH = 5
END_LENGTH = 18
WORDLIST_URL = "https://github.com/dwyl/english-words/raw/master/words_alpha.txt"
REQUEST_DELAY_MS = 0


def download_wordlist(url):
    try:
        filename = os.path.basename(urlparse(url).path)
        response = requests.get(url)
        response.raise_for_status()
        with open(filename, "w") as file:
            file.write(response.text)
        return filename
    except Exception as e:
        print(f"Error while downloading wordlist: {e}")


def load_words(filename):
    try:
        with open(filename, "r") as file:
            return [line.strip().lower() for line in file]
    except Exception as e:
        print(f"Error occurred while loading words from file: {e}")


def get_csrf_token_and_cookies():
    try:
        with requests.Session() as session:
            response = session.get("https://nc.me")
            response.raise_for_status()
            raw_cookies = response.headers.get("Set-Cookie")
            cookie = SimpleCookie()
            cookie.load(raw_cookies)
            csrf_token = urllib.parse.unquote(cookie["XSRF-TOKEN"].value)
            return csrf_token, session.cookies
    except Exception as e:
        print(f"Error occurred while getting CSRF token: {e}")


def check_domain_availability(word, headers, cookies):
    domain = word[:-2]
    try:
        url = "https://nc.me/api/search"
        data = {"term": domain}
        response = requests.post(url, headers=headers, json=data, cookies=cookies)
        response.raise_for_status()
        result = response.json()
        return result["domains"][0]["available"]
    except Exception as e:
        print(f"Error checking domain {domain}: {e}")
        return False


def main():
    try:
        if not (5 <= START_LENGTH <= 32 and 5 <= END_LENGTH <= 32):
            print("START_LENGTH and END_LENGTH must be between 5 and 32 characters.")
            return

        if START_LENGTH > END_LENGTH:
            print("START_LENGTH cannot be greater than END_LENGTH.")
            return

        filename = download_wordlist(WORDLIST_URL)
        if not filename:
            print("Failed to download wordlist.")
            return

        words = load_words(filename)
        if not words:
            print("Failed to load words.")
            return

        csrf_token, cookies = get_csrf_token_and_cookies()
        if not csrf_token:
            print("Failed to get CSRF token.")
            return

        headers = {"X-XSRF-TOKEN": csrf_token}

        for total_length in range(START_LENGTH, END_LENGTH + 1):
            print(f"Checking domains with length: {total_length}")
            for word in words:
                if len(word) == total_length and word.endswith("me"):
                    if check_domain_availability(word, headers, cookies):
                        print(f"Domain available: {word}.me")
                    else:
                        print(f"Not available: {word}.me")
                    if REQUEST_DELAY_MS > 0:
                        time.sleep(REQUEST_DELAY_MS / 1000.0)
    except KeyboardInterrupt:
        return


if __name__ == "__main__":
    main()
