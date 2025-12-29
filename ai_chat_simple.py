"""
Simple AI Chat Tool - Professional Interface
Supports streaming output, token counting, API configuration
"""

import customtkinter as ctk
import threading
import os
import re
import datetime
from api_client import APIClient
from prompts import get_system_prompt


class CodeBlock(ctk.CTkFrame):
    """Collapsible code block with copy button - shows 5 lines by default"""
    
    def __init__(self, parent, code, language="", **kwargs):
        super().__init__(parent, fg_color="#1e1e2e", corner_radius=6, **kwargs)
        
        self.code = code
        self.is_expanded = False
        self.lines = code.split('\n')
        self.total_lines = len(self.lines)
        
        # Header
        self.header = ctk.CTkFrame(self, fg_color="#2d2d3d", corner_radius=6)
        self.header.pack(fill="x", padx=2, pady=2)
        
        lang_text = language if language else "code"
        ctk.CTkLabel(self.header, text=f"📄 {lang_text} ({self.total_lines} lines)",
            font=("Arial", 10), text_color="#888888").pack(side="left", padx=8, pady=4)
        
        # Copy button
        self.copy_btn = ctk.CTkButton(self.header, text="Copy", width=50, height=22,
            font=("Arial", 9), fg_color="#444466", hover_color="#555577", command=self.copy_code)
        self.copy_btn.pack(side="right", padx=4, pady=4)
        
        # Expand button (only if more than 5 lines)
        if self.total_lines > 5:
            self.toggle_btn = ctk.CTkButton(self.header, text=f"▶ +{self.total_lines - 5} lines",
                width=80, height=22, font=("Arial", 9), fg_color="#3a7ca5", 
                hover_color="#2d6a8f", command=self.toggle_expand)
            self.toggle_btn.pack(side="right", padx=2, pady=4)
        
        # Code display - show first 5 lines
        self.code_frame = ctk.CTkFrame(self, fg_color="#0d0d1a", corner_radius=4)
        self.code_frame.pack(fill="x", padx=2, pady=(0, 2))
        
        preview_code = '\n'.join(self.lines[:5]) if self.total_lines > 5 else code
        self.code_text = ctk.CTkTextbox(self.code_frame, font=("Consolas", 10),
            fg_color="transparent", text_color="#e0e0e0",
            height=min(90, self.total_lines * 18), wrap="none")
        self.code_text.pack(fill="x", padx=4, pady=4)
        self.code_text.insert("1.0", preview_code)
        self.code_text.configure(state="disabled")
    
    def toggle_expand(self):
        if self.is_expanded:
            # Collapse - show 5 lines
            self.code_text.configure(state="normal")
            self.code_text.delete("1.0", "end")
            self.code_text.insert("1.0", '\n'.join(self.lines[:5]))
            self.code_text.configure(state="disabled", height=90)
            self.toggle_btn.configure(text=f"▶ +{self.total_lines - 5} lines")
            self.is_expanded = False
        else:
            # Expand - show all
            self.code_text.configure(state="normal")
            self.code_text.delete("1.0", "end")
            self.code_text.insert("1.0", self.code)
            self.code_text.configure(state="disabled", height=min(300, self.total_lines * 18))
            self.toggle_btn.configure(text="▼ Collapse")
            self.is_expanded = True
    
    def copy_code(self):
        self.clipboard_clear()
        self.clipboard_append(self.code)
        self.copy_btn.configure(text="✓")
        self.after(1000, lambda: self.copy_btn.configure(text="Copy"))


