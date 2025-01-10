import streamlit as st
import sqlite3
import bcrypt
import re
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

# 重置資料庫（刪除所有舊數據）
def reset_db():
    conn = sqlite3.connect("records.db")
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS users")
    c.execute("DROP TABLE IF EXISTS records")
    conn.commit()
    conn.close()
    st.warning("資料庫已重置，所有舊數據已清除！")

# 初始化 Session State
def init_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "input_cache" not in st.session_state:
        st.session_state.input_cache = {"username": "", "password": ""}

# 驗證帳號密碼格式
def is_valid_username_password(username, password):
    pattern = r"^[a-zA-Z0-9_.]+$"
    return bool(re.match(pattern, username) and re.match(pattern, password))

# 檢查使用者是否存在
def user_exists(username, conn):
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    return c.fetchone() is not None

# 登入頁面
def login_page(conn):
    st.title("登入")
    init_session_state()

    # 輸入帳號密碼
    username = st.text_input("帳號", value=st.session_state.input_cache["username"])
    password = st.text_input("密碼", value=st.session_state.input_cache["password"], type="password")

    if st.button("登入"):
        if is_valid_username_password(username, password):
            if user_exists(username, conn):
                c = conn.cursor()
                c.execute("SELECT password FROM users WHERE username = ?", (username,))
                stored_password = c.fetchone()[0]
                if bcrypt.checkpw(password.encode("utf-8"), stored_password.encode("utf-8")):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.input_cache = {"username": "", "password": ""}
                    st.success(f"歡迎 {username}！")
                else:
                    st.error("密碼錯誤！")
            else:
                st.error("帳號不存在！")
        else:
            st.error("帳號或密碼包含非法字符！")

    # 若使用者未登入，顯示清除資料的選項
    if not st.session_state.logged_in:
        if st.button("重置資料庫"):
            reset_db()

# 主頁面
def main():
    conn = init_db()
    if st.session_state.logged_in:
        st.title("歡迎進入系統")
        st.write(f"您已經登入為: {st.session_state.username}")
        # 其他功能可以放在這裡
    else:
        login_page(conn)

if __name__ == "__main__":
    main()