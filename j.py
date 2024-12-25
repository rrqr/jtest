import os
import re
import uuid
import time
from datetime import datetime
from requests import post, get
from rich.console import Console

UID = str(uuid.uuid4())
console = Console()

def check_date():
    """يتحقق من انتهاء صلاحية الأداة."""
    current_date = datetime.now().date()
    target_date = datetime(2025, 1, 1).date()
    if current_date >= target_date:
        console.print("[bold red]Tool expired. Please renew.[/bold red]")
        exit()

def clear_screen():
    """يمسح الشاشة."""
    os.system("cls" if os.name == 'nt' else "clear")

def header():
    """يعرض عنوان البرنامج."""
    clear_screen()
    console.print("""
    [bold magenta]Instagram Real Reporting Tool[/bold magenta]
    [cyan]Ensure reports are valid and authentic.[/cyan]
    """, style="bold magenta")

def get_report_type():
    """يعرض قائمة أنواع البلاغات ويطلب من المستخدم اختيار واحد."""
    options = [
        "Spam", "Self", "Sale", "Nudity", "Violence",
        "Hate Speech", "Harassment", "Impersonation (Instagram)",
        "Impersonation (Business)", "Copyright", 
        "Impression 3 (Business)", "Impression 3 (Instagram)",
        "Impression 4 (Business)", "Impression 4 (Instagram)", 
        "Violence Type 1"
    ]
    console.print("Choose report type:", style="bold cyan")
    for idx, option in enumerate(options, start=1):
        console.print(f"{idx}. {option}")
    try:
        choice = int(input("Enter your choice (1-15): "))
        if 1 <= choice <= 15:
            return choice
        else:
            console.print("[bold red]Invalid choice. Try again.[/bold red]")
            return get_report_type()
    except ValueError:
        console.print("[bold red]Invalid input. Enter a number.[/bold red]")
        return get_report_type()

def report_instagram(target_id, session_id, csrf_token, report_type):
    """يرسل البلاغ إلى إنستاجرام."""
    url = f"https://i.instagram.com/api/v1/media/{target_id}/flag/"
    headers = {
        "User-Agent": "Instagram 114.0.0.38.120 Android",
        "Cookie": f"sessionid={session_id}; csrftoken={csrf_token}",
        "X-CSRFToken": csrf_token,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "media_id": target_id,
        "reason_id": report_type,
        "source_name": "",
        "frx_context": ""
    }
    response = post(url, headers=headers, data=data)
    if response.status_code == 200 and "ok" in response.text.lower():
        console.print("[bold green]Report successfully submitted![/bold green]")
    elif response.status_code == 429:
        console.print("[bold red]Rate limit reached. Try again later.[/bold red]")
    else:
        console.print(f"[bold red]Failed to submit report. Status: {response.status_code}[/bold red]")

def login_instagram(username, password):
    """يسجل الدخول إلى إنستاجرام."""
    login_url = "https://i.instagram.com/api/v1/accounts/login/"
    headers = {
        "User-Agent": "Instagram 114.0.0.38.120 Android",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "_uuid": UID,
        "password": password,
        "username": username,
        "device_id": UID,
        "from_reg": "false",
        "_csrftoken": "missing",
        "login_attempt_count": "0"
    }
    response = post(login_url, headers=headers, data=data)
    if 'logged_in_user' in response.text:
        console.print("[bold green]Login successful![/bold green]")
        session_id = response.cookies['sessionid']
        csrf_token = response.cookies['csrftoken']
        return session_id, csrf_token
    else:
        console.print("[bold red]Login failed. Check credentials.[/bold red]")
        exit()

def fetch_target_id(username, session_id, csrf_token):
    """يحاول جلب معرف الهدف باستخدام عدة طرق."""
    search_url = f"https://www.instagram.com/{username}/?__a=1&__d=dis"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cookie": f"csrftoken={csrf_token}; sessionid={session_id}"
    }
    response = get(search_url, headers=headers)
    if response.status_code == 200:
        try:
            data = response.json()
            return data['graphql']['user']['id']
        except KeyError:
            console.print("[bold red]Failed to fetch target ID. Please try again.[/bold red]")
            exit()
    else:
        console.print("[bold red]Failed to fetch target ID. Status: {response.status_code}[/bold red]")
        exit()

def main():
    """النقطة الرئيسية لتشغيل البرنامج."""
    header()
    check_date()

    username = input("Enter Instagram username: ")
    password = input("Enter Instagram password: ")
    session_id, csrf_token = login_instagram(username, password)

    target = input("Enter target username: ")
    target_id = fetch_target_id(target, session_id, csrf_token)
    console.print(f"[bold cyan]Target ID: {target_id}[/bold cyan]")

    report_type = get_report_type()
    report_instagram(target_id, session_id, csrf_token, report_type)

    # فاصل زمني لمنع اكتشاف الأداة كروبوت
    time.sleep(5)

if __name__ == "__main__":
    main()
