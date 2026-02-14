import asyncio
import httpx
import time
import uuid

# Configuration
BASE_URL = "http://localhost:8000/api"
FORM_SLUG = "feedback"  # Update this to a slug that exists in your local DB
CONCURRENT_USERS = 20
TOTAL_REQUESTS = 100

async def submit_response(client, user_id):
    """Simulate a single form submission"""
    payload = {
        "form_id": "8908865e-2f22-4a00-9833-2882f082e012", # Update with real ID
        "answers": {
            "q1": f"User {user_id} feedback at {time.time()}",
            "q2": "Extremely satisfied"
        }
    }
    try:
        start = time.time()
        response = await client.post(f"/f/{FORM_SLUG}/submit", json=payload)
        end = time.time()
        return response.status_code, end - start
    except Exception as e:
        return 500, 0

async def run_load_test():
    """Run concurrent load test"""
    print(f"Starting load test on {BASE_URL}...")
    print(f"Concurrent Users: {CONCURRENT_USERS}, Total Requests: {TOTAL_REQUESTS}")
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        tasks = []
        for i in range(TOTAL_REQUESTS):
            tasks.append(submit_response(client, i))
            if len(tasks) >= CONCURRENT_USERS:
                results = await asyncio.gather(*tasks)
                tasks = []
        
        if tasks:
            results.extend(await asyncio.gather(*tasks))
            
    # Analyze results
    successes = [r for r in results if r[0] == 200]
    latencies = [r[1] for r in results if r[0] == 200]
    
    print("\n--- Load Test Results ---")
    print(f"Total Requests: {TOTAL_REQUESTS}")
    print(f"Success Rate: {len(successes)}/{TOTAL_REQUESTS} ({len(successes)/TOTAL_REQUESTS*100:.1f}%)")
    if latencies:
        print(f"Avg Latency: {sum(latencies)/len(latencies):.3f}s")
        print(f"Max Latency: {max(latencies):.3f}s")
        print(f"Min Latency: {min(latencies):.3f}s")

if __name__ == "__main__":
    asyncio.run(run_load_test())
