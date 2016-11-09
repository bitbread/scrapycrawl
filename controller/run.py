# coding: utf-8

import requests

data = dict(
    project='crawl',
    spider='sina_globalnews_realtime'
)

url = 'http://localhost:6800/schedule.json'

req = requests.post(url, data=data)
print req.content
