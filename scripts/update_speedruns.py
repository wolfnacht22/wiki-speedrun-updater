import requests
import os
import sys
from datetime import datetime

# Configuration - set these as GitHub repository secrets
WIKI_API_URL = os.environ.get('WIKI_API_URL', 'https://your-wiki.wiki.gg/api.php')
WIKI_USERNAME = os.environ.get('WIKI_USERNAME')
WIKI_PASSWORD = os.environ.get('WIKI_PASSWORD')
GAME_ID = os.environ.get('GAME_ID')  # From speedrun.com
CATEGORY_ID = os.environ.get('CATEGORY_ID')  # From speedrun.com
WIKI_PAGE_TITLE = os.environ.get('WIKI_PAGE_TITLE', 'Speedrun_Leaderboards')

def get_speedrun_data():
    """Fetch leaderboard data from speedrun.com API"""
    url = f"https://www.speedrun.com/api/v1/leaderboards/{GAME_ID}/category/{CATEGORY_ID}"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching speedrun data: {e}")
        return None

def format_leaderboard_wikitext(data):
    """Convert speedrun data to MediaWiki table format"""
    if not data or 'data' not in data:
        return "{{notice|Error loading speedrun data}}"
    
    runs = data['data']['runs']
    players = data['data']['players']['data']
    
    # Create player lookup
    player_lookup = {player['id']: player['names']['international'] for player in players}
    
    wikitext = """{{DISPLAYTITLE:Speedrun Leaderboards}}
== Current Leaderboards ==
''Last updated: """ + datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC') + """''

{| class="wikitable sortable"
! Rank !! Player !! Time !! Date !! Video
|-
"""
    
    for i, run in enumerate(runs[:10]):  # Top 10 runs
        rank = i + 1
        player_id = run['run']['players'][0]['id']
        player_name = player_lookup.get(player_id, 'Unknown')
        
        # Format time (seconds to readable format)
        time_seconds = run['run']['times']['primary_t']
        time_formatted = format_time(time_seconds)
        
        # Format date
        date = run['run']['date']
        
        # Video link
        video_link = run['run']['videos']['links'][0]['uri'] if run['run']['videos'] and run['run']['videos']['links'] else ''
        video_cell = f"[{video_link} Video]" if video_link else "No video"
        
        wikitext += f"""|-
| {rank} || {player_name} || {time_formatted} || {date} || {video_cell}
"""
    
    wikitext += "|}\n\n[[Category:Speedrunning]]"
    return wikitext

def format_time(seconds):
    """Convert seconds to H:MM:SS or MM:SS format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"

def login_to_wiki():
    """Login to MediaWiki and get session token"""
    session = requests.Session()
    
    # Get login token
    login_token_params = {
        'action': 'query',
        'meta': 'tokens',
        'type': 'login',
        'format': 'json'
    }
    
    response = session.get(WIKI_API_URL, params=login_token_params)
    login_token = response.json()['query']['tokens']['logintoken']
    
    # Login
    login_params = {
        'action': 'login',
        'lgname': WIKI_USERNAME,
        'lgpassword': WIKI_PASSWORD,
        'lgtoken': login_token,
        'format': 'json'
    }
    
    response = session.post(WIKI_API_URL, data=login_params)
    if response.json()['login']['result'] != 'Success':
        raise Exception(f"Login failed: {response.json()}")
    
    return session

def update_wiki_page(session, title, content):
    """Update a MediaWiki page with new content"""
    # Get edit token
    edit_token_params = {
        'action': 'query',
        'meta': 'tokens',
        'format': 'json'
    }
    
    response = session.get(WIKI_API_URL, params=edit_token_params)
    edit_token = response.json()['query']['tokens']['csrftoken']
    
    # Edit page
    edit_params = {
        'action': 'edit',
        'title': title,
        'text': content,
        'token': edit_token,
        'format': 'json',
        'summary': 'Automated speedrun leaderboard update'
    }
    
    response = session.post(WIKI_API_URL, data=edit_params)
    result = response.json()
    
    if 'edit' in result and result['edit']['result'] == 'Success':
        print(f"Successfully updated page: {title}")
    else:
        print(f"Failed to update page: {result}")
        sys.exit(1)

def main():
    """Main execution function"""
    print("Starting speedrun leaderboard update...")
    
    # Validate environment variables
    required_vars = ['WIKI_USERNAME', 'WIKI_PASSWORD', 'GAME_ID', 'CATEGORY_ID']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"Missing required environment variables: {missing_vars}")
        sys.exit(1)
    
    # Fetch speedrun data
    speedrun_data = get_speedrun_data()
    if not speedrun_data:
        print("Failed to fetch speedrun data")
        sys.exit(1)
    
    # Format as wikitext
    wikitext = format_leaderboard_wikitext(speedrun_data)
    
    # Login to wiki
    try:
        session = login_to_wiki()
        print("Successfully logged into wiki")
    except Exception as e:
        print(f"Failed to login to wiki: {e}")
        sys.exit(1)
    
    # Update wiki page
    update_wiki_page(session, WIKI_PAGE_TITLE, wikitext)
    print("Speedrun leaderboard update completed!")

if __name__ == "__main__":
    main()
