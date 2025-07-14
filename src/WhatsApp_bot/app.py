import os
import json
import requests
import time
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime, timedelta
import numpy as np
import time
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
from difflib import get_close_matches
import threading
import tempfile
import shutil

# --- Load Environment Variables ---
load_dotenv()
app = Flask(__name__)

# --- Load Credentials ---
ACCESS_TOKEN         = os.getenv('ACCESS_TOKEN')
VERIFY_TOKEN         = os.getenv('VERIFY_TOKEN')
PHONE_NUMBER_ID      = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
API_BASE_URL         = os.getenv('BACKEND_API_BASE_URL')

# --- In‑memory user state store ---
user_states = {}

# --- Audio snippets (URLs) and crop/category data ---
AUDIO_CLIPS = {
    "welcome":      "https://raw.github.com/debdip4/agrikartwhatsappbot/main/Audio_files/welcome.mp3",
    "en": {
        'ask_name': "https://raw.github.com/debdip4/agrikartwhatsappbot/main/Audio_files/en_ask_name.mp3",
        'ask_address': "https://raw.github.com/debdip4/agrikartwhatsappbot/main/Audio_files/en_ask_address.mp3",
        "ask_state":   "https://raw.github.com/debdip4/agrikartwhatsappbot/main/Audio_files/en_ask_state.mp3",
        'ask_pincode': "https://raw.github.com/debdip4/agrikartwhatsappbot/main/Audio_files/en_ask_pincode.mp3",
        'ask_password': "https://raw.github.com/debdip4/agrikartwhatsappbot/main/Audio_files/en_ask_password.mp3",
        'reg_complete': "https://raw.github.com/debdip4/agrikartwhatsappbot/main/Audio_files/en_reg_complete.mp3",
        'ask_price': "https://raw.github.com/debdip4/agrikartwhatsappbot/main/Audio_files/en_ask_price.mp3",
        'ask_quantity': "https://raw.github.com/debdip4/agrikartwhatsappbot/main/Audio_files/en_ask_quantity.mp3",
        'ask_more_crops': "https://raw.github.com/debdip4/agrikartwhatsappbot/main/Audio_files/en_ask_more_crops.mp3",
        'next_crop': "https://raw.github.com/debdip4/agrikartwhatsappbot/main/Audio_files/en_next_crop.mp3",
        'thank_you': "https://raw.github.com/debdip4/agrikartwhatsappbot/main/Audio_files/en_thank_you.mp3",
        'welcome_back': "https://raw.github.com/debdip4/agrikartwhatsappbot/main/Audio_files/en_welcome_back.mp3",
        'closing': "https://raw.github.com/debdip4/agrikartwhatsappbot/main/Audio_files/en_closing.mp3",
        'ask_loginpassword': "https://raw.github.com/debdip4/agrikartwhatsappbot/main/Audio_files/en_ask_loginpassword.mp3",
        'ask_choice' : "https://raw.github.com/nav-jk/whatsapp/main/Audio_files/en_ask_choice.mp3",
        'ask_location' : "https://raw.github.com/debdip4/agrikartwhatsappbot/main/Audio_files/en_ask_location.mp3",
        'ai_bot_disclaimer' : "https://raw.github.com/nav-jk/whatsapp/main/Audio_files/en_ai_bot_disclaimer.mp3"
    },
    "hi": {  # Hindi clips...
        'ask_name': "https://raw.githubusercontent.com/debdip4/agrikartwhatsappbot/main/Audio_files/hi_ask_name.mp3",
        'ask_address': "https://raw.githubusercontent.com/debdip4/agrikartwhatsappbot/main/Audio_files/hi_ask_address.mp3",
        "ask_state":   "https://raw.githubusercontent.com/debdip4/agrikartwhatsappbot/main/Audio_files/hi_ask_state.mp3",
        'ask_pincode': "https://raw.githubusercontent.com/debdip4/agrikartwhatsappbot/main/Audio_files/hi_ask_pincode.mp3",
        'ask_password': "https://raw.githubusercontent.com/debdip4/agrikartwhatsappbot/main/Audio_files/hi_ask_password.mp3",
        'reg_complete': "https://raw.githubusercontent.com/debdip4/agrikartwhatsappbot/main/Audio_files/hi_reg_complete.mp3",
        'ask_price': "https://raw.githubusercontent.com/debdip4/agrikartwhatsappbot/main/Audio_files/hi_ask_price.mp3",
        'ask_quantity': "https://raw.githubusercontent.com/debdip4/agrikartwhatsappbot/main/Audio_files/hi_ask_quantity.mp3",
        'ask_more_crops': "https://raw.githubusercontent.com/debdip4/agrikartwhatsappbot/main/Audio_files/hi_ask_more_crops.mp3",
        'next_crop': "https://raw.githubusercontent.com/debdip4/agrikartwhatsappbot/main/Audio_files/hi_next_crop.mp3",
        'thank_you': "https://raw.githubusercontent.com/debdip4/agrikartwhatsappbot/main/Audio_files/hi_thank_you.mp3",
        'welcome_back': "https://raw.githubusercontent.com/debdip4/agrikartwhatsappbot/main/Audio_files/hi_welcome_back.mp3",
        'closing': "https://raw.githubusercontent.com/debdip4/agrikartwhatsappbot/main/Audio_files/hi_closing.mp3",
        'ask_loginpassword': "https://raw.githubusercontent.com/debdip4/agrikartwhatsappbot/main/Audio_files/hi_ask_loginpassword.mp3",
        'ask_choice' : "https://raw.github.com/nav-jk/whatsapp/main/Audio_files/hi_ask_choice.mp3",
        'ask_location' : "https://raw.github.com/debdip4/agrikartwhatsappbot/main/Audio_files/hi_ask_location.mp3",
        'ai_bot_disclaimer' : "https://raw.github.com/nav-jk/whatsapp/main/Audio_files/hi_ai_bot_disclaimer.mp3"
    }
}

