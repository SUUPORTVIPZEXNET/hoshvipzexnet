import os
import requests
from rubka import Robot
from rubka.context import Message

bot = Robot(token="توکن")

def download_image(url: str, save_path: str) -> str | None:
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        with open(save_path, "wb") as f:
            f.write(resp.content)
        abs_path = os.path.abspath(save_path)
        print(f"[LOG] تصویر دانلود و ذخیره شد در: {abs_path}")
        return abs_path
    except Exception as e:
        print(f"[❌] خطا در دانلود: {e}")
        return None

@bot.on_message(commands=["پروفایل"])
def handle_start(bot: Robot, message: Message) -> None:
    
    api_endpoint = "https://api-free.ir/api2/enime"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(api_endpoint, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        # انتظار: {"ok": true, "code": 200, ..., "result": "https://download.api-free.ir/....jpg"}
        if not isinstance(data, dict) or not data.get("ok") or int(data.get("code", 0)) != 200 or "result" not in data:
            message.reply("❌ پاسخ نامعتبر از API دریافت شد.")
            return
        image_url = data["result"]
        if not isinstance(image_url, str) or not image_url.startswith("http"):
            message.reply("❌ لینک تصویر معتبر نیست.")
            return
    except Exception as e:
        message.reply(f"❌ خطا در ارتباط با API: {e}")
        return

    local_file = "downloaded_image.jpg"
    abs_path = download_image(image_url, local_file)
    if not abs_path:
        message.reply("❌ خطا در دانلود تصویر.")
        return

    
    message.reply_image(local_file)
    message.reply(f"پروفایل انیمه شما اماده شده.")

    
    try:
        os.remove(local_file)
        print(f"[LOG] فایل محلی حذف شد: {local_file}")
    except Exception as e:
        print(f"[⚠️] حذف فایل محلی ناموفق بود: {e}")
        

@bot.on_message()
def handle(bot, message: Message):
    text = message.text.strip()
    
    if text == "/start":
        message.reply("✨ به ربات هوش مصنوعی خوش آمدید!\nلطفاً پیام خود را ارسال کنید:")
        return
    
    response = requests.get(f"https://hoshi-app.ir/api/chat-gpt.php?text={text}")
    
    if response and response.status_code == 200:
        result = response.json().get("result") or response.json().get("Result")
        reply_text = result if result else "پاسخی دریافت نشد"
    else:
        reply_text = "⚠️ خطا در ارتباط با سرور"
    
    message.reply(reply_text)

bot.run()