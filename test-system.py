"""Quick test script to verify EVY system is working."""
import asyncio
import httpx
import time

API_URL = "http://localhost:8000"

async def test_system():
    """Test EVY system functionality."""
    print("🧪 Testing EVY System")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: API Gateway health
        print("\n1️⃣  Testing API Gateway...")
        try:
            response = await client.get(f"{API_URL}/health")
            if response.status_code == 200:
                print("   ✅ API Gateway is healthy")
            else:
                print(f"   ❌ API Gateway returned {response.status_code}")
        except Exception as e:
            print(f"   ❌ Failed to connect: {e}")
            return
        
        # Test 2: Services health
        print("\n2️⃣  Testing all services...")
        try:
            response = await client.get(f"{API_URL}/services/health")
            if response.status_code == 200:
                data = response.json()
                services = data.get('services', {})
                for name, status in services.items():
                    status_emoji = "✅" if status['status'] == 'healthy' else "⚠️"
                    print(f"   {status_emoji} {name}: {status['status']}")
            else:
                print(f"   ❌ Services check returned {response.status_code}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        # Test 3: Send test SMS
        print("\n3️⃣  Testing SMS functionality...")
        test_message = {
            "sender": "+1234567890",
            "receiver": "+1000000000",
            "content": "What is EVY?"
        }
        
        try:
            print("   📤 Sending test message: 'What is EVY?'")
            response = await client.post(
                f"{API_URL}/sms/receive",
                json=test_message
            )
            if response.status_code == 200:
                print("   ✅ Message sent successfully")
                
                # Wait a bit for processing
                print("   ⏳ Waiting for response...")
                await asyncio.sleep(3)
                
                # Check sent messages
                response = await client.get(f"{API_URL}/sms/history")
                if response.status_code == 200:
                    data = response.json()
                    sent = data.get('sent', [])
                    if sent:
                        print(f"   📨 Response received: {sent[-1]['content'][:100]}...")
                    else:
                        print("   ⚠️  No response yet (may need more time)")
            else:
                print(f"   ❌ Failed to send message: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        # Test 4: Knowledge base
        print("\n4️⃣  Testing knowledge base...")
        try:
            response = await client.get(f"{API_URL}/knowledge/stats")
            if response.status_code == 200:
                data = response.json()
                count = data.get('document_count', 0)
                print(f"   ✅ Knowledge base has {count} documents")
            else:
                print(f"   ❌ Failed to get stats: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Testing complete!")
    print("\n💡 Next steps:")
    print("   - Open http://localhost:3000 to access the dashboard")
    print("   - Try sending messages through the UI")
    print("   - Check service health and logs")

if __name__ == "__main__":
    print("\n⏳ Starting tests in 5 seconds...")
    print("   (Make sure services are running with: docker-compose up -d)\n")
    time.sleep(5)
    
    asyncio.run(test_system())


