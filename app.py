import threading
import asyncio
import aiohttp
import time
from flask import Flask, Response, send_file, render_template, request, redirect, flash
import requests
import xml.etree.ElementTree as ET
import os
from pattern import match_sub

app = Flask(__name__)
app.secret_key = '7372sbjabb8277'


# Uptime Monitoring Configuration
URL_TO_MONITOR = "partial-ilysa-ygen-1a982271.koyeb.app/"  # Change this to your target URL
CHECK_INTERVAL = 360  # Time in seconds between checks



async def check_url():
    """Asynchronously checks if the URL is up."""
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(URL_TO_MONITOR, timeout=10) as response:
                    if response.status == 200:
                        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ✅ {URL_TO_MONITOR} is UP.")
                    else:
                        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ {URL_TO_MONITOR} returned status {response.status}")
            except Exception as e:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ❌ {URL_TO_MONITOR} is DOWN. Error: {e}")

            await asyncio.sleep(CHECK_INTERVAL)

def start_monitoring():
    """Starts the event loop in a separate thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(check_url())

# Start monitoring in a separate thread
monitor_thread = threading.Thread(target=start_monitoring, daemon=True)
monitor_thread.start()

# Flask routes and logic
@app.route('/')
def index():
    return render_template('index.html')



# Directory to save torrent files
TORRENT_DIR = 'torrents'
os.makedirs(TORRENT_DIR, exist_ok=True)


def fetch_and_parse_rss(rss_url, choice):
    response = requests.get(rss_url)
    root = ET.fromstring(response.content)

    # Get the current domain dynamically
    current_domain = request.host_url.rstrip('/') + "/torrents/"

    items = []
    json_url = f"https://raw.githubusercontent.com/voatxm/PublicData/main/sub_rss.json"
    response = requests.get(json_url)
    json_data = response.json()
    
    for item in root.findall(".//item"):
        data = {
            "title": item.find("title").text,
            "link": item.find("link").text,
            "guid": item.find("guid").text,
            "pubDate": item.find("pubDate").text,
            "seeders": item.find("{https://nyaa.si/xmlns/nyaa}seeders").text,
            "leechers": item.find("{https://nyaa.si/xmlns/nyaa}leechers").text,
            "downloads": item.find("{https://nyaa.si/xmlns/nyaa}downloads").text,
            "infoHash": item.find("{https://nyaa.si/xmlns/nyaa}infoHash").text,
            "category": item.find("{https://nyaa.si/xmlns/nyaa}category").text,
            "size": item.find("{https://nyaa.si/xmlns/nyaa}size").text
        }
        data["link"] = data["link"].split("/")[-1]
        data["link"] = current_domain + data["link"]  # Use dynamically fetched domain
        
        if choice == 'sub':
            name, ep, se, title = match_sub(data['title'])
            if not name or not ep:
                continue
            ep = int(ep)
            for dicts in json_data:
                if dicts.get('name').lower() == name.lower():
                    prev_seasons = dicts.get('eps', [])  # List of season episode counts
                    total_prev_eps = sum(prev_seasons)  # Sum all completed seasons
                    
                    if not se:  # If season is not specified in title
                        if ep > total_prev_eps:  # If it's a new season
                            new_ep = ep - total_prev_eps
                            new_season = len(prev_seasons) + 1  # Next season number
                            data['title'] = data['title'].replace(f'- {ep:02}', f'S{new_season} - {new_ep:02}')
                        elif len(prev_seasons) == 0:
                            data['title'] = data['title'].replace(f'- {ep:02}', f'S1 - {ep:02}')
                        else:
                            current_ep = ep
                            season = 1
                            for eps in prev_seasons:
                                if current_ep > eps:
                                    current_ep = current_ep - eps
                                    season += 1
                                else:
                                    break
                            data['title'] = data['title'].replace(f'- {ep:02}', f'S{season} - {current_ep:02}')
                           
                    break  # Stop checking after finding a match
            name, ep, se, title = match_sub(data['title'])
            ep = int(ep)
            if not se:
                data['title'] = data['title'].replace(f'- {ep:02}', f'S1 - {ep:02}')
        items.append(data)

    return {"rss": {"channel": {"item": items[:30]}}}

def download_torrent_file(torrent_url, save_path):
    response = requests.get(torrent_url)
    with open(save_path, 'wb') as file:
        file.write(response.content)

@app.route('/rss/sub')
def show_rss_sub():
    rss_url = "https://nyaa.si/?page=rss&u=SubsPlease&q=1080p"
    rss_data = fetch_and_parse_rss(rss_url, 'sub')

    # Create XML root
    rss = ET.Element("rss")
    channel = ET.SubElement(rss, "channel")

    # Add items to the channel
    for item_data in rss_data["rss"]["channel"]["item"]:
        item = ET.SubElement(channel, "item")
        for key, value in item_data.items():
            sub_element = ET.SubElement(item, key)
            sub_element.text = str(value)

    # Generate XML string with declaration at the top
    xml_content = ET.tostring(rss, encoding="utf-8", method="xml").decode()
    xml_content = f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_content}'

    return Response(xml_content, mimetype='application/xml')

@app.route('/rss/dub')
def show_rss_dub():
    rss_url = "https://nyaa.si/?page=rss&u=varyg1001&q=dual"
    rss_data = fetch_and_parse_rss(rss_url, 'dub')

    rss = ET.Element("rss")
    channel = ET.SubElement(rss, "channel")

    for item_data in rss_data["rss"]["channel"]["item"]:
        item = ET.SubElement(channel, "item")
        for key, value in item_data.items():
            sub_element = ET.SubElement(item, key)
            sub_element.text = str(value)

    xml_content = ET.tostring(rss, encoding="utf-8", method="xml").decode()
    xml_content = f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_content}'

    return Response(xml_content, mimetype='application/xml')
    

@app.route('/torrents/<filename>')
def download_torrent_by_filename(filename):
    torrent_url = f"https://nyaa.si/download/{filename}"
    save_path = os.path.join(TORRENT_DIR, filename)
    download_torrent_file(torrent_url, save_path)
    return send_file(save_path, as_attachment=True)

@app.route('/torrents/<int:file>')
def download_torrent_by_id(file):
    filename = f"{file}.torrent"
    torrent_url = f"https://nyaa.si/download/{file}.torrent"
    save_path = os.path.join(TORRENT_DIR, filename)
    download_torrent_file(torrent_url, save_path)
    return send_file(save_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
