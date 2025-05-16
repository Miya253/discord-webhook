import tkinter as tk
from tkinter import messagebox, scrolledtext
import aiohttp
import asyncio
import json
import os
from dotenv import load_dotenv
import configparser

class DiscordWebhookSender:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Discord Webhook Sender")
        self.root.geometry("500x300")
        self.center_window(self.root)
        self.webhook_url = ""
        self.message_history = []
        self.config_file = "config.ini"
        self.load_config()
        self.setup_main_window()
        load_dotenv()

    def center_window(self, window):
        """Center the window on the screen."""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    def load_config(self):
        """Load the last used webhook URL from config file."""
        self.config = configparser.ConfigParser()
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
            self.webhook_url = self.config.get("Settings", "webhook_url", fallback="")

    def save_config(self):
        """Save the webhook URL to config file."""
        self.config["Settings"] = {"webhook_url": self.webhook_url}
        with open(self.config_file, "w") as configfile:
            self.config.write(configfile)

    def setup_main_window(self):
        """Set up the main window UI."""
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10, fill="both", expand=True)

        tk.Label(frame, text="Enter Discord Webhook URL:").pack(pady=5)
        self.webhook_entry = tk.Entry(frame, width=50)
        self.webhook_entry.insert(0, self.webhook_url)
        self.webhook_entry.pack(pady=5)

        button_frame = tk.Frame(frame)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Verify", command=self.verify_webhook).pack(side="left", padx=5)
        tk.Button(button_frame, text="Clear", command=self.clear_webhook_entry).pack(side="left", padx=5)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def clear_webhook_entry(self):
        """Clear the webhook URL entry field."""
        self.webhook_entry.delete(0, tk.END)

    async def check_webhook_async(self, url):
        """Asynchronously check if the webhook URL is valid."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    return response.status == 200
        except aiohttp.ClientError as e:
            return str(e)

    def verify_webhook(self):
        """Verify the webhook URL."""
        self.webhook_url = self.webhook_entry.get().strip()
        if not self.webhook_url.startswith("https://discord.com/api/webhooks/"):
            messagebox.showerror("Error", "Please enter a valid Discord Webhook URL!")
            return

        # Run the async check in the event loop
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.check_webhook_async(self.webhook_url))

        if result is True:
            self.save_config()
            messagebox.showinfo("Success", "Webhook verified successfully! Proceed to send messages.")
            self.root.withdraw()
            self.open_message_window()
        else:
            messagebox.showerror("Error", f"Invalid webhook: {result if isinstance(result, str) else 'Unable to connect.'}")

    def open_message_window(self):
        """Open the window for sending messages."""
        self.message_window = tk.Toplevel(self.root)
        self.message_window.title("Send Message")
        self.message_window.geometry("500x400")
        self.center_window(self.message_window)

        frame = tk.Frame(self.message_window)
        frame.pack(padx=10, pady=10, fill="both", expand=True)

        tk.Label(frame, text="Enter your message:").pack(pady=5)
        self.message_entry = tk.Entry(frame, width=50)
        self.message_entry.pack(pady=5)

        tk.Label(frame, text="Message History:").pack(pady=5)
        self.history_text = scrolledtext.ScrolledText(frame, height=8, width=50, wrap=tk.WORD, state="disabled")
        self.history_text.pack(pady=5)

        button_frame = tk.Frame(frame)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Send", command=self.send_message).pack(side="left", padx=5)
        tk.Button(button_frame, text="Back", command=self.back_to_main).pack(side="left", padx=5)

        self.message_window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def back_to_main(self):
        """Return to the main window."""
        self.message_window.destroy()
        self.root.deiconify()

    async def send_message_async(self, message):
        """Asynchronously send a message to the webhook."""
        if len(message) > 2000:
            return "Error: Message exceeds Discord's 2000-character limit."

        data = {"content": message}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=data, timeout=5) as response:
                    return response.status, await response.text() if response.status != 204 else ""
        except aiohttp.ClientError as e:
            return 0, str(e)

    def send_message(self):
        """Send the message to the Discord webhook."""
        message = self.message_entry.get().strip()
        if not message:
            messagebox.showwarning("Warning", "Please enter a message!")
            return

        # Run the async send in the event loop
        loop = asyncio.get_event_loop()
        status, response_text = loop.run_until_complete(self.send_message_async(message))

        if status == 204:
            self.message_history.append(message)
            self.update_history()
            messagebox.showinfo("Success", "Message sent successfully!")
            self.message_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", f"Failed to send message. Status: {status}\nResponse: {response_text}")

    def update_history(self):
        """Update the message history display."""
        self.history_text.config(state="normal")
        self.history_text.delete(1.0, tk.END)
        for msg in self.message_history[-5:]:  # Show last 5 messages
            self.history_text.insert(tk.END, f"{msg}\n{'-'*40}\n")
        self.history_text.config(state="disabled")

    def on_closing(self):
        """Handle window closing."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()

    def run(self):
        """Start the application."""
        self.root.mainloop()

if __name__ == "__main__":
    app = DiscordWebhookSender()
    app.run()
