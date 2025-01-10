import streamlit as st
import sqlite3
import pandas as pd
import bcrypt
import matplotlib.pyplot as plt

DB_NAME = "accounting.db"

# 初始化資料庫
@st.cache_resource
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # 建立用戶表
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    """)
    # 建立記帳記錄表
    c.execute("""
        CREATE TABLE IF NOT EXISTS records (
            username TEXT,
            category TEXT,
            date TEXT,
            amount REAL,
            type TEXT,
            description TEXT,
            FOREIGN KEY(username) REFERENCES users(username)
        )
    """)
    conn.commit()
    return conn

# 密碼加密
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# 驗證密碼
def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)

# 檢查用戶是否存在
def user_exists(username, conn):
    c = conn.cursor()
    c.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    return c.fetchone() is not None

# 新增用戶
def add_user(username, password, conn):
    hashed = hash_password(password)
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
    conn.commit()

# 驗證帳號與密碼
def verify_user(username, password, conn):
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    return result and verify_password(password, result[0])

# 新增記帳記錄
def add_record(username, category, date, amount, record_type, description, conn):
    c = conn.cursor()
    c.execute("""
        INSERT INTO records (username, category, date, amount, type, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (username, category, date, amount, record_type, description))
    conn.commit()

# 獲取記帳記錄
def get_records(username, conn):
    c = conn.cursor()
    c.execute("SELECT category, date, amount, type, description FROM records WHERE username = ?", (username,))
    return c.fetchall()

# 計算總餘額
def calculate_balance(records):
    balance = 0
    for record in records:
        if record[3] == "收入":
            balance += record[2]
        elif record[3] == "支出":
            balance -= record[2]
    return balance

# 主功能
def main(username, conn):
    st.title(f"記帳系統（使用者：{username}）")
    menu = st.sidebar.selectbox("功能", ["新增記帳記錄", "查看記帳記錄", "計算總餘額"])

    # 新增記帳記錄
    if menu == "新增記帳記錄":
        st.subheader("新增記帳記錄")
        category = st.selectbox("選擇類別", ["飲食", "通勤", "生活用品", "娛樂", "其他"])
        date = st.date_input("請選擇日期")
        amount = st.text_input("輸入金額", "")
        record_type = st.selectbox("記錄類型", ["收入", "支出"])
        description = st.text_input("輸入描述", "")

        if st.button("新增記錄"):
            try:
                amount = float(amount)
                if amount <= 0:
                    st.error("金額必須是正數！")
                else:
                    add_record(username, category, str(date), amount, record_type, description, conn)
                    st.success("記錄已成功新增！")
            except ValueError:
                st.error("金額必須是有效的數字！")

    # 查看記帳記錄
    elif menu == "查看記帳記錄":
        st.subheader("查看記帳記錄")
        records = get_records(username, conn)
        if records:
            category_filter = st.selectbox("篩選分類", ["全部"] + ["飲食", "通勤", "生活用品", "娛樂", "其他"])
            filtered_records = records if category_filter == "全部" else [r for r in records if r[0] == category_filter]

            if filtered_records:
                df = pd.DataFrame(filtered_records, columns=["分類", "日期", "金額", "類型", "描述"])
                st.table(df)

                # 圖表
                if st.checkbox("顯示圖表"):
                    chart_type = st.radio("選擇圖表類型", ["圓餅圖", "柱狀圖"])
                    if chart_type == "圓餅圖":
                        pie_data = df.groupby("分類")["金額"].sum()
                        fig, ax = plt.subplots()
                        pie_data.plot.pie(autopct='%1.1f%%', ylabel='', ax=ax)
                        st.pyplot(fig)
                    elif chart_type == "柱狀圖":
                        bar_data = df.groupby("分類")["金額"].sum()
                        fig, ax = plt.subplots()
                        bar_data.plot.bar(ax=ax)
                        st.pyplot(fig)
            else:
                st.warning("目前沒有任何記帳記錄。")

    # 計算總餘額
    elif menu == "計算總餘額":
        st.subheader("計算總餘額")
        records = get_records(username, conn)
        balance = calculate_balance(records)
        st.write(f"目前總餘額為： **{balance:.2f}**")

# 登入頁面
def login_page(conn):
    st.title("記帳系統")
    choice = st.sidebar.selectbox("選擇操作", ["登入", "註冊"])

    if choice == "登入":
        username = st.text_input("輸入帳號")
        password = st.text_input("輸入密碼", type="password")
        if st.button("登入"):
            if verify_user(username, password, conn):
                st.success("登入成功！")
                main(username, conn)
            else:
                st.error("帳號或密碼錯誤！")

    elif choice == "註冊":
        st.subheader("創建帳號")
        username = st.text_input("輸入帳號")
        password = st.text_input("輸入密碼", type="password")
        confirm_password = st.text_input("確認密碼", type="password")

        if password != confirm_password:
            st.error("密碼不一致，請重新輸入！")
        elif st.button("註冊"):
            if user_exists(username, conn):
                st.error("帳號已存在！")
            else:
                add_user(username, password, conn)
                st.success("註冊成功！請返回登入頁面。")

if __name__ == "__main__":
    conn = init_db()
    login_page(conn)