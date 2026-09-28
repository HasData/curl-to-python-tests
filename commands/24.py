import requests

headers = {
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/151.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

params = {
    'd': 'ssd',
    '__cf_chl_rt_tk': 't65xKR8pscxQKY02ftascUR7LyeuEdeQZN93.MAxTP4-1787704923-1.0.1.1-NeMKzjgm8d2_FQydBAHsUT5KwpUCgDUfPSkix5KXfYA',
}

response = requests.get('https://www.newegg.com/p/pl', params=params, headers=headers)
