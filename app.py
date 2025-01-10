import streamlit as st
import sqlite3
import bcrypt
import re
import os
import pandas as pd

# 定義合法帳號密碼的正則表達式
VALID_USERNAME_PASSWORD_REGEX = r'^[a-zA-Z0-9_.]+$'

# 設定記帳紀錄檔案
FILENAME = "accounting_records.csv"

# 建立資料庫連接並初始化
def init_db():
    conn = sqlite3.connect('users.db')  # 使用 SQLite 資料庫存儲帳號密碼
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT)''')
    conn.commit()
    return conn

# 驗證帳號和密碼格式
def is_valid_username_password(username, password):
    if re.match(VALID_USERNAME_PASSWORD_REGEX, username) and re.match(VALID_USERNAME_PASSWORD_REGEX, password):
        return True
    else:
        return False

# 驗證使用者是否存在
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
        else:
            st.error("帳號已存在，請選擇其他帳號名稱。")
    else:
        st.error("帳號或密碼包含非法字符，只允許英文字母、數字、_ 和 .")

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
            return False
    else:
        st.error("帳號或密碼包含非法字符，只允許英文字母、數字、_ 和 .")
        return False

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

# 初始化
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

# 主頁面
def main():
    st.title("記帳")
    st.sidebar.title("選單")
    menu = st.sidebar.selectbox("功能", ["登入", "創建帳號", "新增記帳記錄", "查看記帳記錄", "計算總餘額"])

    conn = init_db()

    # 登入頁面
    if menu == "登入":
        st.subheader("登入")
        username = st.text_input("請輸入帳號")
        password = st.text_input("請輸入密碼", type="password")

        if st.button("登入"):
            if login(username, password, conn):
                st.session_state.logged_in = True
                st.success("登入成功！")
            else:
                st.session_state.logged_in = False

    # 創建帳號頁面
    elif menu == "創建帳號":
        st.subheader("創建帳號")
        username = st.text_input("請輸入帳號")
        password = st.text_input("請輸入密碼", type="password")

        if st.button("創建帳號"):
            create_account(username, password, conn)

    # 需要登入才能進行的操作
    if 'logged_in' in st.session_state and st.session_state.logged_in:
        records = load_records()
        # 新增記帳的地方
        if menu == "新增記帳記錄":
            st.subheader("新增記帳記錄")
            category = st.selectbox("選擇類別", ["收入", "支出"])
            date = st.date_input("請選擇日期")
            amount = st.text_input("輸入金額", "")
            description = st.selectbox("分類", ["飲食", "通勤", "生活用品", "娛樂", "其他"])
            des = st.text_input("輸入描述", "")

            if st.button("新增記錄"):
                try:
                    amount = int(amount)
                    if amount <= 0:
                        st.error("金額必須是正數！")
                    else:
                        records.append([category, date, amount, description, des])
                        save_records(records)
                        st.success("記錄已成功新增！")
                except ValueError:
                    st.error("金額必須是有效的數字！")

        # 查看記帳紀錄的地方
        elif menu == "查看記帳記錄":
            st.subheader("查看記帳記錄")
            category_money_item = ["全部", "飲食", "通勤", "生活用品", "娛樂", "其他"]
            category_money = st.selectbox("選擇類別", category_money_item)

            # 過濾紀錄
            if category_money == category_money_item[0]:
                if records:
                    df = pd.DataFrame(records, columns=["類別", "日期", "金額", "分類", "描述"])
                    st.table(df)
                else:
                    st.warning("目前沒有任何記帳記錄。")
            else:
                filtered_records = [record for record in records if record[3] == category_money]
                if filtered_records:
                    df = pd.DataFrame(filtered_records, columns=["類別", "日期", "金額", "分類", "描述"])
                    st.table(df)
                else:
                    st.warning(f"目前沒有 {category_money} 類別的記帳記錄。")

        # 計算總餘額
        elif menu == "計算總餘額":
            st.subheader("計算總餘額")
            balance = calculate_balance(records)
            st.write(f"目前總餘額為： **{balance