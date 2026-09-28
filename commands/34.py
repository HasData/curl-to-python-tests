import requests

headers = {
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/151.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

params = {
    '__cf_chl_rt_tk': 'hMAWTuD.Tq0qn_3x1tW5YCHuIkY08bbK2f8dsAxa7WI-1787705003-1.0.1.1-qym0p7.1ejkbihtzARxnvYO8uvSUGBmvZLUT.F8MXHI',
}

response = requests.get('https://www.producthunt.com/', params=params, headers=headers)
