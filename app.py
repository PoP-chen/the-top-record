import streamlit as st
import sqlite3
import bcrypt
import re
import pandas as pd
from datetime import date

# 初始化資料庫
def init_db():
    conn = sqlite3.connect("records.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY, 
                    password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    category TEXT,
                    record_date TEXT,
                    amount REAL,
                    description TEXT,
                    details TEXT,
                    FOREIGN KEY (username) REFERENCES users(username))''')
    conn.commit()
    return conn

# 驗證帳號密碼格式
def is_valid_username_password(username, password):
    pattern = r"^[a-zA-Z0-9_.]+$"
    return bool(re.match(pattern, username) and re.match(pattern, password))

# 檢查使用者是否存在
def user_exists(username, conn):
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    return c.fetchone() is not None

# 註冊新帳號
def create_account(username, password, conn):
    if is_valid_username_password(username, password):
        if not user_exists(username, conn):
            hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            st.success("帳號創建成功！")
            return True
        else:
            st.error("帳號已存在！")
    else:
        st.error("帳號或密碼包含非法字符，只允許英文字母、數字、_ 和 .")
    return False

# 登入帳號
def login(username, password, conn):
    if is_valid_username_password(username, password):
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username = ?", (username,))
        record = c.fetchone()
        if record and bcrypt.checkpw(password.encode("utf-8"), record[0]):
            st.success("登入成功！")
            return True
        else:
            st.error("帳號或密碼錯誤！")
    else:
        st.error("帳號或密碼包含非法字符，只允許英文字母、數字、_ 和 .")
    return False

# 儲存記錄
def save_record(username, category, record_date, amount, description, details, conn):
    c = conn.cursor()
    c.execute('''INSERT INTO records (username, category, record_date, amount, description, details) 
                 VALUES (?, ?, ?, ?, ?, ?)''', 
              (username, category, record_date, amount, description, details))
    conn.commit()

# 載入記錄
def load_records(username, conn):
    c = conn.cursor()
    c.execute("SELECT category, record_date, amount, description, details FROM records WHERE username = ?", (username,))
    return c.fetchall()

# 計算總餘額
def calculate_balance(records):
    balance = 0
    for record in records:
        category, _, amount, _, _ = record
        if category == "收入":
            balance += amount
        elif category == "支出":
            balance -= amount
    return balance

# 初始化 Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# 主頁面
def main():
    st.title("記帳系統")
    st.sidebar.title("選單")
    menu = st.sidebar.selectbox("功能", ["登入", "創建帳號", "新增記帳記錄", "查看記帳記錄", "計算總餘額"])

    conn = init_db()

    if menu == "登入":
        st.subheader("登入")
        username = st.text_input("帳號")
        password = st.text_input("密碼", type="password")

        if st.button("登入"):
            if login(username, password, conn):
                st.session_state.logged_in = True
                st.session_state.username = username
            else:
                st.session_state.logged_in = False

    elif menu == "創建帳號":
        st.subheader("創建帳號")
        username = st.text_input("帳號")
        password = st.text_input("密碼", type="password")

        if st.button("創建帳號"):
            create_account(username, password, conn)

    elif st.session_state.logged_in:
        username = st.session_state.username

        if menu == "新增記帳記錄":
            st.subheader("新增記帳記錄")
            category = st.selectbox("選擇類別", ["收入", "支出"])
            record_date = st.date_input("日期", date.today())
            amount = st.text_input("金額")
            description = st.selectbox("分類", ["飲食", "通勤", "生活用品", "娛樂", "其他"])
            details = st.text_input("描述")

            if st.button("新增記錄"):
                try:
                    amount = float(amount)
                    save_record(username, category, record_date, amount, description, details, conn)
                    st.success("記錄新增成功！")
                except ValueError:
                    st.error("請輸入有效的金額！")

        elif menu == "查看記帳記錄":
            st.subheader("查看記帳記錄")
            records = load_records(username, conn)
            if records:
                df = pd.DataFrame(records, columns=["類別", "日期", "金額", "分類", "描述"])
                st.table(df)
            else:
                st.warning("尚無記錄。")

        elif menu == "計算總餘額":
            st.subheader("計算總餘額")
            records = load_records(username, conn)
            balance = calculate_balance(records)
            st.success(f"目前總餘額為： {balance:.2f}")

if __name__ == "__main__":
    main()