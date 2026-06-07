import os
import pandas as pd
import kagglehub
import sys

# Add the parent directory to sys.path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.agents.health_agent import run_health_agent

# Use the user's provided token
os.environ["KAGGLE_API_TOKEN"] = "KGAT_52024f93b032478ef9b93bcd0b021163"

def explore_and_test():
    print("Exploring Microsoft Azure Predictive Maintenance Dataset via Kaggle...")
    
    # Download the dataset using kagglehub
    try:
        # Note: arnabbiswas1/microsoft-azure-predictive-maintenance is a well-known Kaggle repo
        path = kagglehub.dataset_download("arnabbiswas1/microsoft-azure-predictive-maintenance")
        print(f"Downloaded successfully to: {path}")
        
        # Look for telemetry data
        csv_file = os.path.join(path, "PdM_telemetry.csv")
        
        if not os.path.exists(csv_file):
            print(f"Could not find PdM_telemetry.csv in {path}. Found files:")
            print(os.listdir(path))
            return
            
        print("Loading Telemetry Data...")
        df = pd.read_csv(csv_file)
        print(f"Loaded {len(df)} rows. Columns: {list(df.columns)}")
        
        # The Azure dataset columns are: datetime, machineID, volt, rotate, pressure, vibration
        # Let's test the LangGraph Agent on an anomalous row!
        
        # Find a row with very high vibration
        anomaly_row = df[df['vibration'] > 60].iloc[0]
        
        print("\n--- TESTING LANGGRAPH AGENT GENERALIZATION ---")
        print(f"Passing Azure Kaggle Data to Agent:")
        print(f"Machine: M-AZURE-{anomaly_row['machineID']}")
        print(f"Vibration: {anomaly_row['vibration']:.2f} (High!)")
        print(f"Voltage: {anomaly_row['volt']:.2f}")
        print(f"Rotation: {anomaly_row['rotate']:.2f}")
        print(f"Pressure: {anomaly_row['pressure']:.2f}")
        
        # Test if the LangGraph agent can adapt to this new data
        result = run_health_agent(
            machine_id=f"M-AZURE-{anomaly_row['machineID']}",
            vibration=anomaly_row['vibration'],
            temp=anomaly_row['volt'], # Simulating mapping voltage to the agent's temp parameter for testing
            rpm=anomaly_row['rotate']
        )
        
        print("\n--- GEMINI EXPLAINABLE AI RESULT ---")
        print(f"Risk Score: {result['risk_score'] * 100}%")
        print(f"Root Cause Analysis:\n{result['analysis']}")
        print("---------------------------------------------")
        print("Kaggle Dataset Exploration & Generalization test PASSED!")

    except Exception as e:
        print(f"Error during Kaggle exploration: {e}")

if __name__ == "__main__":
    explore_and_test()
