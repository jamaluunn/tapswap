import requests
import json
import time
from colorama import init, Fore, Style
import sys
import os
init(autoreset=True)

with open('init_data.txt', 'r') as file:
    init_data_lines = file.readlines()

with open('content_time.txt', 'r') as file:
    content_time_lines = file.readlines()
# Fungsi untuk login dan mendapatkan token akses serta shares
def get_access_token_and_shares(init_data_line):
    url = "https://api.tapswap.ai/api/account/login"
    headers = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/json",
        "Connection": "keep-alive",
        "Origin": "https://app.tapswap.club",
        "Referer": "https://app.tapswap.club/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "x-app": "tapswap_server",
        "x-cv": "608",
        "x-bot": "no",
    }
    # chr_value, actual_init_data = init_data_line.split('|')
    payload = {
        "init_data": init_data_line,
        "referrer": "",
        "bot_key": "app_bot_0"
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 201:
        data = response.json()
        if 'access_token' in data:
            access_token = data['access_token']
            name = data['player']['full_name']
            coin = data['player']['shares']
            energy = data['player']['energy']
            level_energy = data['player']['energy_level']
            level_charge = data['player']['charge_level']
            level_tap = data['player']['tap_level']
            boosts = data['player']['boost']
            energy_boost = next((b for b in boosts if b["type"] == "energy"), None)
            turbo_boost = next((b for b in boosts if b["type"] == "turbo"), None)
            boost_ready = turbo_boost['cnt']
            energy_ready = energy_boost['cnt']

            print(f"{Fore.BLUE+Style.BRIGHT}\n========================== ")  
            print(f"{Fore.GREEN+Style.BRIGHT}[Nama]: {name}")    
            print(f"{Fore.YELLOW+Style.BRIGHT}[Koin]: {coin}")
            print(f"{Fore.YELLOW+Style.BRIGHT}[Energi]: {energy}")
            print(f"{Fore.CYAN+Style.BRIGHT}[Level Tap]: {level_tap}")
            print(f"{Fore.CYAN+Style.BRIGHT}[Level Energi]: {level_energy}")
            print(f"{Fore.CYAN+Style.BRIGHT}[Level Recharge]: {level_charge}")
            print(f"{Fore.MAGENTA+Style.BRIGHT}[Free Booster] : Energy {energy_boost['cnt']} | Turbo : {turbo_boost['cnt']}")

            return access_token, energy, boost_ready, energy_ready
        else:
            print("Token akses tidak ditemukan dalam respons.")
            return None, None, None, None
    elif response.status_code == 408:
        print("Request Time Out")
    else:
        print(response.json())
        print(f"Gagal mendapatkan token akses, status code: {response.status_code}")
    
    return None, None, None, None
turbo_activated = False    
def apply_turbo_boost(access_token):
    global turbo_activated
    url = "https://api.tapswap.ai/api/player/apply_boost"
    headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Origin": "https://app.tapswap.club",
            "Referer": "https://app.tapswap.club/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "x-app": "tapswap_server",
            "x-cv": "608",
            "x-bot": "no",
            # "Content-Id": content_id
        }

    
    payload = {"type": "turbo"}
    if turbo_activated == False:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 201:

            print(f"\r{Fore.GREEN+Style.BRIGHT}Turbo boost berhasil diaktifkan           ", flush=True)
            turbo_activated = True
            return True

        else:
            print(f"{Fore.RED+Style.BRIGHT}Gagal mengaktifkan turbo boost, status code: {response.json()}")
            return False
    else:
        print(f"\r{Fore.GREEN+Style.BRIGHT}Turbo aktif")
        return True



# Fungsi untuk mengirim taps
def upgrade_level(headers, upgrade_type):
    for i in range(5):
        print(f"\r{Fore.WHITE+Style.BRIGHT}Upgrading {upgrade_type} {'.' * (i % 4)}", end='', flush=True)
    url = "https://api.tapswap.ai/api/player/upgrade"
    payload = {"type": upgrade_type}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        print(f"\r{Fore.GREEN+Style.BRIGHT}Upgrade {upgrade_type} berhasil", flush=True)
        return True
    else:
        response_json = response.json()
        if 'message' in response_json and 'not_enough_shares' in response_json['message']:
            print(f"\r{Fore.RED+Style.BRIGHT}Koin tidak cukup untuk upgrade {upgrade_type}", flush=True)
            return False
        else:
            print(f"\r{Fore.RED+Style.BRIGHT}Error saat upgrade {upgrade_type}: {response_json['message']}", flush=True)
        return False



# Tambahkan input untuk penggunaan booster
use_booster = input("Gunakan booster secara otomatis? (Y/N): ").strip().lower()
if use_booster in ['y', 'n', '']:
    use_booster = use_booster or 'n'
else:
    print("Input tidak valid. Harus 'Y' atau 'N'.")
    sys.exit()


use_upgrade = input("Lakukan upgrade secara otomatis? (Y/N): ").strip().lower()
if use_upgrade in ['y', 'n', '']:
    use_upgrade = use_upgrade or 'n'
else:
    print("Input tidak valid. Harus 'Y' atau 'N'.")
    sys.exit()

