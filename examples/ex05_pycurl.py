import json
from io import BytesIO
from urllib.parse import urlencode

import pycurl

# GET: libcurl writes the body into a buffer you own.
buffer = BytesIO()
curl = pycurl.Curl()
curl.setopt(pycurl.URL, "https://quotes.toscrape.com/api/quotes?page=1")
curl.setopt(pycurl.HTTPHEADER, ["accept: application/json", "user-agent: Mozilla/5.0"])
curl.setopt(pycurl.ACCEPT_ENCODING, "")        # the --compressed equivalent
curl.setopt(pycurl.FOLLOWLOCATION, True)       # -L
curl.setopt(pycurl.TIMEOUT, 30)                # --max-time 30
curl.setopt(pycurl.WRITEDATA, buffer)
curl.perform()
status = curl.getinfo(pycurl.RESPONSE_CODE)
print("GET", status, len(json.loads(buffer.getvalue())["quotes"]), "quotes")

# POST: reuse the handle, swap the URL and attach a form body (-d).
buffer = BytesIO()
curl.setopt(pycurl.URL, "https://httpbin.org/post")
curl.setopt(pycurl.POSTFIELDS, urlencode({"field": "value"}))
curl.setopt(pycurl.WRITEDATA, buffer)
curl.perform()
print("POST", curl.getinfo(pycurl.RESPONSE_CODE), json.loads(buffer.getvalue())["form"])
curl.close()
