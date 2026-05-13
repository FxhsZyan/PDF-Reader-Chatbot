import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import threading
from chatbot import PDFChatBot

bot = PDFChatBot()

# ── Palette ───────────────────────────────────────────────────────────────────
BG        = "#0F1117"
SURFACE   = "#1C1E2A"
BORDER    = "#2A2D3E"
ACCENT    = "#6C63FF"
TEXT      = "#E8EAED"
TEXT_DIM  = "#7A7F9A"
USER_CLR  = "#6C63FF"
BOT_CLR   = "#00D9A3"
DANGER    = "#FF4757"
FONT_BODY = ("Segoe UI", 12)
FONT_BOLD = ("Segoe UI", 12, "bold")
FONT_SM   = ("Segoe UI", 10)
FONT_LG   = ("Segoe UI", 15, "bold")


def append_message(sender: str, message: str, color: str):
    chat_display.config(state=tk.NORMAL)
    tag = f"tag_{sender.replace(' ', '_')}"
    chat_display.tag_configure(tag, foreground=color, font=FONT_BOLD)
    chat_display.insert(tk.END, f"  {sender}\n", tag)
    chat_display.insert(tk.END, f"  {message}\n\n")
    chat_display.config(state=tk.DISABLED)
    chat_display.see(tk.END)


def _set_status(text: str, color: str):
    status_label.config(text=text, fg=color)


def upload_pdf():
    file_path = filedialog.askopenfilename(
        title="Select a PDF File",
        filetypes=[("PDF Files", "*.pdf")]
    )
    if not file_path:
        return
    upload_btn.config(state=tk.DISABLED, text="Reading…")
    _set_status("📖  Reading PDF — please wait…", TEXT_DIM)

    def do_upload():
        success, message = bot.upload_pdf(file_path)
        if success:
            fname  = file_path.replace("\\", "/").split("/")[-1]
            chunks = len(bot.pdf_chunks)
            _set_status(f"✅  {fname}  ({chunks} chunks)", BOT_CLR)
            append_message(
                "Assistant",
                f"'{fname}' loaded! {chunks} sections indexed.\n"
                "Ask me anything about the document.",
                BOT_CLR
            )
        else:
            _set_status("❌  Failed to load PDF", DANGER)
            append_message("Assistant", f"Error: {message}", DANGER)
        upload_btn.config(state=tk.NORMAL, text="📂  Upload PDF")

    threading.Thread(target=do_upload, daemon=True).start()


def send_message(event=None):
    user_input = input_field.get().strip()
    if not user_input:
        return
    if not bot.pdf_chunks:
        messagebox.showwarning("No PDF", "Please upload a PDF file first!")
        return
    input_field.delete(0, tk.END)
    send_btn.config(state=tk.DISABLED)
    append_message("You", user_input, USER_CLR)
    _set_status("⏳  Thinking…", TEXT_DIM)

    def call_api():
        reply = bot.send_message(user_input)
        append_message("Assistant", reply, BOT_CLR)
        send_btn.config(state=tk.NORMAL)
        _set_status("✅  Ready", BOT_CLR)

    threading.Thread(target=call_api, daemon=True).start()


def clear_chat():
    bot.clear_chat()
    chat_display.config(state=tk.NORMAL)
    chat_display.delete(1.0, tk.END)
    chat_display.config(state=tk.DISABLED)
    _set_status("No PDF loaded", TEXT_DIM)
    append_message("Assistant", "Chat cleared! Upload a PDF to get started.", BOT_CLR)


# ═══════════════════════════════════════════════════════════════════════════════
#  BUILD WINDOW
# ═══════════════════════════════════════════════════════════════════════════════
window = tk.Tk()
window.title("PDF Chat — Groq ⚡")
window.geometry("900x660")
window.configure(bg=BG)
window.resizable(True, True)

# ── Header ────────────────────────────────────────────────────────────────────
header = tk.Frame(window, bg=SURFACE)
header.pack(fill=tk.X)

logo_frame = tk.Frame(header, bg=SURFACE)
logo_frame.pack(side=tk.LEFT, padx=18, pady=12)
tk.Label(logo_frame, text="⚡", font=("Segoe UI", 22), bg=SURFACE, fg=ACCENT).pack(side=tk.LEFT)
tk.Label(logo_frame, text="  PDF Chat", font=FONT_LG, bg=SURFACE, fg=TEXT).pack(side=tk.LEFT)
tk.Label(logo_frame, text="  powered by Groq", font=FONT_SM, bg=SURFACE, fg=TEXT_DIM).pack(side=tk.LEFT)

upload_btn = tk.Button(
    header, text="📂  Upload PDF", font=FONT_BOLD,
    bg=ACCENT, fg="white", activebackground="#5652D8", activeforeground="white",
    relief=tk.FLAT, cursor="hand2", padx=18, pady=8, command=upload_pdf
)
upload_btn.pack(side=tk.RIGHT, padx=18, pady=10)

# ── Status ────────────────────────────────────────────────────────────────────
tk.Frame(window, bg=BORDER, height=1).pack(fill=tk.X)
status_frame = tk.Frame(window, bg=BG, pady=4)
status_frame.pack(fill=tk.X, padx=16)
status_label = tk.Label(status_frame, text="No PDF loaded", font=FONT_SM, bg=BG, fg=TEXT_DIM, anchor="w")
status_label.pack(side=tk.LEFT)

# ── Chat ──────────────────────────────────────────────────────────────────────
chat_display = scrolledtext.ScrolledText(
    window, state=tk.DISABLED, wrap=tk.WORD,
    font=("Segoe UI", 12), bg=SURFACE, fg=TEXT,
    insertbackground=TEXT, selectbackground=ACCENT,
    relief=tk.FLAT, padx=14, pady=14, spacing3=2, bd=0
)
chat_display.pack(fill=tk.BOTH, expand=True, padx=12, pady=(4, 0))

# ── Input ─────────────────────────────────────────────────────────────────────
tk.Frame(window, bg=BORDER, height=1).pack(fill=tk.X, padx=12)
bottom = tk.Frame(window, bg=BG, pady=10)
bottom.pack(fill=tk.X, padx=12)

input_frame = tk.Frame(bottom, bg=SURFACE, padx=8, pady=6)
input_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
input_field = tk.Entry(input_frame, font=FONT_BODY, bg=SURFACE, fg=TEXT, insertbackground=TEXT, relief=tk.FLAT, bd=0)
input_field.pack(fill=tk.X, ipady=4, padx=4)
input_field.bind("<Return>", send_message)
tk.Frame(input_frame, bg=ACCENT, height=2).pack(fill=tk.X)

send_btn = tk.Button(
    bottom, text="Send  ➤", font=FONT_BOLD,
    bg=ACCENT, fg="white", activebackground="#5652D8", activeforeground="white",
    relief=tk.FLAT, cursor="hand2", padx=18, pady=8, command=send_message
)
send_btn.pack(side=tk.LEFT, padx=(8, 4))

clear_btn = tk.Button(
    bottom, text="Clear", font=FONT_BOLD,
    bg=SURFACE, fg=DANGER, activebackground=BORDER, activeforeground=DANGER,
    relief=tk.FLAT, cursor="hand2", padx=14, pady=8, command=clear_chat
)
clear_btn.pack(side=tk.LEFT)

# ── Welcome ───────────────────────────────────────────────────────────────────
append_message(
    "Assistant",
    "Hello! I'm your PDF assistant powered by Groq ⚡\n"
    "Upload any PDF and I'll index the FULL document — no article limits.\n"
    "Then ask me anything about it.",
    BOT_CLR
)

window.mainloop()