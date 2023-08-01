import requests
import json
import time

DISCORD_WEBHOOK_URL = "webhookgiriniz"

def get_earthquake_data():
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
    response = requests.get(url)
    data = response.json()
    return data['features']

def format_earthquake_message(earthquake):
    properties = earthquake['properties']
    title = properties['title']
    mag = properties['mag']
    place = properties['place']
    time = properties['time']
    url = properties['url']

    message = f"**{title}**\nBüyüklük: {mag}\nYer: {place}\nZaman: {time}\nDaha Fazla Bilgi: {url}"
    return message

def create_discord_embed(earthquake):
    properties = earthquake['properties']
    title = properties['title']
    mag = properties['mag']
    place = properties['place']
    time = properties['time']
    url = properties['url']

    embed = {
        "title": title,
        "description": f"Büyüklük: {mag}\nYer: {place}\nZaman: {time}\nDaha Fazla Bilgi: [Tıklayın]({url})",
        "color": 16729344
    }
    return embed

def is_turkey_earthquake(earthquake, turkey_center=(39.920770, 32.854110), radius=5.0):
    lat, lon = earthquake['geometry']['coordinates'][1], earthquake['geometry']['coordinates'][0]
    turkey_lat, turkey_lon = turkey_center

    from math import radians, sin, cos, sqrt, atan2
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371.0
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c
        return distance

    distance_to_turkey = haversine(lat, lon, turkey_lat, turkey_lon)
    return distance_to_turkey <= radius

def send_discord_message(embed):
    payload = {
        "embeds": [embed]
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(DISCORD_WEBHOOK_URL, data=json.dumps(payload), headers=headers)
    if response.status_code == 204:
        print("Discord mesajı başarıyla gönderildi!")
    else:
        print("Discord mesajı gönderilemedi.")

def main():
    sent_earthquakes = set()
    while True:
        try:
            earthquakes = get_earthquake_data()
            if earthquakes:
                for earthquake in earthquakes:
                    earthquake_id = earthquake['id']
                    if earthquake_id not in sent_earthquakes:
                        is_turkey = is_turkey_earthquake(earthquake)
                        message = format_earthquake_message(earthquake)
                        embed = create_discord_embed(earthquake)
                        send_discord_message(embed)
                        sent_earthquakes.add(earthquake_id)
            time.sleep(5) 
            print("Yenilendi.")
        except Exception as e:
            print("Bir hata oluştu:", e)
            time.sleep(5)

if __name__ == "__main__":
    main()
