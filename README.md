# Python-Based-Punch-in-Punchout-System
# 🕒 Attendance App with Supabase + Kivy

A simple **punch-in/punch-out attendance system** built using **Python + Kivy**, with cloud storage powered by **Supabase**.

---

## ✨ Features

- Users punch in/out with **Roll Number and Name**
- Records are stored in **Supabase PostgreSQL**
- Sidebar shows all punch-ins and outs **for today**
- Timestamps are stored in **UTC**, displayed in **IST**
- Sidebar refreshes automatically every 3 seconds

---

## 📦 Tech Stack

- Python 3.x
- Kivy (GUI framework)
- Supabase (PostgreSQL + REST API)
- pytz + requests

---

## 🧱 Supabase Setup

1. **Create a Supabase project** at https://supabase.com
2. Go to the **SQL Editor** and run this to create the table:

#sql
create table attendance (
  id uuid default gen_random_uuid() primary key,
  username text,
  password text,
  status text,
  timestamp timestamptz
);

Replace in code for database setup 
SUPABASE_URL = 'https://<your_project_id>.supabase.co'
SUPABASE_API_KEY = '<your_anon_key>'

