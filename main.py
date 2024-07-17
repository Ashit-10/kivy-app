from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.camera import Camera
from kivy.uix.image import AsyncImage
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.modalview import ModalView
from kivy.graphics import RoundedRectangle, Color
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
import os
import random

# Predefined list of colors
COLORS = ["#3498db", "#1abc9c", "#f39c12", "#e74c3c", "#8e44ad", "#2ecc71"]

class RoundedButton(Button):
    def __init__(self, **kwargs):
        super(RoundedButton, self).__init__(**kwargs)
        self.background_normal = ''  # Remove the default background
        self.background_color = (0, 0, 1, 0)  # Make the background transparent
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.background_color[:-1], 1)  # Use the given background color
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(20)])
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class CameraScreen(Screen):
    def __init__(self, **kwargs):
        super(CameraScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')

        # Add the camera widget
        self.camera = Camera(play=True, resolution=(960, 480))
        self.layout.add_widget(self.camera)

        # Horizontal box layout for buttons
        self.button_layout = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))

        # Capture button
        self.capture_button = RoundedButton(text='Capture', size_hint=(None, None), size=(dp(100), dp(48)), background_color=random.choice(COLORS))
        self.capture_button.bind(on_press=self.capture_image)
        self.button_layout.add_widget(self.capture_button)

        # Flashlight button
        self.flashlight_button = RoundedButton(text='Flashlight', size_hint=(None, None), size=(dp(100), dp(48)), background_color=random.choice(COLORS))
        self.flashlight_button.bind(on_press=self.toggle_flashlight)
        self.button_layout.add_widget(self.flashlight_button)

        # Back button
        self.back_button = RoundedButton(text='Back', size_hint=(None, None), size=(dp(100), dp(48)), background_color="#e74c3c")
        self.back_button.bind(on_press=self.go_back)
        self.button_layout.add_widget(self.back_button)

        self.layout.add_widget(self.button_layout)
        self.add_widget(self.layout)

        # Placeholder for the result image
        self.result_image = AsyncImage()

        # Loading label
        self.loading_label = Label(text='Processing...')

        # Action layout for result screen
        self.action_layout = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        self.cancel_button = RoundedButton(text='Cancel', size_hint=(None, None), size=(dp(100), dp(48)), background_color="#e74c3c")
        self.cancel_button.bind(on_press=self.restart_camera)
        self.action_layout.add_widget(self.cancel_button)
        self.save_button = RoundedButton(text='Save and Next', size_hint=(None, None), size=(dp(150), dp(48)), background_color=random.choice(COLORS))
        self.save_button.bind(on_press=self.save_and_restart)
        self.action_layout.add_widget(self.save_button)

    def capture_image(self, instance):
        # Capture image from the camera
        camera = self.camera
        if camera.texture:
            camera.export_to_png("images/capture.png")
            self.process_image("images/capture.png")

    def process_image(self, image_path):
        # Process image with OpenCV (dummy processing)
        self.layout.clear_widgets()
        self.layout.add_widget(self.loading_label)

        # Dummy processing for demonstration
        result_path = image_path  # Replace with your actual image processing logic

        # Display result image
        self.result_image.source = result_path
        self.result_image.allow_stretch = True
        self.result_image.keep_ratio = True
        self.layout.clear_widgets()
        self.layout.add_widget(self.result_image)
        self.layout.add_widget(self.action_layout)

    def toggle_flashlight(self, instance):
        # Toggle flashlight on/off
        if self.camera.play:
            self.camera.play = False
        else:
            self.camera.play = True

    def restart_camera(self, instance):
        # Restart camera view
        self.layout.clear_widgets()
        self.layout.add_widget(self.camera)
        self.layout.add_widget(self.button_layout)

    def save_and_restart(self, instance):
        # Save image and restart camera view
        # Placeholder for saving functionality
        self.restart_camera(None)

    def go_back(self, instance):
        self.manager.current = 'home'