CROP_CATEGORIES = {
    "en": {"1":"Fruits","2":"Vegetables","3":"Organic","4":"Dairy & Eggs","5":"Grains & Pulses"},
    "hi": {"1":"फल","2":"सब्जियां","3":"जैविक","4":"डेयरी और अंडे","5":"अनाज और दालें"}
}

PRODUCTS_BY_CATEGORY = {
    "Fruits": [
        "Apple", "Mango", "Banana", "Grapes", "Orange", "Pineapple",
        "Papaya", "Guava", "Watermelon", "Pomegranate"
    ],
    "Vegetables": [
        "Potato", "Onion", "Tomato", "Carrot", "Cauliflower", "Brinjal",
        "Spinach", "Cabbage", "Lady Finger", "Beetroot"
    ],
    "Organic": [
        "Organic Honey", "Organic Tea", "Organic Rice", "Organic Turmeric",
        "Organic Jaggery", "Organic Wheat"
    ],
    "Dairy & Eggs": [
        "Milk", "Cheese", "Butter", "Eggs", "Curd", "Paneer", "Ghee"
    ],
    "Grains & Pulses": [
        "Wheat", "Rice", "Maize", "Arhar Dal", "Moong Dal", "Chana Dal",
        "Urad Dal", "Masoor Dal", "Barley", "Bajra"
    ]
}

