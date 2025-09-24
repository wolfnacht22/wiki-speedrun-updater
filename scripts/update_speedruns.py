import requests
import os
import sys
from datetime import datetime

WIKI_API_URL = os.environ.get('WIKI_API_URL', 'https://your-wiki.wiki.gg/api.php')
WIKI_USERNAME = os.environ.get('WIKI_USERNAME')
WIKI_PASSWORD = os.environ.get('WIKI_PASSWORD')
GAME_ID = os.environ.get('GAME_ID')
CATEGORY_ID = os.environ.get('CATEGORY_ID')
WIKI_PAGE_TITLE = os.environ.get('WIKI_PAGE_TITLE', 'Speedrun_Leaderboards')

def get_speedrun_data():
    url = f"https://www.speedrun.com/api/v1/leaderboards/{GAME_ID}/category/{CATEGORY_ID}"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching speedrun data: {e}")
        return None

def format_leaderboard_wikitext(data):
    if not data or 'data' not in data:
        return "{{notice|Error loading speedrun data}}"
    
    runs = data['data']['runs']
    
    player_lookup = {}
    if 'players' in data['data'] and 'data' in data['data']['players']:
        players = data['data']['players']['data']
        player_lookup = {player['id']: player['names']['international'] for player in players}
    
    wikitext = """❗ NOTE: Due to CORS restrictions, the proper API cannot be utilized. As a result, entries on this page must be updated manually. For the most up-to-date information on speedrun times, please visit [https://www.speedrun.com/Abyssus_ speedrun.com].<br>
[[File:Discord_Icon.png|20x20px|link=https://discord.gg/z9KA7jSyFv]] Visit the official Abyssus Speedrunning Discord here: [https://discord.gg/z9KA7jSyFv Abyssus Speedrunning].

''Last updated: """ + datetime.utcnow().strftime('%m-%d') + """''

<div style="display: flex; gap: 10px; flex-wrap: wrap;">

<div style="flex: 1; min-width: 300px;">
=== Solo DW 0 ===
{| class="wikitable" style="width:100%; background-color:#1A1A1A;"
! style="background-color:#059669; color:white; text-align:center;" colspan="6" | Solo | DW 0
|-
! style="background-color:#2C3539; color:white; width:8%;" | #
! style="background-color:#2C3539; color:white; width:35%;" | Player
! style="background-color:#2C3539; color:white; width:15%;" | IGT
! style="background-color:#2C3539; color:white; width:15%;" | Time
! style="background-color:#2C3539; color:white; width:12%;" | Date
! style="background-color:#2C3539; color:white; width:15%;" | Video
|-
"""
    
    for i, run in enumerate(runs[:10]):
        rank = i + 1
        
        if run['run']['players']:
            player_data = run['run']['players'][0]
            if 'id' in player_data:
                player_id = player_data['id']
                player_name = player_lookup.get(player_id, 'Unknown')
            elif 'name' in player_data:
                player_name = player_data['name']
            else:
                player_name = 'Unknown'
        else:
            player_name = 'Unknown'
        
        igt_seconds = run['run']['times']['ingame_t'] if 'ingame_t' in run['run']['times'] and run['run']['times']['ingame_t'] else run['run']['times']['primary_t']
        time_seconds = run['run']['times']['primary_t']
        igt_formatted = format_time_short(igt_seconds)
        time_formatted = format_time_short(time_seconds)
        
        date_formatted = run['run']['date'][5:]
        
        video_link = ''
        if run['run']['videos'] and run['run']['videos']['links']:
            video_link = run['run']['videos']['links'][0]['uri']
        video_cell = f"[{video_link} Video]" if video_link else ""
        
        bg_color = "#1A1A1A" if rank % 2 == 1 else "#2C3539"
        
        wikitext += f"""|-
| style="background-color:{bg_color}; color:white; text-align:center; font-weight:bold;" | {rank}
| style="background-color:{bg_color}; color:white; font-weight:bold;" | {player_name}
| style="background-color:{bg_color}; color:white; font-family:monospace;" | {igt_formatted}
| style="background-color:{bg_color}; color:white; font-family:monospace;" | {time_formatted}
| style="background-color:{bg_color}; color:white;" | {date_formatted}
| style="background-color:{bg_color}; color:white;" | {video_cell}
"""
    
    wikitext += """|}
</div>

<div style="flex: 1; min-width: 300px;">
=== Solo All Bosses DW 0 ===
{| class="wikitable" style="width:100%; background-color:#1A1A1A;"
! style="background-color:#059669; color:white; text-align:center;" colspan="6" | Solo | All Bosses | DW 0
|-
! style="background-color:#2C3539; color:white; width:8%;" | #
! style="background-color:#2C3539; color:white; width:35%;" | Player
! style="background-color:#2C3539; color:white; width:15%;" | IGT
! style="background-color:#2C3539; color:white; width:15%;" | Time
! style="background-color:#2C3539; color:white; width:12%;" | Date
! style="background-color:#2C3539; color:white; width:15%;" | Video
|-
| style="background-color:#1A1A1A; color:white; text-align:center; font-weight:bold;" | 1
| style="background-color:#1A1A1A; color:white; font-weight:bold;" | Placeholder
| style="background-color:#1A1A1A; color:white; font-family:monospace;" | --
| style="background-color:#1A1A1A; color:white; font-family:monospace;" | --
| style="background-color:#1A1A1A; color:white;" | --
| style="background-color:#1A1A1A; color:white;" | 
|-
|}
</div>

<div style="flex: 1; min-width: 300px;">
=== Duo DW 0 ===
{| class="wikitable" style="width:100%; background-color:#1A1A1A;"
! style="background-color:#059669; color:white; text-align:center;" colspan="6" | Duo | DW 0
|-
! style="background-color:#2C3539; color:white; width:8%;" | #
! style="background-color:#2C3539; color:white; width:35%;" | Player
! style="background-color:#2C3539; color:white; width:15%;" | IGT
! style="background-color:#2C3539; color:white; width:15%;" | Time
! style="background-color:#2C3539; color:white; width:12%;" | Date
! style="background-color:#2C3539; color:white; width:15%;" | Video
|-
| style="background-color:#1A1A1A; color:white; text-align:center; font-weight:bold;" | 1
| style="background-color:#1A1A1A; color:white; font-weight:bold;" | Placeholder
| style="background-color:#1A1A1A; color:white; font-family:monospace;" | --
| style="background-color:#1A1A1A; color:white; font-family:monospace;" | --
| style="background-color:#1A1A1A; color:white;" | --
| style="background-color:#1A1A1A; color:white;" | 
|-
|}
</div>

</div>

[[Category:Speedrunning]]"""
    return wikitext

