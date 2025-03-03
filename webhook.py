import requests
import tkinter as tk
from tkinter import messagebox

def check_webhook():
    global webhook_url
    webhook_url = webhook_entry.get()
    
    if not webhook_url.startswith("https://discord.com/api/webhooks/"):
        messagebox.showerror("錯誤", "請輸入有效的 Discord Webhook URL！")
        return
    
    response = requests.get(webhook_url)
    if response.status_code == 200:
        messagebox.showinfo("成功", "Webhook 驗證成功！請輸入要發送的訊息。")
        root.withdraw()
        open_message_window()
    else:
        messagebox.showerror("錯誤", "Webhook 無效，請確認網址是否正確！")

def send_message():
    message = message_entry.get()
    
    if not message:
        messagebox.showwarning("警告", "請輸入訊息！")
        return
    
    data = {"content": message}
    response = requests.post(webhook_url, json=data)

    if response.status_code == 204:
        messagebox.showinfo("成功", "訊息發送成功！")
    else:
        messagebox.showerror("錯誤", f"發送失敗，狀態碼: {response.status_code}\n回應: {response.text}")

def open_message_window():
    global message_entry
    message_window = tk.Toplevel(root)
    message_window.title("發送訊息")
    message_window.geometry("400x200")

    tk.Label(message_window, text="請輸入要發送的訊息：").pack(pady=10)
    
    message_entry = tk.Entry(message_window, width=40)
    message_entry.pack(pady=5)
    
    send_button = tk.Button(message_window, text="發送", command=send_message)
    send_button.pack(pady=10)

root = tk.Tk()
root.title("Discord Webhook 發送器")
root.geometry("400x200")

tk.Label(root, text="請輸入 Discord Webhook URL：").pack(pady=10)

webhook_entry = tk.Entry(root, width=50)
webhook_entry.pack(pady=5)

check_button = tk.Button(root, text="確認", command=check_webhook)
check_button.pack(pady=10)

root.mainloop()
