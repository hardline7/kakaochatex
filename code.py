import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import time
import threading
import schedule
import json
import os
import requests

class KakaoTalkExporter:
    def __init__(self, master):
        self.master = master
        master.title("카카오톡 채팅 내보내기")

        self.kakao_pos = None
        self.chat_pos = None
        self.complete_pos = None
        self.config_file = 'kakao_config.json'
        self.minutes = tk.StringVar(value="180")
        self.auto_confirm = tk.BooleanVar(value=False)
        self.confirm_delay = tk.StringVar(value="5")
        self.telegram_token = tk.StringVar()
        self.telegram_chat_id = tk.StringVar()
        
        self.load_config()
        self.create_widgets()
        self.is_running = False

    def create_widgets(self):
        # 카카오톡 창 위치 프레임
        kakao_frame = ttk.LabelFrame(self.master, text="카카오톡 창 위치")
        kakao_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.kakao_pos_label = ttk.Label(kakao_frame, text="저장되지 않음")
        self.kakao_pos_label.grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(kakao_frame, text="위치 저장", command=self.save_kakao_pos).grid(row=0, column=1, padx=5, pady=5)

        # 대화방 위치 프레임
        chat_frame = ttk.LabelFrame(self.master, text="대화방 위치")
        chat_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        self.chat_pos_label = ttk.Label(chat_frame, text="저장되지 않음")
        self.chat_pos_label.grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(chat_frame, text="위치 저장", command=self.save_chat_pos).grid(row=0, column=1, padx=5, pady=5)

        # 완료 메시지 위치 프레임
        complete_frame = ttk.LabelFrame(self.master, text="완료 메시지 위치")
        complete_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        
        self.complete_pos_label = ttk.Label(complete_frame, text="저장되지 않음")
        self.complete_pos_label.grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(complete_frame, text="위치 저장", command=self.save_complete_pos).grid(row=0, column=1, padx=5, pady=5)

        # 내보내기 설정 프레임
        export_frame = ttk.LabelFrame(self.master, text="내보내기 설정")
        export_frame.grid(row=3, column=0, padx=5, pady=5, sticky="ew")

        ttk.Label(export_frame, text="내보내기 주기 (분):").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(export_frame, textvariable=self.minutes, width=10).grid(row=0, column=1, padx=5, pady=5)

        ttk.Checkbutton(export_frame, text="완료 메시지 자동 확인", variable=self.auto_confirm).grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        ttk.Label(export_frame, text="확인 대기 시간 (초):").grid(row=2, column=0, padx=5, pady=5)
        self.delay_spinbox = ttk.Spinbox(export_frame, from_=1, to=30, textvariable=self.confirm_delay, width=5)
        self.delay_spinbox.grid(row=2, column=1, padx=5, pady=5)

        # 텔레그램 설정 프레임
        telegram_frame = ttk.LabelFrame(self.master, text="텔레그램 설정")
        telegram_frame.grid(row=4, column=0, padx=5, pady=5, sticky="ew")

        ttk.Label(telegram_frame, text="봇 토큰:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(telegram_frame, textvariable=self.telegram_token, width=30).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(telegram_frame, text="채팅 ID:").grid(row=1, column=0, padx=5, pady=5)
        ttk.Entry(telegram_frame, textvariable=self.telegram_chat_id, width=30).grid(row=1, column=1, padx=5, pady=5)

        # 버튼 프레임
        button_frame = ttk.Frame(self.master)
        button_frame.grid(row=5, column=0, padx=5, pady=5)

        self.start_stop_button = ttk.Button(button_frame, text="시작", command=self.toggle_exporting)
        self.start_stop_button.grid(row=0, column=0, padx=5, pady=5)

        ttk.Button(button_frame, text="수동 내보내기", command=self.manual_export).grid(row=0, column=1, padx=5, pady=5)

        self.status_label = ttk.Label(self.master, text="대기 중...")
        self.status_label.grid(row=6, column=0, pady=5)

        # 설정 저장 버튼
        ttk.Button(self.master, text="설정 저장", command=self.save_config).grid(row=7, column=0, pady=10)

        self.update_position_labels()

    def save_kakao_pos(self):
        messagebox.showinfo("안내", "3초 후 카카오톡 창의 아무 위치나 클릭하세요.")
        time.sleep(3)
        self.kakao_pos = pyautogui.position()
        self.update_position_labels()
        messagebox.showinfo("완료", f"카카오톡 창 위치가 저장되었습니다: {self.kakao_pos}")

    def save_chat_pos(self):
        messagebox.showinfo("안내", "3초 후 대화방 내부의 아무 위치나 클릭하세요.")
        time.sleep(3)
        self.chat_pos = pyautogui.position()
        self.update_position_labels()
        messagebox.showinfo("완료", f"대화방 위치가 저장되었습니다: {self.chat_pos}")

    def save_complete_pos(self):
        messagebox.showinfo("안내", "3초 후 내보내기 완료 메시지의 '확인' 버튼을 클릭하세요.")
        time.sleep(3)
        self.complete_pos = pyautogui.position()
        self.update_position_labels()
        messagebox.showinfo("완료", f"완료 메시지 위치가 저장되었습니다: {self.complete_pos}")

    def update_position_labels(self):
        self.kakao_pos_label.config(text=f"X: {self.kakao_pos[0]}, Y: {self.kakao_pos[1]}" if self.kakao_pos else "저장되지 않음")
        self.chat_pos_label.config(text=f"X: {self.chat_pos[0]}, Y: {self.chat_pos[1]}" if self.chat_pos else "저장되지 않음")
        self.complete_pos_label.config(text=f"X: {self.complete_pos[0]}, Y: {self.complete_pos[1]}" if self.complete_pos else "저장되지 않음")

    def export_chat(self):
        if not self.kakao_pos or not self.chat_pos:
            messagebox.showerror("오류", "카카오톡 창 위치와 대화방 위치를 먼저 저장해주세요.")
            return

        pyautogui.click(self.kakao_pos)
        time.sleep(0.5)
        pyautogui.click(self.chat_pos)
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 's')
        time.sleep(2)
        pyautogui.press('enter')
        
        if self.auto_confirm.get() and self.complete_pos:
            confirm_delay = int(self.confirm_delay.get())
            self.status_label.config(text=f"내보내기 완료 대기 중... ({confirm_delay}초)")
            time.sleep(confirm_delay)
            pyautogui.click(self.complete_pos)
        
        self.status_label.config(text="채팅 내보내기 완료")
        self.send_telegram_message("카카오톡 채팅 내보내기가 완료되었습니다.")

    def manual_export(self):
        self.export_chat()

    def toggle_exporting(self):
        if self.is_running:
            self.stop_exporting()
        else:
            self.start_exporting()

    def start_exporting(self):
        try:
            minutes = int(self.minutes.get())
            if minutes < 1:
                raise ValueError("내보내기 주기는 1분 이상이어야 합니다.")
        except ValueError as e:
            messagebox.showerror("오류", str(e))
            return

        self.is_running = True
        self.start_stop_button.config(text="중단")
        self.status_label.config(text="자동 내보내기 시작됨")

        def run_schedule():
            schedule.every(minutes).minutes.do(self.export_chat)
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)

        threading.Thread(target=run_schedule, daemon=True).start()

    def stop_exporting(self):
        self.is_running = False
        schedule.clear()
        self.start_stop_button.config(text="시작")
        self.status_label.config(text="자동 내보내기 중지됨")

    def save_config(self):
        config = {
            'kakao_pos': self.kakao_pos,
            'chat_pos': self.chat_pos,
            'complete_pos': self.complete_pos,
            'export_interval': self.minutes.get(),
            'auto_confirm': self.auto_confirm.get(),
            'confirm_delay': self.confirm_delay.get(),
            'telegram_token': self.telegram_token.get(),
            'telegram_chat_id': self.telegram_chat_id.get()
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f)
        messagebox.showinfo("완료", "설정이 저장되었습니다.")

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            self.kakao_pos = tuple(config.get('kakao_pos', (None, None)))
            self.chat_pos = tuple(config.get('chat_pos', (None, None)))
            self.complete_pos = tuple(config.get('complete_pos', (None, None)))
            self.minutes.set(config.get('export_interval', '180'))
            self.auto_confirm.set(config.get('auto_confirm', False))
            self.confirm_delay.set(config.get('confirm_delay', '5'))
            self.telegram_token.set(config.get('telegram_token', ''))
            self.telegram_chat_id.set(config.get('telegram_chat_id', ''))

    def send_telegram_message(self, message):
        token = self.telegram_token.get()
        chat_id = self.telegram_chat_id.get()
        if token and chat_id:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            params = {
                "chat_id": chat_id,
                "text": message
            }
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
            except requests.RequestException as e:
                print(f"텔레그램 메시지 전송 실패: {e}")
        else:
            print("텔레그램 설정이 완료되지 않았습니다.")

if __name__ == "__main__":
    root = tk.Tk()
    app = KakaoTalkExporter(root)
    root.mainloop()
