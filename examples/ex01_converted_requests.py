import requests

# The command DevTools copied, translated flag by flag:
#   curl 'https://quotes.toscrape.com/api/quotes?page=2' \
#     -H 'accept: application/json, text/javascript, */*; q=0.01' \
#     -H 'accept-language: en-US,en;q=0.9' \
#     -H 'referer: https://quotes.toscrape.com/scroll' \
#     -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36' \
#     -H 'x-requested-with: XMLHttpRequest' \
#     --compressed
headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "en-US,en;q=0.9",
    "referer": "https://quotes.toscrape.com/scroll",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}
# The URL's query string becomes params=, and --compressed needs no counterpart:
# requests asks for gzip and deflate on its own and decompresses the body.
response = requests.get("https://quotes.toscrape.com/api/quotes", params={"page": 2}, headers=headers, timeout=30)
response.raise_for_status()
data = response.json()
print(response.status_code, len(data["quotes"]), "quotes, has_next =", data["has_next"])
print(data["quotes"][0]["author"]["name"], "-", data["quotes"][0]["text"][:50])
