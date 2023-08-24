import json

import requests


def post_slack_message(text):
    url = 'https://hooks.slack.com/services/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'
    headers = {'Content-Type': 'application/json'}
    data = {'text': text}
    requests.post(url, headers=headers, data=json.dumps(data), verify=False)
