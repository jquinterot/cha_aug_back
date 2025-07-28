import sys
import requests
from bs4 import BeautifulSoup

# Set a proper User-Agent to avoid being blocked
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def test_wow_leaderboard():
    """Test loading World of Warcraft leaderboard data."""
    url = "http://worldofwarcraft.blizzard.com/en-us/game/pvp/leaderboards/3v3"
    
    print(f"Testing URL: {url}")
    print("=" * 80)
    
    try:
        # Try to fetch the page
        print("\nAttempting to fetch the page...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        print(f"Status Code: {response.status_code}")
        print(f"Content Type: {response.headers.get('content-type')}")
        
        # Check if this is the actual leaderboard page or a login/JS-required page
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for common elements that would indicate the leaderboard is loaded
        leaderboard = soup.find('div', {'class': 'Leaderboard'}) or soup.find('table', {'class': 'leaderboard'})
        
        if leaderboard:
            print("\nFound leaderboard content!")
            print("-" * 50)
            print(leaderboard.get_text(separator='\n', strip=True)[:500] + "...")
        else:
            print("\nCould not find leaderboard data. This page might require JavaScript to load the content.")
            print("\nPage title:", soup.title.string if soup.title else "No title found")
            
            # Check for common elements that indicate a login or JS requirement
            if any(term in response.text.lower() for term in ['enable javascript', 'login', 'sign in']):
                print("\nThis page may require JavaScript to be enabled or authentication.")
            
            # Save the response for inspection
            with open('wow_leaderboard_response.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("\nFull response saved to 'wow_leaderboard_response.html'")
            
    except requests.exceptions.RequestException as e:
        print(f"\nError fetching the URL: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_wow_leaderboard()