class FolderScreen(Screen):
    def __init__(self, folder_name=None, **kwargs):
        super(FolderScreen, self).__init__(**kwargs)
        self.folder_name = folder_name
        self.layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        # Label for folder name
        self.label = Label(text=f'Folder: {self.folder_name}', size_hint_y=None, height=dp(48))
        self.layout.add_widget(self.label)

        # Scroll view for file grid
        self.scroll_view = ScrollView()
        self.file_grid = GridLayout(cols=10, spacing=dp(10), size_hint_y=None)
        self.file_grid.bind(minimum_height=self.file_grid.setter('height'))
        self.update_file_list()
        self.scroll_view.add_widget(self.file_grid)
        self.layout.add_widget(self.scroll_view)

        # Back button
        self.back_button = RoundedButton(text='Back', size_hint=(None, None), size=(dp(100), dp(48)), background_color="#e74c3c")
        self.back_button.bind(on_press=self.go_back)
        self.layout.add_widget(self.back_button)

        self.add_widget(self.layout)

    def update_file_list(self):
        self.file_grid.clear_widgets()

        if not self.folder_name:
            return

        folder_path = os.path.abspath(self.folder_name)
        try:
            files = os.listdir(folder_path)
            print(f"Files in {folder_path}: {files}")  # Debug print
            for file_name in files:
                file_path = os.path.join(folder_path, file_name)
                if os.path.isfile(file_path):
                    if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        image = AsyncImage(source=file_path, allow_stretch=True, keep_ratio=True)
                        image.bind(on_touch_down=self.on_image_touch)  # Bind touch event
                        self.file_grid.add_widget(image)
                    else:
                        file_button = RoundedButton(text=file_name, size_hint=(1, None), height=dp(48), background_color=random.choice(COLORS))
                        self.file_grid.add_widget(file_button)
        except FileNotFoundError:
            print(f"Folder '{self.folder_name}' not found.")
        except PermissionError:
            print(f"Permission denied for folder '{self.folder_name}'.")
        except Exception as e:
            print(f"Error while updating file list for folder '{self.folder_name}': {e}")

    def on_image_touch(self, instance, touch):
        if touch.is_double_tap:
            print(f"Image {instance.source} tapped!")
            self.display_image_fullscreen(instance.source)

    def display_image_fullscreen(self, image_path):
        view = ModalView(size_hint=(1, 1))
        image = AsyncImage(source=image_path, allow_stretch=True)
        view.add_widget(image)
        view.open()

    def go_back(self, instance):
        self.manager.current = 'home'

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        # Scroll view for folder list
        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.folder_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        self.scroll_view.add_widget(self.folder_layout)
        self.update_folder_list()
        self.layout.add_widget(self.scroll_view)

        # Add 'scan' button
        self.scan_button = RoundedButton(text='Scan', size_hint=(None, None), size=(dp(100), dp(48)), background_color=random.choice(COLORS))
        self.scan_button.bind(on_press=self.open_camera_screen)
        self.layout.add_widget(self.scan_button)

        # Add 'add folder' button
        self.add_folder_button = RoundedButton(text='Add Folder', size_hint=(None, None), size=(dp(120), dp(48)), background_color=random.choice(COLORS))
        self.add_folder_button.bind(on_press=self.show_add_folder_popup)
        self.layout.add_widget(self.add_folder_button)

        self.add_widget(self.layout)

    def update_folder_list(self):
        self.folder_layout.clear_widgets()
        self.folder_layout.height = 0  # Reset height

        for folder_name in os.listdir('.'):
            if os.path.isdir(folder_name):
                folder_button = RoundedButton(text=folder_name, size_hint_y=None, height=dp(48), background_color=random.choice(COLORS))
                folder_button.bind(on_press=self.open_folder_screen)
                self.folder_layout.add_widget(folder_button)
                self.folder_layout.height += folder_button.height + dp(10)  # Update height

    def show_add_folder_popup(self, instance):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        folder_name_input = TextInput(hint_text='Folder Name', multiline=False)
        content.add_widget(folder_name_input)
        add_button = Button(text='Add', size_hint_y=None, height=dp(48))
        content.add_widget(add_button)

        popup = Popup(title='Add Folder', content=content, size_hint=(0.9, 0.5))

        def add_folder(instance):
            folder_name = folder_name_input.text.strip()
            if folder_name:
                if not os.path.exists(folder_name):
                    os.makedirs(folder_name)
                    self.update_folder_list()
                    popup.dismiss()

        add_button.bind(on_press=add_folder)
        popup.open()

    def open_camera_screen(self, instance):
        self.manager.current = 'camera'

    def open_folder_screen(self, instance):
        folder_name = instance.text
        self.manager.add_widget(FolderScreen(name=folder_name, folder_name=folder_name))
        self.manager.current = folder_name

class MyApp(App):
    def build(self):
        self.screen_manager = ScreenManager()
        self.screen_manager.add_widget(HomeScreen(name='home'))
        self.screen_manager.add_widget(CameraScreen(name='camera'))
        return self.screen_manager

if __name__ == '__main__':
    MyApp().run()
