from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from urllib.parse import quote
import requests
import datetime
import pytz

SUPABASE_URL = 'https://<your_project_id>.supabase.co'
SUPABASE_API_KEY = '<your_anon_key>'
SUPABASE_TABLE = 'attendance'

class AttendanceApp(App):
    def build(self):
        root_layout = BoxLayout(orientation='horizontal')

        # Sidebar
        self.sidebar = BoxLayout(orientation='vertical', size_hint=(0.4, 1))
        self.sidebar_label = Label(text='[b]Punched In Today[/b]', markup=True, size_hint=(1, 0.1))
        self.sidebar_box = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.sidebar_box.bind(minimum_height=self.sidebar_box.setter('height'))
        scroll = ScrollView(size_hint=(1, 0.9))
        scroll.add_widget(self.sidebar_box)
        self.sidebar.add_widget(self.sidebar_label)
        self.sidebar.add_widget(scroll)

        # Form
        self.form_layout = BoxLayout(orientation='vertical', padding=20, spacing=10, size_hint=(0.6, 1))
        self.username_input = TextInput(hint_text="Roll Number", multiline=False)
        self.password_input = TextInput(hint_text="Name", multiline=False)
        self.status_label = Label(text="Welcome To Cell!")

        punch_in_btn = Button(text="Punch In", background_color=(0, 1, 0, 1))
        punch_in_btn.bind(on_press=self.punch_in)

        punch_out_btn = Button(text="Punch Out", background_color=(1, 0, 0, 1))
        punch_out_btn.bind(on_press=self.punch_out)

        self.form_layout.add_widget(self.username_input)
        self.form_layout.add_widget(self.password_input)
        self.form_layout.add_widget(punch_in_btn)
        self.form_layout.add_widget(punch_out_btn)
        self.form_layout.add_widget(self.status_label)

        root_layout.add_widget(self.sidebar)
        root_layout.add_widget(self.form_layout)

        Clock.schedule_interval(lambda dt: self.update_sidebar(), 3)  # Auto refresh every 3 seconds
        return root_layout

    def get_current_time_iso(self):
        now_utc = datetime.datetime.utcnow()
        return now_utc.isoformat() + 'Z'

    def send_to_supabase(self, username, password, status):
        url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
        headers = {
            "apikey": SUPABASE_API_KEY,
            "Authorization": f"Bearer {SUPABASE_API_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        data = {
            "username": username,
            "password": password,
            "status": status,
            "timestamp": self.get_current_time_iso()
        }
        response = requests.post(url, json=data, headers=headers)
        return response.status_code, response.text

    def update_sidebar(self):
        self.sidebar_box.clear_widgets()

        # Calculate IST midnight and convert to UTC
        ist = pytz.timezone("Asia/Kolkata")
        now = datetime.datetime.now(ist)
        ist_midnight = datetime.datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=ist)
        utc_midnight = ist_midnight.astimezone(pytz.utc).isoformat()

        # Encode the timestamp filter properly
        filter_time = quote(f"gte.{utc_midnight}")
        url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}?select=username,password,status,timestamp&timestamp={filter_time}"

        headers = {
            "apikey": SUPABASE_API_KEY,
            "Authorization": f"Bearer {SUPABASE_API_KEY}"
        }
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            self.sidebar_box.add_widget(Label(text="Error fetching records", size_hint_y=None, height=30))
            return

        records = response.json()
        punch_times = {}
        for record in records:
            user = record['username']
            name = record.get("password", "")
            # Convert UTC to IST
            utc_time = datetime.datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00'))
            ist_time = utc_time.astimezone(ist)
            time_str = ist_time.strftime("%H:%M")

            if user not in punch_times:
                punch_times[user] = {"name": name, "in": "", "out": ""}
            punch_times[user][record["status"]] = time_str

        if punch_times:
            for user, times in punch_times.items():
                name = times.get("name", user)
                in_time = times.get("in", "")
                out_time = times.get("out", "")
                display = f"{user} - {name} @ {in_time}"
                if out_time:
                    display += f" - {out_time}"
                self.sidebar_box.add_widget(Label(text=display, size_hint_y=None, height=30))
        else:
            self.sidebar_box.add_widget(Label(text="No records yet", size_hint_y=None, height=30))

    def punch_in(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        if not username or not password:
            self.status_label.text = "Enter both roll number and name!"
            return

        status_code, _ = self.send_to_supabase(username, password, "in")
        if status_code == 201:
            self.status_label.text = f"{username} punched IN"
        else:
            self.status_label.text = "Error punching in"

    def punch_out(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        if not username or not password:
            self.status_label.text = "Enter both roll number and name!"
            return

        status_code, _ = self.send_to_supabase(username, password, "out")
        if status_code == 201:
            self.status_label.text = f"{username} punched OUT"
        else:
            self.status_label.text = "Error punching out"

if __name__ == '__main__':
    AttendanceApp().run()