AGMARKNET_STATES = {
    'Andhra Pradesh': 'AP',
    'Arunachal Pradesh': 'AR',
    'Assam': 'AS',
    'Bihar': 'BR',
    'Chhattisgarh': 'CG',
    'Goa': 'GA',
    'Gujarat': 'GJ',
    'Haryana': 'HR',
    'Himachal Pradesh': 'HP',
    'Jharkhand': 'JH',
    'Karnataka': 'KA',
    'Kerala': 'KL',
    'Madhya Pradesh': 'MP',
    'Maharashtra': 'MH',
    'Manipur': 'MN',
    'Meghalaya': 'ML',
    'Mizoram': 'MZ',
    'Nagaland': 'NL',
    'Odisha': 'OR',
    'Punjab': 'PB',
    'Rajasthan': 'RJ',
    'Sikkim': 'SK',
    'Tamil Nadu': 'TN',
    'Telangana': 'TG',
    'Tripura': 'TR',
    'Uttar Pradesh': 'UP',
    'Uttarakhand': 'UK',
    'West Bengal': 'WB',
    'Andaman and Nicobar Islands': 'AN',
    'Chandigarh': 'CH',
    'Dadra and Nagar Haveli and Daman and Diu': 'DN',
    'Delhi': 'DL',
    'Jammu and Kashmir': 'JK',
    'Ladakh': 'LA',
    'Lakshadweep': 'LD',
    'Puducherry': 'PY'
}

# --- Main Menu Message ---
MAIN_MENU_MSG = (
    "What would you like to do?\n"
    "1️⃣ Place an order\n"
    "2️⃣ Ask a question/doubt\n"
    "3️⃣ Get weather updates\n"
    "Reply with 1, 2, or 3."
)

OPENWEATHER_API_KEY = "82c5f387b8d7068b44aa33ce26bf7cf2"  # Replace with your actual key

def get_weather_forecast(lat, lon, lang='en'):
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()

        if data.get("cod") != "200":
            return " Unable to fetch weather data. Please try again."

        from datetime import datetime
        from collections import defaultdict

        # Group forecasts by day
        daily_forecast = defaultdict(list)
        for entry in data['list']:
            dt = datetime.fromtimestamp(entry['dt'])
            date_key = dt.strftime('%Y-%m-%d')
            daily_forecast[date_key].append(entry)

        # Prepare response for 3 days
        forecast_msg = ""
        days = list(daily_forecast.keys())[:3]

        for day in days:
            entries = daily_forecast[day]
            temps = [e['main']['temp'] for e in entries]
            descriptions = [e['weather'][0]['description'] for e in entries]
            humidities = [e['main']['humidity'] for e in entries]
            winds = [e['wind']['speed'] for e in entries]

            avg_temp = round(sum(temps) / len(temps), 1)
            avg_humidity = round(sum(humidities) / len(humidities))
            avg_wind = round(sum(winds) / len(winds), 1)
            main_desc = max(set(descriptions), key=descriptions.count).capitalize()

            if lang == 'hi':
                forecast_msg += (
                    f"\n📅 *{day}*:\n"
                    f"🌡️ औसत तापमान: {avg_temp}°C\n"
                    f"📋 मौसम: {main_desc}\n"
                    f"💧 नमी: {avg_humidity}%\n"
                    f"🌬️ हवा: {avg_wind} मी/सेक\n"
                )
            else:
                forecast_msg += (
                    f"\n📅 *{day}*:\n"
                    f"🌡️ Avg Temp: {avg_temp}°C\n"
                    f"📋 Condition: {main_desc}\n"
                    f"💧 Humidity: {avg_humidity}%\n"
                    f"🌬️ Wind: {avg_wind} m/s\n"
                )

        if lang == 'hi':
            forecast_msg = "🌤️ *अगले 3 दिनों का मौसम पूर्वानुमान:*" + forecast_msg + \
                "\n\nℹ️ यह जानकारी *AI द्वारा उत्पन्न* की गई है और पूरी तरह सही हो यह आवश्यक नहीं है।\n📞 अधिक जानकारी के लिए कृपया किसान कॉल सेंटर से संपर्क करें।"
        else:
            forecast_msg = "🌤️ *3-Day Weather Forecast:*" + forecast_msg + \
                "\n\nℹ️ This info is *AI-generated* and may not be fully accurate.\n📞 For reliable info, contact Kisan Call Centre."

        return forecast_msg

    except Exception as e:
        return f" Error fetching weather: {str(e)}"

