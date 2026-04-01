import os
import sys
import logging
import json

# Ensure the src directory is in the PYTHONPATH
sys.path.append(os.path.join(os.getcwd(), 'src'))

from wavesync.agents.rectify import rectify

# Setup logging
logging.basicConfig(level=logging.INFO)

def test_pipeline():
    """
    Test the integrated rectification pipeline:
    Legacy Service -> Rectifier -> AWS Architect -> Final Plan
    """
    mock_service = {
        "name": "Auth Service",
        "tech_stack": "Python Flask",
        "database_type": "Local MySQL",
        "dependencies": ["User Service"],
        "priority": 9
    }
    
    print("\n🚀 Starting Integrated Pipeline Test...")
    print(f"Input: {json.dumps(mock_service, indent=2)}\n")
    
    try:
        # Run the full pipeline
        result = rectify(mock_service)
        
        print("\n✅ Pipeline Execution Complete!")
        print("-" * 50)
        print(f"Service Name: {result.get('service_name')}")
        print(f"Status: {result.get('status')}")
        print(f"Cloud Changes: {result.get('cloud_changes')}")
        print(f"AWS Services: {', '.join(result.get('aws_services', []))}")
        
        print("\n🏗️ AWS ARCHITECTURE RECOMMENDATIONS:")
        aws_arc = result.get('aws_architecture', {})
        print(f"  Compute:  {aws_arc.get('compute')}")
        print(f"  Database: {aws_arc.get('database')}")
        print(f"  Storage:  {aws_arc.get('storage')}")
        print(f"  Cache:    {aws_arc.get('cache')}")
        print(f"  Queue:    {aws_arc.get('queue')}")
        print(f"  Notes:    {aws_arc.get('notes')}")
        print("-" * 50)
        
        # Final validation of keys
        required_keys = ["cloud_changes", "aws_services", "aws_architecture"]
        for key in required_keys:
            if key in result and result[key]:
                print(f"VERIFIED: {key} is present and populated.")
            else:
                print(f"❌ ERROR: {key} is missing or empty!")
                
    except Exception as e:
        print(f"❌ TEST FAILED with error: {str(e)}")

if __name__ == "__main__":
    test_pipeline()