# Kemudian, modifikasi fungsi `submit_taps` untuk memperhitungkan input ini
def submit_taps(access_token, energy, boost_ready, energy_ready, content_id, time_stamp, init_data_line):
    global turbo_activated

    while True:
        url = "https://api.tapswap.ai/api/player/submit_taps"

        if use_booster == 'y':
            if boost_ready > 0:
                if turbo_activated == False:
                    print(f"\r{Fore.WHITE+Style.BRIGHT}Turbo boost ready, applying turbo boost", end='', flush=True)
                    apply_turbo_boost(access_token)
                else:
                    print(f"\r{Fore.WHITE+Style.BRIGHT}Turbo aktif", end='', flush=True)
                    
        if energy < 50:
            print(f"\r{Fore.RED+Style.BRIGHT}Low Energy", end='', flush=True)
            if use_booster == 'y':
                if turbo_activated == False:
                # Cek ketersediaan energy boost
                    if energy_ready > 0 :
                        print(f"\r{Fore.WHITE+Style.BRIGHT}Energy boost ready, applying energy boost", end='', flush=True)
                        apply_energy_boost(access_token) 
                        cek_energy = 100
            else:
                time.sleep(3)

                print(f"\r{Fore.RED+Style.BRIGHT}Beralih ke akun selanjutnya", end='', flush=True)
                return
                access_token, energy, boost_ready = get_access_token_and_shares(init_data_line)          
        else:
            print(f"\r{Fore.WHITE+Style.BRIGHT}Tapping ..", end='', flush=True)

        headers = {
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": f"Bearer {access_token}",
            "Connection": "keep-alive",
            "Content-Id": content_id,
            "Content-Type": "application/json",
            "Origin": "https://app.tapswap.club",
            "Referer": "https://app.tapswap.club/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "x-app": "tapswap_server",
            "x-bot": "no",
            "x-cv": "608",
        }

        if turbo_activated == True:
            total_taps = 1000000
            payload = {"taps": total_taps, "time": int(time_stamp)}
        else:
            total_taps = 10000
            payload = {"taps": total_taps, "time": int(time_stamp)}

       

        if turbo_activated == True:
            for _ in range(30):
                response = requests.post(url, headers=headers, json=payload)
                if response.status_code == 201:
                    print(f"\r{Fore.GREEN+Style.BRIGHT}Tapped              ", flush=True)
                else:
                    print(f"\r{Fore.RED+Style.BRIGHT}Gagal mengirim taps, status code: {response.status_code}")
            turbo_activated = False
        else:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 201:
                print(f"\r{Fore.GREEN+Style.BRIGHT}Tapped            ", flush=True)

                if use_upgrade == 'y' :
                    upgrade_level(headers, "tap")
                    upgrade_level(headers, "energy")
                    upgrade_level(headers, "charge")
                cek_energy = response.json().get("player").get("energy")
                if cek_energy < 50:
                    if use_booster == 'y':
                    # Cek ketersediaan energy boost
                        if energy_ready > 0 :
                            print(f"\r{Fore.WHITE+Style.BRIGHT}Energy boost ready, applying energy boost", end='', flush=True)
                            apply_energy_boost(access_token) 
                    print(f"\r{Fore.RED+Style.BRIGHT}Energi rendah, memeriksa akun lain\n", end='', flush=True)
                    return
            else:
                print(f"\n\r{Fore.RED+Style.BRIGHT}Gagal mengirim taps, status code: {response.status_code}")
                print(response.text)

def clear_console():

    # Clear the console based on the operating system
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
def apply_energy_boost(access_token):

    url = "https://api.tapswap.ai/api/player/apply_boost"
    headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Origin": "https://app.tapswap.club",
            "Referer": "https://app.tapswap.club/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "x-app": "tapswap_server",
            "x-cv": "608",
            "x-bot": "no",
        }

    payload = {"type": "energy"}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        print(f"\r{Fore.GREEN+Style.BRIGHT}Energy boost berhasil diaktifkan                 ", flush=True)
        submit_taps(access_token, 100, 0, 0, content_id, time_stamp, init_data_line)  # Anggap energy penuh setelah boost
        return True

    else:
        print(f"{Fore.RED+Style.BRIGHT}Gagal mengaktifkan energy boost, status code: {response.status_code}")
        return False

while True:  # Loop ini akan terus berjalan sampai skrip dihentikan secara manual
    for init_data_line, content_time_line in zip(init_data_lines, content_time_lines):
        content_id, time_stamp = content_time_line.strip().split('|')
        access_token, energy, boost_ready, energy_ready = get_access_token_and_shares(init_data_line.strip())  # Terima energy_boost
        if access_token:
            submit_taps(access_token, energy, boost_ready, energy_ready, content_id, time_stamp, init_data_line.strip())  # Kirim energy_boost ke submit_taps

    print(f"\n\n{Fore.CYAN+Style.BRIGHT}==============Semua akun telah diproses=================\n")
    for detik in range(60, 0, -1):
        print(f"\rMemulai lagi dalam {detik} detik...", end='')
        time.sleep(1)
    clear_console()
