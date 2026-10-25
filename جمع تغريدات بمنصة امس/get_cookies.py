import browser_cookie3
import json

def extract_twitter_cookies():
    try:
        # Load cookies from Chrome
        cj = browser_cookie3.chrome(domain_name='.twitter.com')
        cj_x = browser_cookie3.chrome(domain_name='.x.com')
        
        cookies_list = []
        for cookie in cj:
            cookies_list.append({
                "name": cookie.name,
                "value": cookie.value,
                "domain": cookie.domain,
                "path": cookie.path,
                "expires": cookie.expires if cookie.expires else -1,
                "httpOnly": cookie.has_nonstandard_attr('HttpOnly'),
                "secure": cookie.secure,
                "sameSite": "Lax"
            })
        for cookie in cj_x:
            cookies_list.append({
                "name": cookie.name,
                "value": cookie.value,
                "domain": cookie.domain,
                "path": cookie.path,
                "expires": cookie.expires if cookie.expires else -1,
                "httpOnly": cookie.has_nonstandard_attr('HttpOnly'),
                "secure": cookie.secure,
                "sameSite": "Lax"
            })
            
        if not cookies_list:
            print("لم يتم العثور على ملفات تعريف ارتباط (كوكيز) لتويتر في متصفح كروم.")
            return False

        storage_state = {
            "cookies": cookies_list,
            "origins": []
        }
        
        with open("twitter_auth.json", "w", encoding="utf-8") as f:
            json.dump(storage_state, f, indent=4)
        
        print(f"تم بنجاح سحب الكوكيز من متصفحك العادي! تم حفظ {len(cookies_list)} كوكي.")
        return True
    except Exception as e:
        print(f"حدث خطأ أثناء سحب الكوكيز: {e}")
        return False

if __name__ == "__main__":
    extract_twitter_cookies()
