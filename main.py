import os
import openai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pytz

def get_openai_recommendations():
    openai.api_key = os.environ["OPENAI_API_KEY"]

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",  # Updated model name
        messages=[
            {"role": "system", "content": "You are a signal-sorting AI trained to find betting and domain market edge."},
            {"role": "user", "content": "Give me top sports bets and expiring domain flips with high ROI today."}
        ],
        temperature=0.7
    )

    return response["choices"][0]["message"]["content"]

def append_to_sheet(content):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
    client = gspread.authorize(creds)

    sheet = client.open("LineWolf Dispatch").sheet1
    est = pytz.timezone("US/Eastern")
    now = datetime.now(est).strftime("%Y-%m-%d %H:%M:%S")

    sheet.append_row([now, content])

if __name__ == "__main__":
    print("⚙️ Polling OpenAI for insights...")
    raw_output = get_openai_recommendations()
    append_to_sheet(raw_output)
    print("✅ Dispatch sent.")

