import pandas as pd
from sqlalchemy import create_engine, text
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from datetime import datetime
import urllib.parse

# Database connection info
user = "postgres"
password = urllib.parse.quote("kartik@1123")
host = "localhost"
port = "5432"
database = "news_sentiment"

engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')

# Step 2: Load articles from DB
df = pd.read_sql("SELECT * FROM articles", engine)

# Combine text fields for sentiment analysis
df['text'] = df['title'].fillna('') + '. ' + df['description'].fillna('') + '. ' + df['content'].fillna('')

# Load sentiment model & pipeline
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

# Step 3: Run sentiment analysis on all combined text
texts = df['text'].tolist()
results = sentiment_pipeline(texts)

df['sentiment'] = [res['label'] for res in results]

# Step 4: Map model labels to custom sentiment labels
def map_sentiment(label):
    return {
        "1 star": "very negative",
        "2 stars": "negative",
        "3 stars": "neutral",
        "4 stars": "positive",
        "5 stars": "very positive"
    }.get(label, "unknown")

df['sentiment_label'] = df['sentiment'].apply(map_sentiment)

# Step 5: Update sentiment column in the database row by row
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
