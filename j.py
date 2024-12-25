import os
import re
import uuid
from datetime import datetime
from requests import post, get
from rich.console import Console

# إعداد المظهر والتنسيق
MAGENTA = "\033[1m\033[35m"
CYAN = "\033[1m\033[36m"
RESET = "\033[0m"

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
    console.print(f"""
    {MAGENTA}Instagram Reporting Tool
    {CYAN}Version: Improved
    {RESET}""", style="bold magenta")

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
    url = f"https://i.instagram.com/users/{target_id}/flag/"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cookie": f"sessionid={session_id}",
        "X-CSRFToken": csrf_token,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = f"source_name=&reason_id={report_type}&frx_context="
    while True:
        response = post(url, headers=headers, data=data)
        if response.status_code == 429:
            console.print("[bold red]Rate limited. Please try later.[/bold red]")
            break
        elif response.status_code == 500:
            console.print("[bold red]Target not found.[/bold red]")
            break
        else:
            console.print(f"[bold green]Report sent. Status: {response.status_code}[/bold green]")

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

def main():
    """النقطة الرئيسية لتشغيل البرنامج."""
    header()
    check_date()

    username = input("Enter Instagram username: ")
    password = input("Enter Instagram password: ")
    session_id, csrf_token = login_instagram(username, password)

    target = input("Enter target username: ")
    report_type = get_report_type()
    
    # Fetch target ID
    search_url = f"https://www.instagram.com/{target}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = get(search_url, headers=headers)
    try:
        target_id = re.findall('"profile_id":"(\\d+)"', response.text)[0]
        report_instagram(target_id, session_id, csrf_token, report_type)
    except IndexError:
        console.print("[bold red]Target not found.[/bold red]")

if __name__ == "__main__":
    main()