class APIConfigDialog(ctk.CTkToplevel):
    """API Configuration Dialog"""

    def __init__(self, parent, on_save_callback):
        super().__init__(parent)
        self.title("API Settings")
        self.geometry("500x420")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.on_save = on_save_callback
        self.env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
        
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 500) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 420) // 2
        self.geometry(f"+{x}+{y}")
        
        self.create_widgets()
        self.load_config()

    def create_widgets(self):
        ctk.CTkLabel(self, text="⚙️ API Configuration", font=("Arial", 18, "bold")).pack(pady=(20, 15))

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=10)

        ctk.CTkLabel(content, text="API Base URL", anchor="w").pack(fill="x", pady=(0, 5))
        self.url_entry = ctk.CTkEntry(content, height=35)
        self.url_entry.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(content, text="API Key", anchor="w").pack(fill="x", pady=(0, 5))
        self.key_entry = ctk.CTkEntry(content, height=35, show="*")
        self.key_entry.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(content, text="Model Name", anchor="w").pack(fill="x", pady=(0, 5))
        self.model_entry = ctk.CTkEntry(content, height=35)
        self.model_entry.pack(fill="x", pady=(0, 15))

        self.status = ctk.CTkLabel(content, text="", font=("Arial", 11))
        self.status.pack(anchor="w", pady=(0, 10))

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(fill="x", padx=30, pady=(0, 20))

        ctk.CTkButton(btns, text="Test", width=80, height=36, fg_color="#3a7ca5",
            hover_color="#2d6a8f", command=self.test_connection).pack(side="left")
        ctk.CTkButton(btns, text="Save", width=80, height=36, fg_color="#2a9d8f",
            hover_color="#238b7e", command=self.save_config).pack(side="right")
        ctk.CTkButton(btns, text="Cancel", width=80, height=36, fg_color="#555555",
            hover_color="#666666", command=self.destroy).pack(side="right", padx=(0, 10))

    def load_config(self):
        try:
            if os.path.exists(self.env_path):
                with open(self.env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '=' in line and not line.startswith('#'):
                            k, v = line.strip().split('=', 1)
                            if k == 'API_BASE_URL': self.url_entry.insert(0, v)
                            elif k == 'API_KEY': self.key_entry.insert(0, v)
                            elif k == 'MODEL_NAME': self.model_entry.insert(0, v)
        except: pass

    def save_config(self):
        url, key, model = self.url_entry.get().strip(), self.key_entry.get().strip(), self.model_entry.get().strip()
        if not all([url, key, model]):
            self.status.configure(text="❌ Fill all fields", text_color="#ff5555")
            return
        try:
            with open(self.env_path, 'w', encoding='utf-8') as f:
                f.write(f"API_BASE_URL={url}\nAPI_KEY={key}\nMODEL_NAME={model}\n")
            self.status.configure(text="✅ Saved!", text_color="#50fa7b")
            if self.on_save: self.on_save()
            self.after(500, self.destroy)
        except Exception as e:
            self.status.configure(text=f"❌ {e}", text_color="#ff5555")

    def test_connection(self):
        url, key, model = self.url_entry.get().strip(), self.key_entry.get().strip(), self.model_entry.get().strip()
        if not all([url, key, model]):
            self.status.configure(text="❌ Fill all fields", text_color="#ff5555")
            return
        self.status.configure(text="🔄 Testing...", text_color="#f0ad4e")
        
        def do_test():
            try:
                import requests
                r = requests.post(f"{url}/v1/messages", headers={'Content-Type': 'application/json', 
                    'Authorization': f'Bearer {key}'}, json={'model': model, 
                    'messages': [{"role": "user", "content": "Hi"}], 'max_tokens': 10}, timeout=15)
                self.after(0, lambda: self.status.configure(
                    text="✅ OK!" if r.status_code == 200 else f"❌ {r.status_code}", 
                    text_color="#50fa7b" if r.status_code == 200 else "#ff5555"))
            except Exception as e:
                self.after(0, lambda: self.status.configure(text=f"❌ {str(e)[:30]}", text_color="#ff5555"))
        threading.Thread(target=do_test, daemon=True).start()


class SimpleAIChat(ctk.CTk):
    """Simple AI Chat Window"""

    def __init__(self):
        super().__init__()
        self.title("AI Chat - xiaomimimoapi - Jokerwpx")
        self.geometry("900x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.client = None
        self.is_streaming = False
        self.total_tokens = 0
        self.conversation = []
        self.current_response = ""
        self.stream_buffer = ""
        self.last_update = 0

        self.create_widgets()
        self.setup()
        self.bind("<Control-Return>", lambda e: self.send_message())

    def create_widgets(self):
        # Top bar
        top = ctk.CTkFrame(self, height=50, fg_color="#1a1a2e")
        top.pack(fill="x")
        top.pack_propagate(False)

        ctk.CTkLabel(top, text="🤖 AI Chat - xiaomimimoapi - Jokerwpx", font=("Arial", 14, "bold")).pack(side="left", padx=15, pady=10)
        ctk.CTkButton(top, text="⚙️", width=40, height=32, font=("Arial", 16),
            fg_color="transparent", hover_color="#333355", command=self.open_settings).pack(side="right", padx=10)

        info = ctk.CTkFrame(top, fg_color="transparent")
        info.pack(side="right", padx=5)
        self.token_label = ctk.CTkLabel(info, text="Tokens: 0", font=("Arial", 10), text_color="#888")
        self.token_label.pack(side="right", padx=10)
        self.status_label = ctk.CTkLabel(info, text="● Disconnected", font=("Arial", 10), text_color="#888")
        self.status_label.pack(side="right", padx=5)

        # Main
        main = ctk.CTkFrame(self, fg_color="#0f0f1a")
        main.pack(fill="both", expand=True)

        # Chat scroll
        self.chat_scroll = ctk.CTkScrollableFrame(main, fg_color="#16162a", corner_radius=8)
        self.chat_scroll.pack(fill="both", expand=True, padx=10, pady=(10, 5))

        # Input
        inp_container = ctk.CTkFrame(main, fg_color="#1e1e3a", corner_radius=8)
        inp_container.pack(fill="x", padx=10, pady=(5, 10))

        # Hidden storage for actual code content
        self.code_content = ""
        self.has_code = False

        # Code preview frame (shown when code detected)
        self.code_preview_frame = ctk.CTkFrame(inp_container, fg_color="#1e1e2e", corner_radius=6)
        
        self.code_preview_header = ctk.CTkFrame(self.code_preview_frame, fg_color="#2d2d3d", corner_radius=6)
        self.code_preview_header.pack(fill="x", padx=2, pady=2)
        
        self.code_preview_label = ctk.CTkLabel(self.code_preview_header, text="📄 code (0 lines)",
            font=("Arial", 10), text_color="#888")
        self.code_preview_label.pack(side="left", padx=8, pady=4)
        
        self.code_expand_btn = ctk.CTkButton(self.code_preview_header, text="View", width=50, height=22,
            font=("Arial", 9), fg_color="#3a7ca5", hover_color="#2d6a8f", command=self.view_code_input)
        self.code_expand_btn.pack(side="right", padx=4, pady=4)
        
        self.code_clear_btn = ctk.CTkButton(self.code_preview_header, text="✕", width=30, height=22,
            font=("Arial", 9), fg_color="#555", hover_color="#666", command=self.clear_code_input)
        self.code_clear_btn.pack(side="right", padx=2, pady=4)

        # Normal text input (always visible)
        self.user_input = ctk.CTkTextbox(inp_container, height=60, font=("Consolas", 11),
            fg_color="transparent", border_width=0)
        self.user_input.pack(fill="x", padx=8, pady=(8, 4))
        self.user_input.bind("<Control-v>", self.on_paste)

        btns = ctk.CTkFrame(inp_container, fg_color="transparent")
        btns.pack(fill="x", padx=8, pady=(0, 8))

        self.send_btn = ctk.CTkButton(btns, text="Send", width=100, height=32, font=("Arial", 12),
            fg_color="#2a9d8f", hover_color="#238b7e", corner_radius=8, command=self.send_message)
        self.send_btn.pack(side="right", padx=(5, 0))
        ctk.CTkButton(btns, text="Clear", width=70, height=32, font=("Arial", 11),
            fg_color="#444466", hover_color="#555577", corner_radius=8, command=self.clear_chat).pack(side="right", padx=(5, 0))
        ctk.CTkButton(btns, text="New", width=60, height=32, font=("Arial", 11),
            fg_color="#444466", hover_color="#555577", corner_radius=8, command=self.new_conversation).pack(side="right")
        ctk.CTkLabel(btns, text="Ctrl+Enter", font=("Arial", 9), text_color="#555").pack(side="left")

    def setup(self):
        self.use_real_api()

    def on_paste(self, event=None):
        """Handle paste event - check for large code"""
        self.after(10, self.check_for_code_paste)
        return None

    def check_for_code_paste(self):
        """Check if pasted content is large code"""
        text = self.user_input.get("1.0", "end-1c").strip()
        lines = text.split('\n')
        
        # If more than 5 lines and looks like code, switch to code preview
        if len(lines) > 5 and (self.is_code_content(text) or '```' in text):
            self.code_content = text
            self.has_code = True
            self.user_input.delete("1.0", "end")
            self.show_code_preview(len(lines))

    def show_code_preview(self, line_count):
        """Show code preview above input"""
        self.code_preview_frame.pack(fill="x", padx=8, pady=(8, 4), before=self.user_input)
        self.code_preview_label.configure(text=f"📄 code ({line_count} lines)")
        self.user_input.configure(height=40)
        self.user_input.focus()

    def view_code_input(self):
        """View full code in popup"""
        popup = ctk.CTkToplevel(self)
        popup.title("View Code")
        popup.geometry("700x500")
        popup.transient(self)
        
        text = ctk.CTkTextbox(popup, font=("Consolas", 11))
        text.pack(fill="both", expand=True, padx=10, pady=10)
        text.insert("1.0", self.code_content)
        
        def save_and_close():
            self.code_content = text.get("1.0", "end-1c")
            lines = len(self.code_content.split('\n'))
            self.code_preview_label.configure(text=f"📄 code ({lines} lines)")
            popup.destroy()
        
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkButton(btn_frame, text="Save & Close", command=save_and_close).pack(side="right")

    def clear_code_input(self):
        """Clear code input"""
        self.code_content = ""
        self.has_code = False
        self.code_preview_frame.pack_forget()
        self.user_input.configure(height=60)

    def open_settings(self):
        APIConfigDialog(self, self.reload_api)

    def reload_api(self):
        self.use_real_api()

    def use_real_api(self):
        try:
            self.client = APIClient('.env')
            self.status_label.configure(text="● Connected", text_color="#50fa7b")
            self.add_system_msg(f"Connected: {self.client.model}")
        except Exception as e:
            self.status_label.configure(text="● Disconnected", text_color="#ff5555")
            self.add_system_msg(f"❌ {e}")

    def add_role_label(self, role, color):
        """Add role label with timestamp"""
        frame = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        frame.pack(fill="x", anchor="w", pady=(8, 2), padx=5)
        
        ts = datetime.datetime.now().strftime("%H:%M")
        ctk.CTkLabel(frame, text=f"[{role}]", font=("Arial", 11, "bold"), 
            text_color=color).pack(side="left")
        ctk.CTkLabel(frame, text=f" {ts}", font=("Arial", 9), 
            text_color="#555").pack(side="left")

    def add_text(self, text):
        """Add plain text"""
        label = ctk.CTkLabel(self.chat_scroll, text=text, font=("Arial", 11),
            text_color="#e0e0e0", wraplength=750, justify="left", anchor="w")
        label.pack(fill="x", anchor="w", padx=10, pady=2)

    def add_code_block(self, code, language=""):
        """Add collapsible code block"""
        block = CodeBlock(self.chat_scroll, code, language)
        block.pack(fill="x", padx=10, pady=4)

    def render_content(self, content):
        """Parse and render content with code blocks"""
        code_pattern = r'```(\w*)\n?(.*?)```'
        last_end = 0
        
        for match in re.finditer(code_pattern, content, re.DOTALL):
            # Text before code
            text_before = content[last_end:match.start()].strip()
            if text_before:
                self.add_text(text_before)
            
            # Code block
            lang = match.group(1)
            code = match.group(2).strip()
            if code:
                self.add_code_block(code, lang)
            
            last_end = match.end()
        
        # Remaining text
        remaining = content[last_end:].strip()
        if remaining:
            self.add_text(remaining)

    def add_system_msg(self, text):
        """Add system message"""
        self.add_role_label("System", "#bd93f9")
        self.add_text(text)
        self.scroll_to_bottom()

    def is_code_content(self, text):
        """Check if text looks like code"""
        # Already has code fence
        if '```' in text:
            return False
        
        code_indicators = [
            r'^\s*(def |class |import |from |if |for |while |return |async |await )',  # Python
            r'^\s*(function |const |let |var |import |export |if |for |while |return )',  # JS
            r'^\s*(<\?php|<\w+>|<\w+\s)',  # PHP/HTML/XML
            r'[{}\[\]();]',  # Brackets common in code
            r'^\s*#include|^\s*using namespace',  # C/C++
            r'=>|->|\$\w+|@\w+',  # Arrow functions, variables
        ]
        
        lines = text.strip().split('\n')
        if len(lines) < 2:
            return False
        
        code_line_count = 0
        for line in lines:
            for pattern in code_indicators:
                if re.search(pattern, line, re.MULTILINE):
                    code_line_count += 1
                    break
        
        # If more than 30% lines look like code
        return code_line_count / len(lines) > 0.3

    def wrap_as_code(self, text):
        """Wrap text as code block if it looks like code"""
        if self.is_code_content(text):
            return f"```\n{text}\n```"
        return text

    def add_user_message(self, content):
        """Add user message with auto code detection"""
        self.add_role_label("You", "#4CAF50")
        wrapped = self.wrap_as_code(content)
        self.render_content(wrapped)
        self.scroll_to_bottom()

    def add_ai_message(self, content):
        """Add AI message with code block support"""
        self.add_role_label("AI", "#64b5f6")
        self.render_content(content)
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        """Scroll chat to bottom"""
        self.chat_scroll._parent_canvas.yview_moveto(1.0)

    def send_message(self):
        if self.is_streaming:
            return

        # Combine code and text
        text_input = self.user_input.get("1.0", "end-1c").strip()
        
        if self.has_code and self.code_content:
            # Has code block + optional text
            if text_input:
                user_text = f"{text_input}\n\n```\n{self.code_content}\n```"
            else:
                user_text = f"```\n{self.code_content}\n```"
        else:
            user_text = text_input
        
        if not user_text:
            return

        self.conversation.append({"role": "user", "content": user_text})
        self.add_user_message(user_text)
        
        # Clear input
        self.code_content = ""
        self.has_code = False
        self.code_preview_frame.pack_forget()
        self.user_input.configure(height=60)
        self.user_input.delete("1.0", "end")

        self.send_btn.configure(state="disabled", text="Thinking...")
        self.status_label.configure(text="● Thinking...", text_color="#f0ad4e")
        self.is_streaming = True
        self.current_response = ""

        # Add AI label and streaming text area
        self.add_role_label("AI", "#64b5f6")
        self.stream_text = ctk.CTkTextbox(self.chat_scroll, height=60, font=("Consolas", 11),
            fg_color="#1a1a2e", text_color="#e0e0e0", border_width=0, corner_radius=6)
        self.stream_text.pack(fill="x", padx=10, pady=4)

        threading.Thread(target=self.process_message, daemon=True).start()

    def process_message(self):
        try:
            system_prompt = get_system_prompt()
            messages = [{"role": "system", "content": system_prompt}] + self.conversation
            
            import time
            self.stream_buffer = ""
            self.last_update = time.time()
            char_count = 0

            for chunk in self.client.send_message_stream(messages):
                self.current_response += chunk
                self.stream_buffer += chunk
                char_count += len(chunk)
                
                # Batch updates - only update UI every 100ms or 50 chars
                now = time.time()
                if now - self.last_update > 0.1 or len(self.stream_buffer) > 50:
                    buf = self.stream_buffer
                    tokens = char_count // 4
                    self.stream_buffer = ""
                    self.last_update = now
                    self.after(0, lambda b=buf, t=tokens: self.append_stream_with_tokens(b, t))

            # Flush remaining buffer
            if self.stream_buffer:
                buf = self.stream_buffer
                tokens = char_count // 4
                self.after(0, lambda b=buf, t=tokens: self.append_stream_with_tokens(b, t))

            self.conversation.append({"role": "assistant", "content": self.current_response})
            
            input_tokens = len(self.conversation[-2]['content']) // 4
            output_tokens = len(self.current_response) // 4
            self.total_tokens += input_tokens + output_tokens

            self.after(0, self.finish_response)

        except Exception as ex:
            error_msg = str(ex)
            self.after(0, lambda: self.safe_destroy_stream())
            self.after(0, lambda msg=error_msg: self.add_text(f"❌ {msg}"))

        finally:
            self.is_streaming = False
            self.after(0, lambda: self.send_btn.configure(state="normal", text="Send"))
            self.after(0, lambda: self.status_label.configure(text="● Connected", text_color="#50fa7b"))

    def safe_destroy_stream(self):
        try:
            if hasattr(self, 'stream_text') and self.stream_text.winfo_exists():
                self.stream_text.destroy()
        except:
            pass

    def append_stream_with_tokens(self, text, tokens):
        try:
            if hasattr(self, 'stream_text') and self.stream_text.winfo_exists():
                self.stream_text.configure(state="normal")
                self.stream_text.insert("end", text)
                self.stream_text.see("end")
                # Update tokens in real-time
                input_t = len(self.conversation[-1]['content']) // 4 if self.conversation else 0
                self.token_label.configure(text=f"Tokens: {self.total_tokens + input_t + tokens}")
        except:
            pass

    def finish_response(self):
        """Replace streaming text with parsed content"""
        self.stream_text.destroy()
        self.render_content(self.current_response)
        self.token_label.configure(text=f"Tokens: {self.total_tokens}")
        self.scroll_to_bottom()

    def clear_chat(self):
        for w in self.chat_scroll.winfo_children():
            w.destroy()
        self.conversation = []
        self.total_tokens = 0
        self.token_label.configure(text="Tokens: 0")
        self.add_system_msg("Chat cleared")

    def new_conversation(self):
        self.clear_chat()
        self.add_system_msg("New conversation")


def main():
    app = SimpleAIChat()
    app.mainloop()


if __name__ == "__main__":
    main()
