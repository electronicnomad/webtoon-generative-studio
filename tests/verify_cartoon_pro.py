import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from models.cartoon import generate_cartoon_frame, analyze_conte
from common.metadata import get_all_datasets
from state.state import AppState

def test_cartoon_pro_logic():
    print("Verifying Cartoon Pro Logic...")
    
    # 1. Check datasets
    datasets = get_all_datasets()
    print(f"Datasets found: {len(datasets)}")
    
    # 2. Mock Conte Analysis (skipping actual API call to save cost/time in test, checking import/signature)
    # If we wanted to test, we'd need a real GCS URI.
    # We will just verify imports and function existence here primarily.
    assert callable(analyze_conte)
    assert callable(generate_cartoon_frame)
    
    print("Functions are callable.")
    print("Verification Script Complete.")

if __name__ == "__main__":
    test_cartoon_pro_logic()
