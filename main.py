import random
import threading
import tkinter as tk
from time import sleep
from threading import Thread
import numpy as np
import pygame
from data.database_handler import DatabaseHandler

CORRECT_ANSWER_PTS = 1
TIME = 25


class GameWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.database_handler = DatabaseHandler('database.db')
        self.title("Blind Test")
        self.geometry("{0}x{1}+0+0".format(self.winfo_screenwidth(), self.winfo_screenheight()))
        self.label = tk.Label(self, text="00:00:00", font=("Helvetica", 50))
        self.label.pack()
        self.BASE_TIME = TIME
        self.time = self.BASE_TIME
        self.running = False
        self.songs = self.database_handler.get_songs()
        random.shuffle(self.songs)
        self.next_song_gen = self.next_song()
        self.song = next(self.next_song_gen)
        self.stop_event = None
        self.thread = None
        self.end = False
        self.count = 0
        self.pt = CORRECT_ANSWER_PTS

        pygame.init()

        self.entry = tk.Entry(self)
        self.entry.pack()

        self.submit_button = tk.Button(self, text="Envoyer", command=self.submit_callback)
        self.submit_button.pack()

    def submit_callback(self):
        text = self.entry.get()

        index = self.songs.index(self.song)
        self.songs[index]['input'] = text

        self.entry.delete(0, tk.END)
        self.stop_timer()

    def run_timer(self, stop_event):
        while self.running and not stop_event.is_set():
            self.time -= 1
            minutes, seconds = divmod(self.time, 60)
            hours, minutes = divmod(minutes, 60)
            self.label.config(text="{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds))
            if self.time <= 0:
                return self.stop_timer()

            sleep(1)

    def next_song(self):
        i = 0
        while True:
            self.end = i + 1 >= len(self.songs)
            yield self.songs[i]
            i = (i + 1) % len(self.songs)

    def run_song(self):
        pygame.mixer.music.load(f"assets/{self.song['path']}.mp3")
        pygame.mixer.music.play()

    def start_lap(self):
        self.entry.delete(0, tk.END)
        self.running = True
        self.stop_event = threading.Event()
        self.thread = Thread(target=self.run_timer, daemon=True, args=(self.stop_event,))
        self.thread.start()
        self.run_song()

    def stop_timer(self):
        if self.end:
            return self.start_end()
        self.stop_event.set()
        self.running = False
        pygame.mixer.music.stop()
        self.time = self.BASE_TIME
        minutes, seconds = divmod(self.time, 60)
        hours, minutes = divmod(minutes, 60)
        self.label.config(text="{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds))

        self.song = next(self.next_song_gen)

        self.start_lap()

    @staticmethod
    def check_answer(song):
        if song.get('input') is None:
            song['input'] = ""
        title = song['title'].strip().lower().replace(' ', '')
        user_input = song['input'].strip().lower().replace(' ', '')
        max_distance = 3

        distance = np.abs(len(title) - len(user_input))
        for i, char in enumerate(title):
            if i >= len(user_input) or char != user_input[i]:
                distance += 1
        return distance <= max_distance

    def start_end(self):
        pygame.mixer.music.stop()
        self.stop_event.set()
        self.running = False
        self.entry.destroy()
        self.submit_button.destroy()
        self.label.destroy()

        for song in self.songs:
            if self.check_answer(song):
                self.count += self.pt
                tk.Label(self, text=f"{song['title']}: Correct", font=("Helvetica", 25)).pack()
            else:
                tk.Label(self, text=f"{song['title']}: Incorrect", font=("Helvetica", 25)).pack()

        tk.Label(self, text=f"Score: {self.count}/{len(self.songs) * CORRECT_ANSWER_PTS}", font=("Helvetica", 50)).pack()


window = GameWindow()
window.start_lap()
window.mainloop()
