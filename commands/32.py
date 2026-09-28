import requests

headers = {
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/151.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

params = {
    '__cf_chl_rt_tk': 'vIan64P8kbjeeFWzzIhPO98KTZPV5E2Xe53pVNUAxo4-1787704991-1.0.1.1-RoI6O6sOe9BLHLRA6jVMl95ip1UmieEFBaYAujgu7lQ',
}

response = requests.get('https://stackoverflow.com/questions', params=params, headers=headers)
