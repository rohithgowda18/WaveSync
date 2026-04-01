"""
WaveSync AI — Member 3 Pipeline Test
Independent verification of the AI Cloud Rectification pipeline.
"""

from wavesync.agents.member3_pipeline import generate_cloud_plan

def test_ai_rectification():
    """Manual test for a single service transformation."""
    mock_payload = {
        "name": "postgresql-main",
        "tech_stack": "PostgreSQL 14",
        "database_type": "postgresql"
    }
    
    print(f"🧠 Testing AI Transformation for: {mock_payload['name']}...")
    try:
        plan = generate_cloud_plan(mock_payload)
        print(f"✅ Success! AWS Compute: {plan['compute']}")
        print(f"📊 Risk Score: {plan['risk_score']}")
    except Exception as e:
        print(f"❌ Transformation Failed: {str(e)}")

if __name__ == "__main__":
    test_ai_rectification()
