import tkinter as tk
from threading import Thread
import sounddevice as sd
import numpy as np
import pyttsx3  # Для озвучивания расшифровки

class MorseDecoderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Morse Code Decoder")

        self.start_button = tk.Button(root, text="Старт", command=self.start_recording)
        self.start_button.pack()

        self.stop_button = tk.Button(root, text="Стоп", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack()

        self.decoded_text_var = tk.StringVar()
        self.decoded_text_label = tk.Label(root, textvariable=self.decoded_text_var, wraplength=400)
        self.decoded_text_label.pack()

        self.status_label = tk.Label(root, text="Статус захвата аудио:")
        self.status_label.pack()

        self.status_square = tk.Canvas(root, width=250, height=300)
        self.status_square.pack()

        self.recording = False
        self.audio_data = None

    def start_recording(self):
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.recording = True
        self.audio_data = np.array([])

        def record_thread():
            with sd.InputStream(callback=self.audio_callback):
                sd.sleep(1000000)  # Запись будет продолжаться, пока не будет вызвана остановка

        self.record_thread = Thread(target=record_thread)
        self.record_thread.start()

        # Обновление статуса захвата аудио в отдельном потоке
        self.update_status_thread = Thread(target=self.update_status)
        self.update_status_thread.start()

    def stop_recording(self):
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.recording = False
        self.record_thread.join()
        self.update_status_thread.join()

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status, flush=True)
        if self.recording:
            self.audio_data = np.concatenate((self.audio_data, indata.flatten()))

    def decode_morse_code(self, threshold=1000, dot_duration=50, dash_multiplier=3):
        morse_code = ""
        is_sound = False
        sound_length = 0

        for amplitude in self.audio_data:
            if abs(amplitude) > threshold:
                if not is_sound:
                    is_sound = True
            else:
                if is_sound:
                    is_sound = False
                    duration = int(sound_length / dot_duration)
                    if duration == 1:
                        morse_code += "."
                    elif duration == dash_multiplier:
                        morse_code += "-"
                    else:
                        morse_code += " "
                    sound_length = 0
                else:
                    sound_length += 1

        decoded_text = self.morse_to_text(morse_code)
        self.decoded_text_var.set(decoded_text)

        # Озвучивание расшифровки
        self.speak(decoded_text)

        # Очистка данных для следующей записи
        self.audio_data = np.array([])

    def speak(self, text):
        # Используем pyttsx3 для озвучивания текста
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    def update_status(self):
        while self.recording:
            self.status_square.config(bg="green")
            self.status_label.config(text="Статус захвата аудио: Захватывается")
            self.root.update()
            self.root.after(50)
            self.status_square.config(bg="yellow")
            self.status_label.config(text="Статус захвата аудио: Обработка")
            self.root.update()
            self.root.after(50)
        self.status_square.config(bg="red")
        self.status_label.config(text="Статус захвата аудио: Остановлен")

    def morse_to_text(self, morse_code):
        morse_dict = {'.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
                      '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
                      '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
                      '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
                      '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
                      '--..': 'Z', '-----': '0', '.----': '1', '..---': '2',
                      '...--': '3', '....-': '4', '.....': '5', '-....': '6',
                      '--...': '7', '---..': '8', '----.': '9', '--..--': ',',
                      '.-.-.-': '.', '..--..': '?'}

        words = morse_code.split('   ')
        decoded_text = ''
        for word in words:
            letters = word.split(' ')
            for letter in letters:
                if letter in morse_dict:
                    decoded_text += morse_dict[letter]
                else:
                    decoded_text += '?'
            decoded_text += ' '

        return decoded_text.strip()

if __name__ == "__main__":
    root = tk.Tk()
    app = MorseDecoderApp(root)
    root.mainloop()