def format_time_short(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}m {secs:02d}s"

def login_to_wiki():
    session = requests.Session()
    
    login_token_params = {
        'action': 'query',
        'meta': 'tokens',
        'type': 'login',
        'format': 'json'
    }
    
    response = session.get(WIKI_API_URL, params=login_token_params)
    login_token = response.json()['query']['tokens']['logintoken']
    
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
    edit_token_params = {
        'action': 'query',
        'meta': 'tokens',
        'format': 'json'
    }
    
    response = session.get(WIKI_API_URL, params=edit_token_params)
    edit_token = response.json()['query']['tokens']['csrftoken']
    
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
    print("Starting speedrun leaderboard update...")
    
    required_vars = ['WIKI_USERNAME', 'WIKI_PASSWORD', 'GAME_ID', 'CATEGORY_ID']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"Missing required environment variables: {missing_vars}")
        sys.exit(1)
    
    speedrun_data = get_speedrun_data()
    if not speedrun_data:
        print("Failed to fetch speedrun data")
        sys.exit(1)
    
    wikitext = format_leaderboard_wikitext(speedrun_data)
    
    try:
        session = login_to_wiki()
        print("Successfully logged into wiki")
    except Exception as e:
        print(f"Failed to login to wiki: {e}")
        sys.exit(1)
    
    update_wiki_page(session, WIKI_PAGE_TITLE, wikitext)
    print("Speedrun leaderboard update completed!")

if __name__ == "__main__":
    main()
