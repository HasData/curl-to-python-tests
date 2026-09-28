from curl_cffi import requests

# Same call shape as requests, plus impersonate=: curl_cffi sends Chrome's TLS and HTTP/2
# fingerprint, which is what a converted curl command loses on the way to plain requests.
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.9",
}
response = requests.get("https://tls.browserleaks.com/json", headers=headers, impersonate="chrome", timeout=30)
report = response.json()
print(response.status_code, "| JA4:", report.get("ja4"), "| HTTP/2 fingerprint:", report.get("akamai_hash"))
print("user-agent sent:", report.get("user_agent"))
