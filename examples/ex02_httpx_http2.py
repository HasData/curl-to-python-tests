import httpx

# curl 'https://quotes.toscrape.com/api/quotes?page=1' --http2 --compressed -H 'accept: application/json'
# requests speaks HTTP/1.1 only. For --http2, use httpx with the h2 extra: pip install 'httpx[http2]'
headers = {"accept": "application/json", "user-agent": "Mozilla/5.0"}

with httpx.Client(http2=True, headers=headers, follow_redirects=True, timeout=30) as client:
    response = client.get("https://quotes.toscrape.com/api/quotes", params={"page": 1})
    print(response.status_code, response.http_version, len(response.json()["quotes"]), "quotes")
    # httpx follows redirects only when asked, the same default as curl without -L.
    plain = client.get("https://quotes.toscrape.com/random")
    print(plain.status_code, plain.http_version, len(plain.text), "bytes of HTML")
