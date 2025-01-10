import streamlit as st
import sqlite3
import bcrypt
import re
import os
import pandas as pd
import csv

# 定義合法帳號密碼的正則表達式
VALID_USERNAME_PASSWORD_REGEX = r'^[a-zA-Z0-9_.]+$'

# 記帳紀錄檔案
FILENAME = "accounting_records.csv"

# 初始化資料庫
def init_db():
    conn = sqlite3.connect('users.db')  # 使用 SQLite 資料庫
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT)''')
    conn.commit()
    return conn

# 驗證帳號密碼格式
def is_valid_username_password(username, password):
    return bool(re.match(VALID_USERNAME_PASSWORD_REGEX, username) and re.match(VALID_USERNAME_PASSWORD_REGEX, password))

# 檢查使用者是否存在
def user_exists(username, conn):
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    return c.fetchone() is not None

# 註冊新帳號
def create_account(username, password, conn):
    if is_valid_username_password(username, password):
        if not user_exists(username, conn):
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            st.success("帳號創建成功！")
            return True
        else:
            st.error("帳號已存在，請選擇其他帳號名稱。")
    else:
        st.error("帳號或密碼包含非法字符，只允許英文字母、數字、_ 和 .")
    return False

# 登入帳號
def login(username, password, conn):
    if is_valid_username_password(username, password):
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username = ?", (username,))
        record = c.fetchone()
        if record and bcrypt.checkpw(password.encode('utf-8'), record[0]):
            st.success("登入成功！")
            return True
        else:
            st.error("帳號或密碼錯誤。")
    else:
        st.error("帳號或密碼包含非法字符，只允許英文字母、數字、_ 和 .")
    return False

# 初始化記帳紀錄
def load_records():
    if os.path.exists(FILENAME):
        with open(FILENAME, mode="r", newline="") as file:
            reader = csv.reader(file)
            return list(reader)
    return []

def save_records(records):
    with open(FILENAME, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(records)

# 計算總餘額
def calculate_balance(records):
    balance = 0
    for record in records:
        amount = float(record[2])
        if record[0] == "收入":
            balance += amount
        elif record[0] == "支出":
            balance -= amount
    return balance

# 初始化 Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "input_cache" not in st.session_state:
    st.session_state.input_cache = {"username": "", "password": ""}

# 主頁面
def main():
    st.title("記帳系統")
    st.sidebar.title("選單")
    menu = st.sidebar.selectbox("功能", ["登入", "創建帳號", "新增記帳記錄", "查看記帳記錄", "計算總餘額"])

    conn = init_db()

    # 登入頁面
    if menu == "登入":
        st.subheader("登入")
        username = st.text_input("請輸入帳號", key="login_username", value=st.session_state.input_cache["username"])
        password = st.text_input("請輸入密碼", key="login_password", value=st.session_state.input_cache["password"], type="password")

        if st.button("登入"):
            if login(username, password, conn):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"歡迎回來，{username}！")
            else:
                st.session_state.logged_in = False

        # 清除已輸入內容
        if st.session_state.get("logged_in", False) is False:
            st.session_state.input_cache["username"] = ""
            st.session_state.input_cache["password"] = ""

    # 創建帳號頁面
    elif menu == "創建帳號":
        st.subheader("創建帳號")
        username = st.text_input("請輸入帳號", key="register_username", value=st.session_state.input_cache["username"])
        password = st.text_input("請輸入密碼", key="register_password", value=st.session_state.input_cache["password"], type="password")

        if st.button("創建帳號"):
            if create_account(username, password, conn):
                st.session_state.input_cache["username"] = ""
                st.session_state.input_cache["password"] = ""

    # 新增、查看或計算需要登入
    if 'logged_in' in st.session_state and st.session_state.logged_in:
        records = load_records()

        if menu == "新增記帳記錄":
            st.subheader("新增記帳記錄")
            category = st.selectbox("選擇類別", ["收入", "支出"])
            date = st.date_input("請選擇日期")
            amount = st.text_input("輸入金額", "")
            description = st.selectbox("分類", ["飲食", "通勤", "生活用品", "娛樂", "其他"])
            des = st.text_input("輸入描述", "")

            if st.button("新增記錄"):
                try:
                    amount = float(amount)
                    if amount <= 0:
                        st.error("金額必須是正數！")
                    else:
                        records.append([category, date, amount, description, des])
                        save_records(records)
                        st.success("記錄已成功新增！")
                except ValueError:
                    st.error("金額必須是有效的數字！")

        elif menu == "查看記帳記錄":
            st.subheader("查看記帳記錄")
            category_filter = st.selectbox("分類", ["全部"] + ["飲食", "通勤", "生活用品", "娛樂", "其他"])

            filtered_records = [r for r in records if r[3] == category_filter or category_filter == "全部"]
            if filtered_records:
                df = pd.DataFrame(filtered_records, columns=["類別", "日期", "金額", "分類", "描述"])
                st.table(df)
            else:
                st.warning("沒有相關記錄。")

        elif menu == "計算總餘額":
            st.subheader("計算總餘額")
            balance = calculate_balance(records)
            st.success(f"目前總餘額為： {balance:.2f}")

# 啟動應用
if __name__ == "__main__":
    main()