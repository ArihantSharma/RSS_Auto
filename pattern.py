import re

def match_sub(text):
    pattern = r"([A-Z.!,=+\(\)a-z0-9\s\-]+)\s*-\s*(\d+)\s*"
    match = re.search(pattern, text)
    if match:
        name = str(match.group(1)).strip()
        season_pattern = r"S(\d+)$"
        
        # Find the season number
        s_match = re.search(season_pattern, name)
        if s_match:
            season = s_match.group(1)
            lenS = len(season)
            lenS = int(lenS) + 2
            name = name[:-lenS]
        else:
            season = None
        episode = match.group(2).strip()
        name = name.strip()
    
        return name, episode, season, ""
    else:
        print("No match found.")
        return None, None, None, ""

def match_dub(text):
    dual_pattern = r"^(.*?)\s*S(\d{2})E(\d{2})\s*(.*?)?\s*(?:\d{3,4}p|$)"

    match = re.match(dual_pattern, text)
    if not match:
        return None, None, None, None

    name = match.group(1).strip()  # Anime name
    season = match.group(2)        # Season number
    episode = match.group(3)       # Episode number
    title = match.group(4).strip() if match.group(4) else None  # Episode title (if present)

    return name, episode, season, title
  
