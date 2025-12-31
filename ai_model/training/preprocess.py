import pandas as pd
import re
from sklearn.model_selection import train_test_split

def clean_text(text):
    """Clean and preprocess report text"""
    if not isinstance(text, str):
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and extra spaces
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def prepare_dataset(reports_df, text_column='report_text', label_column='urgency'):
    """
    Prepare dataset for training
    Expected columns: report_text, urgency (0=not urgent, 1=urgent)
    """
    # Clean text
    reports_df['cleaned_text'] = reports_df[text_column].apply(clean_text)
    
    # Filter out empty texts
    reports_df = reports_df[reports_df['cleaned_text'].str.len() > 10]
    
    # Split data
    train_df, val_df = train_test_split(
        reports_df, 
        test_size=0.2, 
        random_state=42,
        stratify=reports_df[label_column]
    )
    
    return train_df, val_df