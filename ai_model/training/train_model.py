import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.optim import AdamW  # FIXED IMPORT
from transformers import AutoModelForSequenceClassification
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import pandas as pd
import numpy as np
from tqdm import tqdm
import os

def create_initial_dataset():
    """Create MUCH better training data"""
    data = {
        'report_text': [
            # 🔥 EXTREME URGENT - FIRE & LIFE-THREATENING (URGENT = 1)
            'MASSIVE FIRE in building! People trapped, cannot breathe! Send help NOW!',
            'BUILDING ON FIRE with people inside! Smoke everywhere, need fire department IMMEDIATELY!',
            'HOUSE FIRE with children trapped! Flames visible, screaming heard!',
            'EXPLOSION followed by fire! Multiple casualties, building collapsing!',
            'GAS LEAK and fire! Strong smell, danger of explosion! Evacuate area!',
            
            # 🚑 MEDICAL EMERGENCIES (URGENT = 1)
            'HEART ATTACK! Person collapsed, not breathing! Need ambulance URGENT!',
            'CAR ACCIDENT with serious injuries! People trapped in vehicles!',
            'CHILD DROWNING in pool! Not breathing, need CPR immediately!',
            'ACTIVE SHOOTER situation! Multiple gunshot victims!',
            'PERSON HAVING SEIZURE! Unconscious, need medical help!',
            
            # 🚨 OTHER EMERGENCIES (URGENT = 1)
            'EARTHQUAKE! Building collapse, people under rubble!',
            'TORNADO touchdown! Houses destroyed, injuries reported!',
            'FLOOD with people on roofs! Water rising fast!',
            'CHEMICAL SPILL! Toxic fumes, people coughing!',
            'POWER LINES DOWN and sparking! Danger of electrocution!',
            
            # ⚠️ SERIOUS BUT LESS URGENT (URGENT = 1)
            'Gas smell in building, not sure of source',
            'Car accident, minor injuries only',
            'Water pipe burst, flooding basement',
            'Tree fallen on car, no injuries',
            'Power outage in neighborhood',
            
            # 🟢 NOT URGENT (URGENT = 0)
            'Street light not working for a week',
            'Garbage not collected on schedule',
            'Noisy party late at night',
            'Pothole on the road needs fixing',
            'Graffiti on public wall',
            
            # 🟡 VERY NOT URGENT (URGENT = 0)
            'Park bench needs painting',
            'Slow internet connection',
            'Dog barking occasionally',
            'Lawn not mowed',
            'Public toilet needs cleaning',
        ],
        'urgency': [
            1, 1, 1, 1, 1,    # Extreme fire emergencies
            1, 1, 1, 1, 1,    # Medical emergencies
            1, 1, 1, 1, 1,    # Other emergencies
            1, 1, 1, 1, 1,    # Serious issues
            0, 0, 0, 0, 0,    # Not urgent
            0, 0, 0, 0, 0,    # Very not urgent
        ]
    }
    
    return pd.DataFrame(data)
class ReportClassifierTrainer:
    def __init__(self, model_name='bert-base-uncased', num_labels=2):
        self.model_name = model_name
        self.num_labels = num_labels
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    def train(self, train_df, val_df, output_dir='ai_model/models'):
        """Train the model BETTER"""
        
        # Increase epochs for better learning
        num_epochs = 5  # Changed from 2 to 5
        
        # Later in training loop, add:
        print(f"Training on {len(train_df)} examples")
        print(f"Validating on {len(val_df)} examples")
        
        # Train for more epochs
        for epoch in range(num_epochs):
            # ... existing training code ...
        
        # Create datasets
            from .dataset import ReportDataset
        
        train_dataset = ReportDataset(
            train_df['cleaned_text'].tolist(),
            train_df['urgency'].tolist(),
            tokenizer_name=self.model_name
        )
        
        val_dataset = ReportDataset(
            val_df['cleaned_text'].tolist(),
            val_df['urgency'].tolist(),
            tokenizer_name=self.model_name
        )
        
        # Create data loaders
        train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)  # Smaller batch
        val_loader = DataLoader(val_dataset, batch_size=8, shuffle=False)
        
        # Initialize model
        print("Loading model...")
        model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=self.num_labels
        )
        model.to(self.device)
        
        # Optimizer - FIXED: using torch.optim.AdamW
        optimizer = AdamW(model.parameters(), lr=2e-5)
        
        # Training loop
        num_epochs = 2  # Start with 2 epochs
        best_accuracy = 0
        
        print(f"Starting training for {num_epochs} epochs...")
        
        for epoch in range(num_epochs):
            print(f"\nEpoch {epoch+1}/{num_epochs}")
            
            # Training
            model.train()
            train_loss = 0
            train_progress = tqdm(train_loader, desc="Training", leave=False)
            
            for batch in train_progress:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                optimizer.zero_grad()
                outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
                loss = outputs.loss
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
                train_progress.set_postfix({'loss': loss.item()})
            
            # Validation
            model.eval()
            val_predictions = []
            val_true_labels = []
            
            with torch.no_grad():
                val_progress = tqdm(val_loader, desc="Validation", leave=False)
                for batch in val_progress:
                    input_ids = batch['input_ids'].to(self.device)
                    attention_mask = batch['attention_mask'].to(self.device)
                    labels = batch['labels'].to(self.device)
                    
                    outputs = model(input_ids, attention_mask=attention_mask)
                    predictions = torch.argmax(outputs.logits, dim=1)
                    
                    val_predictions.extend(predictions.cpu().numpy())
                    val_true_labels.extend(labels.cpu().numpy())
            
            # Calculate metrics
            accuracy = accuracy_score(val_true_labels, val_predictions)
            precision, recall, f1, _ = precision_recall_fscore_support(
                val_true_labels, val_predictions, average='binary', zero_division=0
            )
            
            print(f"Validation Accuracy: {accuracy:.4f}")
            print(f"Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}")
            
            # Save best model
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                os.makedirs(output_dir, exist_ok=True)
                model.save_pretrained(output_dir)
                print(f"Model saved to {output_dir}")
        
        print(f"\nBest Accuracy: {best_accuracy:.4f}")
        return model

# Simple test if run directly
if __name__ == "__main__":
    print("Testing training module...")
    df = create_initial_dataset()
    
    # Simple preprocessing for test
    df['cleaned_text'] = df['report_text'].str.lower()
    
    # Split manually for test
    train_df = df.iloc[:8]
    val_df = df.iloc[8:]
    
    trainer = ReportClassifierTrainer()
    model = trainer.train(train_df, val_df)
    print("Test completed!")