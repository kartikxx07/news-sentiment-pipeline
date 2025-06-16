import pandas as pd
from sqlalchemy import create_engine, text
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from datetime import datetime
import urllib.parse
import os
from dotenv import load_dotenv

engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')
df = pd.read_sql("SELECT * FROM articles", engine)
df['text'] = df['title'].fillna('') + '. ' + df['description'].fillna('') + '. ' + df['content'].fillna('')

model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model=model,
    tokenizer=tokenizer,
    truncation=True,
    max_length=512,
)
texts = df['text'].tolist()
results = sentiment_pipeline(texts)

df['sentiment'] = [res['label'] for res in results]

def map_sentiment(label):
    return {
        "1 star": "very negative",
        "2 stars": "negative",
        "3 stars": "neutral",
        "4 stars": "positive",
        "5 stars": "very positive"
    }.get(label, "unknown")

df['sentiment_label'] = df['sentiment'].apply(map_sentiment)

with engine.connect() as conn:
    for idx, row in df.iterrows():
        update_stmt = text("""
            UPDATE articles
            SET sentiment = :sentiment
            WHERE id = :id
        """)
        conn.execute(update_stmt, {"sentiment": row['sentiment_label'], "id": row['id']})
    conn.commit()

print(f"Updated {len(df)} rows in articles table with sentiment analysis.")