# Helper to run a function in a thread with timeout
def run_with_timeout(func, args=(), kwargs={}, timeout=35):
    result = {}

    def target():
        result['value'] = func(*args, **kwargs)

    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        print(" Timeout reached while waiting for price prediction.")
        return None
    return result.get('value', None)

def sanitize_commodity_name(driver, input_commodity):
    try:
        dropdown = Select(driver.find_element(By.ID, 'ddlCommodity'))
        commodity_options = [option.text.strip() for option in dropdown.options if option.text.strip() and option.text != "--Select--"]
        match = get_close_matches(input_commodity, commodity_options, n=1, cutoff=0.6)
        return match[0] if match else None
    except Exception as e:
        print(f" Error sanitizing commodity name: {e}")
        return None

def scrape_agmarknet_prices(state, commodity):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)
    try:
        driver.get("https://agmarknet.gov.in/SearchCmmMkt.aspx")

        # Close popup if any
        try:
            popup = driver.find_element(By.CLASS_NAME, 'popup-onload')
            close_btn = popup.find_element(By.CLASS_NAME, 'close')
            close_btn.click()
        except NoSuchElementException:
            pass

        # Sanitize commodity
        sanitized_commodity = sanitize_commodity_name(driver, commodity)
        if not sanitized_commodity:
            print(f" No close match found for commodity: '{commodity}'")
            return None

        print(f" Using commodity: {sanitized_commodity}")

        # Select inputs
        Select(driver.find_element(By.ID, 'ddlCommodity')).select_by_visible_text(sanitized_commodity)
        Select(driver.find_element(By.ID, 'ddlState')).select_by_visible_text(state)

        # Wait for markets to load

        # Set Date From and To
        from_date = (datetime.now() - timedelta(days=2)).strftime('%d-%b-%Y')
        to_date = datetime.now().strftime('%d-%b-%Y')

        driver.find_element(By.ID, "txtDate").clear()
        driver.find_element(By.ID, "txtDate").send_keys(from_date)
        driver.find_element(By.ID, "txtToDate").clear()
        driver.find_element(By.ID, "txtToDate").send_keys(to_date)

        # Submit the form
        driver.find_element(By.ID, 'btnGo').click()

        # Wait for table to load
        WebDriverWait(driver, 35).until(EC.presence_of_element_located((By.ID, 'cphBody_GridPriceData')))
        time.sleep(5)  # Sometimes needs extra wait
        driver.execute_script("arguments[0].scrollIntoView();", driver.find_element(By.ID, 'cphBody_GridPriceData'))

        # Scrape the data
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        rows = soup.find_all("tr")
        prices = []

        for row in rows[4:]:  # Skip header rows
            cols = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(cols) >= 11:
                try:
                    modal_price = int(cols[10])  # 11th column: Modal Price (Rs./Quintal)
                    prices.append(modal_price)
                except:
                    continue

        if not prices:
            print(" No prices found.")
            return None

        print(f" {len(prices)} prices found. Sample: {prices[:5]}")

        # Filter and return median
        q1 = np.percentile(prices, 25)
        q3 = np.percentile(prices, 75)
        iqr = q3 - q1
        filtered = [p for p in prices if q1 - 1.5 * iqr <= p <= q3 + 1.5 * iqr]
        predicted = int(np.median(filtered)) if filtered else int(np.median(prices))
        print(f" Predicted price: ₹{predicted} per quintal")
        return predicted

    except Exception as e:
        print(f" Error: {e}")
        return None
    finally:
        driver.quit()

# --- Backend API helpers ---
def check_farmer_exists(phone_number):
    url = f"{API_BASE_URL}/api/v1/farmer/check/{phone_number}/"
    try:
        response = requests.get(url)
        return response.status_code == 200 and response.json().get("exists", False)
    except requests.exceptions.RequestException as e:
        print(f"ERROR checking farmer existence: {e}")
        return False

