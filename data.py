import requests
from dotenv import load_dotenv
import os
load_dotenv()

tenant_id = os.getenv("TENANT_ID")
tenant_name = os.getenv("TENANT_NAME")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
site_name = os.getenv("SITE_NAME")



def access_token(client_id, tenant_id, client_secret):
    # Define the headers
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    payload = { 
                'grant_type': 'client_credentials',
                'client_id': client_id,
                'client_secret': client_secret,
                'scope': 'https://graph.microsoft.com/.default'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get("access_token")


def site_id(tenant_name, site_name, access_token):
    url = f"https://graph.microsoft.com/v1.0/sites/{tenant_name}.sharepoint.com:/sites/{site_name}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.request("GET", url, headers=headers)
    return response.json().get("id").split(",")[1]

def drive_id(site_id, access_token):
    url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/Drive"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.request("GET", url, headers=headers)
    return response.json().get("id")

def fetch_items(drive_id, access_token, folder):
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{folder}:/children"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.request("GET", url, headers=headers)
    return response.json().get("value")

def download_file(url, destination_path):
    try:
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        
        with requests.get(url, stream=True) as response:
            response.raise_for_status() 
            with open(destination_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
        print(f"File downloaded successfully to {destination_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")



access_token = access_token(client_id, tenant_id, client_secret)
site_id = site_id(tenant_name, site_name, access_token)
drive_id = drive_id(site_id, access_token)

folder = 'Presentations'
fetch_data = fetch_items(drive_id, access_token, folder)
download_url,download_filename = fetch_data[1].get("@microsoft.graph.downloadUrl"), fetch_data[1].get("name")
download_file(download_url, f"./downloads/{download_filename}")
