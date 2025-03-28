import requests
import json
import pandas as pd

def sendWebhook(link, df):
    requests.post(link, json=df,headers={"Content-Type": "application/json"})
