import os 
import re
from pathlib import Path
import pandas as pd


def combine_csv(dir):
    selected_cols = ['content', 
                     'region', 
                     'account_category', 
                     'tweet_id', 
                     'language']
    
    all_files = []
    for f in os.listdir(dir):
        if f.startswith('IRAhandle_tweets_') and f.endswith('.csv'):
            all_files.append(f)
    
    combined_df = pd.DataFrame()
    for file in all_files:
        file_path = os.path.join(dir, file)
        df = pd.read_csv(file_path, usecols=selected_cols)
        combined_df = pd.concat([combined_df, df])

    return combined_df

def preprocess_data(text):
    text = re.sub(r'http\S+', '', text) # Remove URLs
    text = re.sub(r'@\S+', '', text)    # Remove mentions
    text = re.sub(r'#\S+', '', text)    # Remove hashtags
    text = re.sub(r'[^A-Za-z\s]', '', text) # Remove special characters and numbers
    text = re.sub(r'\s+', ' ', text).strip()  # Replace multiple spaces with one and strip
    text = text.lower() # Convert to lowercase
    
    return text

def clean_data(df):
    df = df[df['language'] == 'English']
    df = df.dropna(subset=['account_category'])
    df['content'] = df['content'].astype(str).apply(preprocess_data)
    
    # Remove rows where 'content' is empty after data cleaning
    df = df[df['content'].str.len() > 0]

    return df

def save_subsets(df, column, dir):
    categories = df[column].unique()
    for category in categories:
        subset = df[df[column] == category]
        subset.to_csv(os.path.join(dir, f'{category}.csv'), index=False)


if __name__ == '__main__':
    dir = './'
    out_dir = Path('./preprocessed-data')
    out_dir.mkdir(parents=True, exist_ok=True)

    # load and merge all csv
    combined_df = combine_csv(dir)

    # data cleaning
    cleaned_df = clean_data(combined_df)
    cleaned_df.to_csv('./preprocessed-data/all_data_cleaned.csv', index=False)

    # split into subsets based on account_category
    save_subsets(cleaned_df, 'account_category', './preprocessed-data')