def register_farmer_api(user_data):
    url = f"{API_BASE_URL}/api/v1/auth/signup/farmer/"
    payload = {
        "username": user_data['username'],
        "password": user_data['password'],
        "email": f"{user_data['username']}@agrikart.ai",
        "phone_number": user_data['phone_number'],
        "name": user_data['name'],
        "address": user_data['address']
    }
    try:
        res = requests.post(url, json=payload)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error in register_farmer_api: {e}")
        return None

def login_farmer_api(username, password):
    url = f"{API_BASE_URL}/api/v1/auth/token/"
    payload = {"username": username, "password": password}
    try:
        res = requests.post(url, json=payload)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error in login_farmer_api: {e}")
        return None
    
def add_produce_api(produce_data, access_token):
    url = f"{API_BASE_URL}/api/v1/produce/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "name": produce_data['name'],
        "price": float(produce_data['price_per_kg']),
        "quantity": float(produce_data['quantity_kg']),
        "category": "Others"
    }
    try:
        res = requests.post(url, headers=headers, json=payload)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error in add_produce_api: {e}")
        return None

# --- WhatsApp senders ---
def send_whatsapp_message(to, msg):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": msg}}
    requests.post(url, headers=headers, json=payload)

def send_whatsapp_audio(to, url_link):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "type": "audio", "audio": {"link": url_link}}
    requests.post(url, headers=headers, json=payload)

