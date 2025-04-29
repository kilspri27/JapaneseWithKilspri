import random
import json
from pathlib import Path
from gtts import gTTS
import pygame
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import os

# Initialize pygame mixer for audio
pygame.mixer.init()

class JapaneseReadingApp:
    def __init__(self, root, scale=1.5):
        self.root = root
        self.scale = scale  # Define scale variable
        self.root.title("ano hito no tame ni gambarasu")
        self.root.geometry(f"{int(600 * self.scale)}x{int(400 * self.scale)}")  # Scale the window size
        pil_image = Image.open('cute.jpg')  # Open the image file
        pil_image = pil_image.resize((256,256))  # Resize the image if needed
        tk_image = ImageTk.PhotoImage(pil_image)  # Convert the PIL image to Tkinter's format
        
        # Set the icon for the window
        self.root.iconphoto(True, tk_image)
        
        # App state
        self.current_system = None
        self.current_word = None
        self.show_answer = False
        
        # Load word lists
        self.words = {
            'hiragana': self.load_words('hiragana'),
            'katakana': self.load_words('katakana')
        }
        
        # Create audio cache directory
        self.audio_cache_dir = Path('audio_cache')
        self.audio_cache_dir.mkdir(exist_ok=True)
        
        # Create GUI elements
        self.create_menu_ui()
        
        # Bind keyboard events
        self.root.bind('<space>', self.handle_space)
        self.root.bind('<Escape>', self.return_to_menu)
        
    def load_words(self, system):
        """Load word list from JSON file"""
        try:
            with open(f'{system}_words2.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Fallback sample data
            sample_data = {
                'hiragana': [
                    {'word': 'こんにちは', 'reading': 'konnichiwa', 'meaning': 'hello'},
                    {'word': 'ありがとう', 'reading': 'arigatou', 'meaning': 'thank you'},
                    {'word': 'みず', 'reading': 'mizu', 'meaning': 'water'},
                    {'word': 'いぬ', 'reading': 'inu', 'meaning': 'dog'},
                    {'word': 'ねこ', 'reading': 'neko', 'meaning': 'cat'}
                ],
                'katakana': [
                    {'word': 'コーヒー', 'reading': 'koohii', 'meaning': 'coffee'},
                    {'word': 'テレビ', 'reading': 'terebi', 'meaning': 'TV'},
                    {'word': 'ラジオ', 'reading': 'rajio', 'meaning': 'radio'},
                    {'word': 'パン', 'reading': 'pan', 'meaning': 'bread'},
                    {'word': 'ノート', 'reading': 'nooto', 'meaning': 'notebook'}
                ]
            }
            return sample_data.get(system, [])
    
    def create_menu_ui(self):
        """Create the main menu interface"""
        self.clear_window()
        
        Label(self.root, text="Japanese With Kilspri", font=('Helvetica', int(18 * self.scale))).pack(pady=int(20 * self.scale))
        
        Label(self.root, text="Select writing system to practice:", font=('Helvetica', int(12 * self.scale))).pack(pady=int(10 * self.scale))
        
        hiragana_btn = Button(self.root, text="Hiragana", command=lambda: self.start_practice('hiragana'),
                             font=('Helvetica', int(14 * self.scale)), width=int(15 * self.scale))
        hiragana_btn.pack(pady=int(10 * self.scale))
        
        katakana_btn = Button(self.root, text="Katakana", command=lambda: self.start_practice('katakana'),
                             font=('Helvetica', int(14 * self.scale)), width=int(15 * self.scale))
        katakana_btn.pack(pady=int(10 * self.scale))
        
        exit_btn = Button(self.root, text="Exit", command=self.root.quit,
                         font=('Helvetica', int(12 * self.scale)), width=int(10 * self.scale))
        exit_btn.pack(pady=int(20 * self.scale))
        # Load the image using PIL for more flexibility
        image_path = 'kaoruko.jpg'  # Replace with your actual image file path
        pil_image = Image.open(image_path)  # Open the image using Pillow
        pil_image = pil_image.resize((int(113 * self.scale), int(200 * self.scale)), Image.Resampling.LANCZOS)  # Resize the image

        self.image = ImageTk.PhotoImage(pil_image)  # Convert to Tkinter-compatible PhotoImage
        
        # Create a label to hold the image and position it in the bottom-right corner
        image_label = Label(self.root, image=self.image)
        image_label.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)  # Adjust x and y to position it
        
    def create_practice_ui(self):
        """Create the practice interface"""
        self.clear_window()

        # Define max width for wrapping the word text
        max_width = int(500 * self.scale)  # Adjust the width to your needs (scale adjusted)

        # Word display with wraplength to prevent overflow
        self.word_label = Label(self.root, text="", font=('Helvetica', int(48 * self.scale)), wraplength=max_width)
        self.word_label.pack(pady=int(30 * self.scale))

        # Reading display (hidden until space is pressed)
        self.reading_label = Label(self.root, text="", font=('Helvetica', int(24 * self.scale)), wraplength=max_width)

        # Meaning display (hidden until space is pressed)
        self.meaning_label = Label(self.root, text="", font=('Helvetica', int(18 * self.scale)), wraplength=max_width)

        # Instructions
        self.instructions_label = Label(self.root, 
                                        text="Press SPACE to reveal answer\nPress ESC to return to menu",
                                        font=('Helvetica', int(12 * self.scale)))
        self.instructions_label.pack(side=BOTTOM, pady=int(20 * self.scale))

        self.show_new_word()

    
    def clear_window(self):
        """Remove all widgets from the window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def start_practice(self, writing_system):
        """Start practice with the selected writing system"""
        self.current_system = writing_system
        self.show_answer = False
        self.create_practice_ui()
    
    def show_new_word(self):
        """Display a new word for practice"""
        self.current_word = random.choice(self.words[self.current_system])
        self.word_label.config(text=self.current_word['word'])
        self.reading_label.pack_forget()
        self.meaning_label.pack_forget()
        self.show_answer = False
    
    def show_answer_info(self):
        """Display the reading and meaning of the current word"""
        self.reading_label.config(text=f"{self.current_word['reading']}")
        self.reading_label.pack(pady=int(10 * self.scale))
        
        self.meaning_label.config(text=f"({self.current_word['meaning']})")
        self.meaning_label.pack(pady=int(10 * self.scale))
        
        self.play_pronunciation(self.current_word['reading'])
        self.show_answer = True
    
    def play_pronunciation(self, text):
        """Play pronunciation using cached or new TTS"""
        audio_file = self.audio_cache_dir / f"{text}.mp3"
        
        if not audio_file.exists():
            tts = gTTS(text=text, lang='ja')
            tts.save(str(audio_file))
        
        pygame.mixer.music.load(str(audio_file))
        pygame.mixer.music.play()
    
    def handle_space(self, event=None):
        """Handle space bar press"""
        if not self.current_system:
            return
            
        if not self.show_answer:
            self.show_answer_info()
        else:
            self.show_new_word()
    
    def return_to_menu(self, event=None):
        """Return to main menu"""
        self.current_system = None
        self.create_menu_ui()

if __name__ == "__main__":
    root = Tk()
    app = JapaneseReadingApp(root, scale=1.5)  # Set scale here
    root.mainloop()
