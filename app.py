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

# 主頁面
def main():
    st.title("記帳系統")
    st.sidebar.title("選單")
    menu = st.sidebar.selectbox("功能", ["登入", "創建帳號", "新增記帳記錄", "查看記帳記錄", "計算總餘額"])

    conn = init_db()
    init_session_state()

    if menu == "登入":
        st.subheader("登入")
        st.session_state.input_cache["username"] = st.text_input("帳號", value=st.session_state.input_cache["username"])
        st.session_state.input_cache["password"] = st.text_input("密碼", value=st.session_state.input_cache["password"], type="password")

        if st.button("登入"):
            if login(st.session_state.input_cache["username"], st.session_state.input_cache["password"], conn):
                st.session_state.logged_in = True
                st.session_state.username = st.session_state.input_cache["username"]
                st.session_state.input_cache = {"username": "", "password": ""}
            else:
                st.session_state.logged_in = False
        
        # 新增刪除所有資料的按鈕
        if st.button("刪除所有資料"):
            reset_db()

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
            description = st.selectbox("分類", ["飲食", "通勤", "生活"])
            details = st.text_area("詳細內容")

            if st.button("儲存記錄"):
                save_record(username, category, record_date, float(amount), description, details, conn)
                st.success("記錄已儲存！")

        elif menu == "查看記帳記錄":
            st.subheader("查看記帳記錄")
            records = load_records(username, conn)
            if records:
                st.write(records)
            else:
                st.warning("尚無記錄！")

        elif menu == "計算總餘額":
            st.subheader("計算總餘額")
            records = load_records(username, conn)
            balance = calculate_balance(records)
            st.info(f"總餘額為：{balance} 元")

# 執行程式
if __name__ == "__main__":
    main()