# --- Webhook Handler ---
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get('hub.mode') == 'subscribe' and request.args.get('hub.verify_token') == VERIFY_TOKEN:
            return request.args.get('hub.challenge'), 200
        return 'Unauthorized', 403

    data = request.get_json()
    try:
        entry = data.get("entry", [])[0]
        change = entry.get("changes", [])[0]
        value = change.get("value", {})
        messages = value.get("messages")

        if not messages:
            print(" Ignored non-message webhook event")
            return 'OK', 200

        message = messages[0]
        from_number = message['from']
        msg_body = message['text']['body'] if 'text' in message else ''
        command = msg_body.strip().lower()
        msg_audio_url = None
        if message.get("type") == "audio" and "audio" in message:
            media_id = message["audio"]["id"]
            # Step 1: Get media URL using the media ID
            media_url_resp = requests.get(
                f"https://graph.facebook.com/v19.0/{media_id}",
                headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
            )
            if media_url_resp.ok:
                msg_audio_url = media_url_resp.json().get("url")


        print(f" Message from {from_number}: '{command}'")

        # Initialize state if new user
        if from_number not in user_states:
            user_states[from_number] = {"data": {}}

        current_state = user_states[from_number].get("state")
        print(f" Current state for {from_number}: {current_state}")

        # Greeting to start flow
        if command in ['hi', 'hello', 'नमस्ते']:
            print(f" Greeting received from {from_number}. Checking existence...")
            if check_farmer_exists(from_number):
                user_states[from_number]['state'] = 'awaiting_lang_after_exists'
                send_whatsapp_audio(from_number, AUDIO_CLIPS['welcome'])  # Ask language
            else:
                user_states[from_number]['state'] = 'awaiting_language_choice'
                send_whatsapp_audio(from_number, AUDIO_CLIPS['welcome'])
            return 'OK', 200

        # --- State Machine ---
        if current_state == 'awaiting_lang_after_exists':
            lang = 'en' if '1' in command else 'hi'
            user_states[from_number]['language'] = lang
            last_password = user_states[from_number]['data'].get('password')
            if last_password:
                login_resp = login_farmer_api(from_number, last_password)
                if login_resp and login_resp.get('access'):
                    user_states[from_number]['access_token'] = login_resp['access']
                    user_states[from_number]['state'] = 'awaiting_main_menu'
                    send_whatsapp_audio(from_number, AUDIO_CLIPS[lang]['ask_choice'])
                else:
                    send_whatsapp_audio(from_number, AUDIO_CLIPS[lang]['ask_password'])
                    user_states[from_number]['state'] = 'awaiting_password'
            else:
                send_whatsapp_audio(from_number, AUDIO_CLIPS[lang]['ask_loginpassword'])
                user_states[from_number]['state'] = 'awaiting_password'

        elif current_state == 'awaiting_language_choice':
            lang = 'en' if '1' in command else 'hi'
            user_states[from_number]['language'] = lang
            user_states[from_number]['state'] = 'awaiting_name'
            send_whatsapp_audio(from_number, AUDIO_CLIPS[lang]['ask_name'])

        elif current_state == 'awaiting_name':
            lang = user_states[from_number]['language']
            user_states[from_number]['data']['name'] = msg_body
            user_states[from_number]['state'] = 'awaiting_address'
            send_whatsapp_audio(from_number, AUDIO_CLIPS[lang]['ask_address'])

        elif current_state == 'awaiting_address':
            lang = user_states[from_number]['language']
            user_states[from_number]['data']['address'] = msg_body
            user_states[from_number]['state'] = 'awaiting_password'
            send_whatsapp_audio(from_number, AUDIO_CLIPS[lang]['ask_password'])

        elif current_state == 'awaiting_password':
            lang = user_states[from_number]['language']
            user_states[from_number]['data']['password'] = msg_body
            user_states[from_number]['data']['username'] = from_number
            user_states[from_number]['data']['phone_number'] = from_number

            if check_farmer_exists(from_number):
                login_resp = login_farmer_api(from_number, msg_body)
                if login_resp and login_resp.get('access'):
                    user_states[from_number]['access_token'] = login_resp['access']
                    user_states[from_number]['state'] = 'awaiting_main_menu'
                    send_whatsapp_audio(from_number, AUDIO_CLIPS[lang]['ask_choice'])
                else:
                    send_whatsapp_message(from_number, "❌ Wrong password. Please try again.")
            else:
                if register_farmer_api(user_states[from_number]['data']):
                    login_resp = login_farmer_api(from_number, msg_body)
                    if login_resp and login_resp.get('access'):
                        user_states[from_number]['access_token'] = login_resp['access']
                        user_states[from_number]['state'] = 'awaiting_main_menu'
                        send_whatsapp_audio(from_number, AUDIO_CLIPS[lang]['reg_complete'])
                        send_whatsapp_audio(from_number, AUDIO_CLIPS[lang]['ask_choice'])
                    else:
                        send_whatsapp_message(from_number, "❌ Registration failed. Try again with 'hi'.")

        elif current_state == 'awaiting_main_menu':
            if command in ['1', 'order', 'place order']:
                user_states[from_number]['state'] = 'awaiting_crop_name'
                lang = user_states[from_number]['language']
                send_whatsapp_audio(from_number, AUDIO_CLIPS[lang]['welcome_back'])
            elif command in ['2', 'ask', 'doubt', 'question']:
                user_states[from_number]['state'] = 'awaiting_audio_doubt'
                lang = user_states[from_number]['language']
                send_whatsapp_audio(from_number, AUDIO_CLIPS[lang]['ai_bot_disclaimer'])
            elif command in ['3', 'weather']:
                user_states[from_number]['state'] = 'awaiting_weather_location'
                send_whatsapp_audio(from_number, AUDIO_CLIPS[lang]['ask_location'])
            else:
                send_whatsapp_audio(from_number, AUDIO_CLIPS[lang]['ask_choice'])

        elif current_state == 'awaiting_crop_name':
            lang = user_states[from_number]['language']
            crop_name = msg_body.strip()
            user_states[from_number]['temp_produce'] = {'name': crop_name}
            send_whatsapp_message(from_number, f"🔍 Checking market prices for {crop_name}. Please wait...")

            try:
                # This may take 30+ seconds due to agmarknet load times
                predicted_price = scrape_agmarknet_prices("Kerala", crop_name)

                if predicted_price:
                    msg = f" Based on recent market data, the expected price for {crop_name} is ₹{predicted_price} per quintal."
                    send_whatsapp_message(from_number, msg)
                    user_states[from_number]['temp_produce']['predicted_price'] = predicted_price
                else:
                    send_whatsapp_message(from_number, "⚠️ Couldn't predict the price right now. Please enter it manually.")
                    send_whatsapp_audio(from_number, AUDIO_CLIPS[lang]['ask_price'])

            except Exception as e:
                print(f" Error during price prediction: {e}")
                send_whatsapp_message(from_number, "⚠️ Error predicting price. Please enter it manually.")
                send_whatsapp_audio(from_number, AUDIO_CLIPS[lang]['ask_price'])

            user_states[from_number]['state'] = 'awaiting_price'

        elif current_state == 'awaiting_price':
            lang = user_states[from_number]['language']
            user_states[from_number]['temp_produce']['price_per_kg'] = msg_body
            user_states[from_number]['state'] = 'awaiting_quantity'
            send_whatsapp_audio(from_number, AUDIO_CLIPS[lang]['ask_quantity'])

        elif current_state == 'awaiting_quantity':
            lang = user_states[from_number]['language']
            user_states[from_number]['temp_produce']['quantity_kg'] = msg_body
            token = user_states[from_number].get('access_token')
            if token and add_produce_api(user_states[from_number]['temp_produce'], token):
                send_whatsapp_audio(from_number, AUDIO_CLIPS[lang]['ask_more_crops'])
            else:
                send_whatsapp_message(from_number, " Failed to save produce.")
            user_states[from_number]['state'] = 'awaiting_more_crops'

        elif current_state == 'awaiting_more_crops':
            lang = user_states[from_number]['language']
            if command in ['yes', 'y', 'ok', 'हाँ', 'हां']:
                send_whatsapp_audio(from_number, AUDIO_CLIPS[lang]['next_crop'])
                user_states[from_number]['state'] = 'awaiting_crop_name'
            else:
                send_whatsapp_audio(from_number, AUDIO_CLIPS[lang]['thank_you'])
                user_states[from_number]['state'] = 'conversation_over'
                send_whatsapp_message(from_number, MAIN_MENU_MSG)
                user_states[from_number]['state'] = 'awaiting_main_menu'

        elif current_state == 'conversation_over':
            lang = user_states[from_number]['language']
            send_whatsapp_audio(from_number, AUDIO_CLIPS[lang]['closing'])
            send_whatsapp_message(from_number, MAIN_MENU_MSG)
            user_states[from_number]['state'] = 'awaiting_main_menu'

        # --- AUDIO DOUBT HANDLER ---
        elif current_state == 'awaiting_audio_doubt':
            lang = user_states[from_number].get('language', 'en')

            if msg_audio_url:
                try:
                    # Get and save the audio
                    audio_headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
                    audio_resp = requests.get(msg_audio_url, headers=audio_headers)

                    if audio_resp.status_code != 200:
                        raise Exception(f"Failed to fetch audio media. Status: {audio_resp.status_code}")

                    # Save to temp file
                    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as temp_audio:
                        temp_audio.write(audio_resp.content)
                        temp_audio_path = temp_audio.name

                    # Send to voice assistant
                    with open(temp_audio_path, "rb") as f:
                        files = {"file": (os.path.basename(temp_audio_path), f, "audio/ogg")}
                        data = {"lang": lang}
                        chat_resp = requests.post(
                            "http://localhost:8004/chat/",
                            files=files, data=data, timeout=60
                        )

                    if chat_resp.ok:
                        out = chat_resp.json()
                        if out.get("response"):
                            send_whatsapp_message(from_number, out["response"])
                        if out.get("audio_url"):
                            send_whatsapp_audio(from_number, out["audio_url"])
                        else:
                            send_whatsapp_message(from_number, "⚠️ Audio response unavailable.")
                    else:
                        raise Exception(f"Voice Assistant Error: {chat_resp.text}")
                except Exception as e:
                    print(f"❌ Audio doubt processing error: {e}")
                    send_whatsapp_message(from_number, "❌ AI assistant failed. Please try again.")
                finally:
                    if os.path.exists(temp_audio_path):
                        os.remove(temp_audio_path)
            else:
                send_whatsapp_message(from_number, " No voice message found. Please send your doubt as a voice message.")


            # Return to main menu
            user_states[from_number]['state'] = 'awaiting_main_menu'
            send_whatsapp_audio(from_number, AUDIO_CLIPS[lang]['ask_choice'])


        # --- WEATHER HANDLER (SIMPLE) ---
        elif current_state == 'awaiting_weather_location':
            lang = user_states[from_number].get('language', 'en')
            
            if message.get('type') == 'location':
                location = message['location']
                lat = location['latitude']
                lon = location['longitude']
                weather_report = get_weather_forecast(lat, lon, lang)
            else:
                weather_report = (
                    "📍 Please tap the 📎 icon and choose 'Location' to share your live location for the weather forecast."
                    if lang == 'en'
                    else "📍 मौसम जानने के लिए कृपया 📎 आइकन पर टैप करके 'स्थान' भेजें।"
                )

            send_whatsapp_message(from_number, weather_report)
            user_states[from_number]['state'] = 'awaiting_main_menu'
            send_whatsapp_audio(from_number, AUDIO_CLIPS[lang]['ask_choice'])

    except Exception as e:
        print(f" Error in webhook: {e}")

    return 'OK', 200

