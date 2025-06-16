import json
import urllib.request
import urllib.parse
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values  
import os
from dotenv import load_dotenv

query = "DonaldTrump"
encoded_query = urllib.parse.quote(query)
url = f"https://gnews.io/api/v4/search?q={encoded_query}&lang=en&country=us&max=10&apikey={apikey}"

data = []  # <-- must be a list
print("Type of data before loop:", type(data))

with urllib.request.urlopen(url) as response:
    response_data = json.loads(response.read().decode("utf-8"))
    articles = response_data.get("articles", [])

    for article in articles:
        data.append({
            'title': article.get('title'),
            'description': article.get('description'),
            'content': article.get('content'),
        })

print("Collected articles:", len(data))

df = pd.DataFrame(data)

user = "postgres"
password = "kartik@1123"
host = "localhost"
port = "5432"
database = "news_sentiment"

# Connect to DB
conn = psycopg2.connect(
    user=user,
    password=password,
    host=host,
    port=port,
    database=database
)
cur = conn.cursor()


records = [
    (row['title'], row['description'], row['content']) 
    for _, row in df.iterrows()
]


insert_query = """
INSERT INTO articles (title, description, content)
VALUES %s
"""

# Bulk insert
execute_values(cur, insert_query, records)

# Commit and close
conn.commit()
cur.close()
conn.close()

print(f"Inserted {len(records)} rows successfully!")

