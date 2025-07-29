"""
Test script to verify politeness in RAG responses.
"""
import asyncio
import httpx
from typing import List, Dict, Tuple
import re

# Configuration
BASE_URL = "http://localhost:8000/api/v1"

# Test cases with expected politeness markers
TEST_CASES = [
    {
        "query": "What is the capital of Zyxoria?",
        "checks": [
            "starts_with_polite_phrase",
            "contains_answer",
            "ends_with_closing"
        ]
    },
    {
        "query": "Tell me about something not in the knowledge base",
        "checks": [
            "starts_with_thanks",
            "contains_suggestion",
            "is_apologetic"
        ]
    },
    {
        "query": "How many hearts does an octopus have?",
        "checks": [
            "starts_with_polite_phrase",
            "contains_answer",
            "cites_sources"
        ]
    },
    {
        "query": "",
        "checks": [
            "is_helpful",
            "not_apologetic",
            "suggests_alternatives"
        ]
    }
]

# Politeness check functions
def starts_with_polite_phrase(text: str) -> Tuple[bool, str]:
    polite_starts = [
        "Thank you",
        "I appreciate",
        "That's a great",
        "I'm happy to help",
        "Based on",
        "According to"
    ]
    if any(text.startswith(phrase) for phrase in polite_starts):
        return True, "✓ Starts with a polite phrase"
    return False, f"✗ Should start with a polite phrase like: {', '.join(polite_starts)[:50]}..."

def contains_answer(text: str) -> Tuple[bool, str]:
    if len(text.split()) > 5:  # Simple check for meaningful content
        return True, "✓ Contains a substantive answer"
    return False, "✗ Response seems too short or generic"

def ends_with_closing(text: str) -> Tuple[bool, str]:
    closings = [
        "feel free to ask",
        "don't hesitate",
        "let me know",
        "any other questions"
    ]
    if any(closing in text.lower() for closing in closings):
        return True, "✓ Ends with a friendly closing"
    return False, f"✗ Should end with a friendly closing like: {closings[0]}..."

def starts_with_thanks(text: str) -> Tuple[bool, str]:
    if text.strip().lower().startswith(('thank', 'thanks', 'appreciate')):
        return True, "✓ Starts with thanks/appreciation"
    return False, "✗ Should start with thanks when information isn't found"

def contains_suggestion(text: str) -> Tuple[bool, str]:
    suggestions = [
        "would you like",
        "can i help",
        "would you like me to",
        "could you provide"
    ]
    if any(suggestion in text.lower() for suggestion in suggestions):
        return True, "✓ Includes helpful suggestions"
    return False, "✗ Should include helpful suggestions when information isn't found"

def is_apologetic(text: str) -> Tuple[bool, str]:
    apologies = ["sorry", "apologize", "regret", "unfortunately"]
    if any(apology in text.lower() for apology in apologies):
        return True, "✓ Appropriately apologetic"
    return False, "✗ Should include an apology when information isn't found"

def cites_sources(text: str) -> Tuple[bool, str]:
    if "source" in text.lower() or "according to" in text.lower():
        return True, "✓ Properly cites sources"
    return False, "✗ Should cite sources when providing information"

def is_helpful(text: str) -> Tuple[bool, str]:
    if len(text.split()) > 10:  # Simple check for helpful content
        return True, "✓ Provides helpful information"
    return False, "✗ Should provide helpful guidance"

def not_apologetic(text: str) -> Tuple[bool, str]:
    if not any(word in text.lower() for word in ["sorry", "apologize"]):
        return True, "✓ Doesn't apologize unnecessarily"
    return False, "✗ Shouldn't apologize for empty queries"

def suggests_alternatives(text: str) -> Tuple[bool, str]:
    if "?" in text or "try" in text.lower() or "you can" in text.lower():
        return True, "✓ Suggests alternatives"
    return False, "✗ Should suggest alternatives for empty queries"

# Test runner
async def run_test_case(test_case: Dict) -> Dict:
    """Run a single test case and return results."""
    async with httpx.AsyncClient() as client:
        try:
            # Make the API request
            response = await client.post(
                f"{BASE_URL}/rag/query",
                json={"query": test_case["query"]},
                timeout=10.0
            )
            
            if response.status_code != 200:
                return {
                    "query": test_case["query"],
                    "status": "error",
                    "message": f"API error: {response.status_code} - {response.text}",
                    "checks": []
                }
            
            data = response.json()
            answer = data.get("answer", "")
            
            # Run all checks
            results = []
            for check_name in test_case["checks"]:
                check_func = globals().get(check_name)
                if check_func and callable(check_func):
                    passed, message = check_func(answer)
                    results.append({
                        "check": check_name,
                        "passed": passed,
                        "message": message
                    })
            
            return {
                "query": test_case["query"],
                "status": "success",
                "answer": answer[:200] + ("..." if len(answer) > 200 else ""),
                "checks": results
            }
            
        except Exception as e:
            return {
                "query": test_case["query"],
                "status": "error",
                "message": f"Test failed: {str(e)}",
                "checks": []
            }

async def run_politeness_tests():
    """Run all politeness tests and display results."""
    print("🚀 Running Politeness Tests\n" + "="*50)
    
    results = await asyncio.gather(*[run_test_case(tc) for tc in TEST_CASES])
    
    # Display results
    for i, result in enumerate(results, 1):
        print(f"\n🔍 Test {i}: {result['query']}")
        print("-" * 60)
        
        if result["status"] != "success":
            print(f"❌ {result['status']}: {result.get('message', 'Unknown error')}")
            continue
            
        print(f"💬 Response: {result['answer']}")
        
        # Print check results
        print("\nChecks:")
        for check in result["checks"]:
            status = "✅" if check["passed"] else "❌"
            print(f"  {status} {check['message']}")
        
        print("\n" + "-" * 60)
    
    # Print summary
    total_checks = sum(len(r.get("checks", [])) for r in results)
    passed_checks = sum(c["passed"] for r in results for c in r.get("checks", []))
    
    print(f"\n📊 Summary: {passed_checks}/{total_checks} checks passed ({passed_checks/total_checks*100:.1f}%)")

if __name__ == "__main__":
    asyncio.run(run_politeness_tests())