@app.route('/notify-farmer', methods=['POST'])
def notify_farmer():
    data = request.json
    phone = data.get('phone_number')
    items = data.get('items',[])
    if not phone or not items:
        return jsonify({"error":"Invalid"}),400
    lang = user_states.get(phone,{}).get('language','en')
    lines=[]
    hdr = "🎉 *New Order!*" if lang=='en' else "🎉 *नया ऑर्डर!*"
    lines.append(hdr)
    for it in items:
        if lang=='hi':
            lines.append(f"👉 {it['produce']} | बिक: {it['quantity_bought']}kg | बचे: {it['remaining_stock']}kg")
        else:
            lines.append(f"👉 {it['produce']} | Sold: {it['quantity_bought']}kg | Left: {it['remaining_stock']}kg")
    send_whatsapp_message(phone, "\n".join(lines))
    return jsonify({"status":"notified"}),200

# --- /chat/ ENDPOINT (AUDIO QA PROXY) ---
@app.route('/chat/', methods=['POST'])
def chat():
    if 'file' not in request.files or 'lang' not in request.form:
        return jsonify({'error': 'Missing file or lang'}), 400

    file = request.files['file']
    lang = request.form['lang']

    # Save incoming file to a temp location
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, file.filename)
    file.save(temp_path)

    # Forward to truefoundry endpoint
    files = {'file': open(temp_path, 'rb')}
    data = {'lang': lang}
    try:
        resp = requests.post(
            'http://localhost:8004/chat',
            files=files,
            data=data,
            timeout=60
        )
        resp.raise_for_status()
        output = resp.json()
    except Exception as e:
        shutil.rmtree(temp_dir)
        return jsonify({'error': str(e)}), 500

    # Clean up temp file
    shutil.rmtree(temp_dir)
    return jsonify(output), 200

if __name__ == '__main__':
    print("🚀 WhatsApp Bot Running...")
    # Create static/audio directory if it doesn't exist
    if not os.path.exists('static/audio'):
        os.makedirs('static/audio')
    app.run(port=5000, debug=True)