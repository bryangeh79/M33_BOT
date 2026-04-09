import requests
import sys

def check_token(token):
    print(f"éªŒè¯Token: {token[:15]}...")
    
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                bot = data["result"]
                print(f"âœ… Tokenæœ‰æ•ˆ")
                print(f"   Bot ID: {bot.get('id')}")
                print(f"   ç”¨æˆ·å: @{bot.get('username')}")
                print(f"   åç§°: {bot.get('first_name')}")
                return True
            else:
                print(f"âŒ APIé”™è¯¯: {data.get('description')}")
                return False
        else:
            print(f"âŒ HTTPé”™è¯¯: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"âŒ é”™è¯¯: {e}")
        return False

if __name__ == "__main__":
    token = "8226064460:AAH1dCFD6jmzz-fa3KPbBmdJvvuZtxhH9FM"
    success = check_token(token)
    sys.exit(0 if success else 1)
