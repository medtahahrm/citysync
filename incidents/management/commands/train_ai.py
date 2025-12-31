import sys
import os

# Add the ai_model directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'ai_model'))

# Now try to import
try:
    from ai_model.training.train_model import ReportClassifierTrainer, create_initial_dataset
    from ai_model.training.preprocess import prepare_dataset
    print("✅ AI module imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Current sys.path:", sys.path)
    
from django.core.management.base import BaseCommand
import pandas as pd
from ai_model.training.train_model import ReportClassifierTrainer, create_initial_dataset
from ai_model.training.preprocess import prepare_dataset

class Command(BaseCommand):
    help = 'Train the AI model for report classification'
    
    def handle(self, *args, **kwargs):
        self.stdout.write("🚀 Starting AI model training...")
        
        # Use initial dataset
        df = create_initial_dataset()
        train_df, val_df = prepare_dataset(df)
        
        # Train model
        trainer = ReportClassifierTrainer()
        model = trainer.train(train_df, val_df)
        
        self.stdout.write(self.style.SUCCESS("✅ AI model training completed!"))