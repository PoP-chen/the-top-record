import streamlit as st
import csv
import os
import pandas as pd
from hashlib import sha256

USER_FILE = "users.csv"

# 密碼加密
def hash_password(password):
    return sha256(password.encode()).hexdigest()

# 初始化用戶檔案
def init_user_file():
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["username", "password"])  # 欄位名稱

# 檢查用戶是否存在
def user_exists(username):
    with open(USER_FILE, mode="r") as file:
        reader = csv.DictReader(file)
        return any(row["username"] == username for row in reader)

# 新增用戶
def add_user(username, password):
    with open(USER_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([username, hash_password(password)])

# 驗證帳號與密碼
def verify_user(username, password):
    with open(USER_FILE, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["username"] == username and row["password"] == hash_password(password):
                return True
    return False

# 初始化記帳檔案
@st.cache_data
def init_record_file(username):
    filename = f"accounting_records_{username}.csv"
    if not os.path.exists(filename):
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["類別", "日期", "金額", "分類", "描述"])
    return filename

# 加載記帳記錄
@st.cache_data
def load_records(username):
    filename = init_record_file(username)
    with open(filename, mode="r", newline="") as file:
        reader = csv.reader(file)
        return list(reader)

# 儲存記帳記錄
def save_records(username, records):
    filename = init_record_file(username)
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(records)

# 計算總餘額
def calculate_balance(records):
    balance = 0
    for record in records[1:]:  # 跳過標題行
        amount = float(record[2])
        if record[0] == "收入":
            balance += amount
        elif record[0] == "支出":
            balance -= amount
    return balance

# 主選單
def main(username):
    st.title(f"記帳系統（使用者：{username}）")
    st.sidebar.title("選單")
    menu = st.sidebar.selectbox("功能", ["新增記帳記錄", "查看記帳記錄", "計算總餘額"])

    # 載入記錄
    records = load_records(username)

    # 新增記帳記錄
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
                    records.append([category, str(date), str(amount), description, des])
                    save_records(username, records)
                    st.success("記錄已成功新增！")
            except ValueError:
                st.error("金額必須是有效的數字！")

    # 查看記帳記錄
    elif menu == "查看記帳記錄":
        st.subheader("查看記帳記錄")
        category_money = st.selectbox("選擇分類", ["全部", "飲食", "通勤", "生活用品", "娛樂", "其他"])
        filtered_records = records[1:] if category_money == "全部" else [
            r for r in records[1:] if r[3] == category_money
        ]

        if filtered_records:
            df = pd.DataFrame(filtered_records, columns=records[0])
            st.table(df)

            # 圓餅圖
            if st.checkbox("顯示圖表"):
                chart_data = df.groupby("分類")["金額"].sum()
                st.pyplot(chart_data.plot.pie(autopct='%1.1f%%', ylabel=''))
        else:
            st.warning("目前沒有任何記帳記錄。")

    # 計算總餘額
    elif menu == "計算總餘額":
        st.subheader("計算總餘額")
        balance = calculate_balance(records)
        st.write(f"目前總餘額為： **{balance:.2f}**")

# 登入頁面
def login_page():
    st.title("記帳系統")
    st.sidebar.subheader("登入或註冊")
    choice = st.sidebar.selectbox("選擇操作", ["登入", "註冊"])

    if choice == "登入":
        username = st.text_input("輸入帳號")
        password = st.text_input("輸入密碼", type="password")
        if st.button("登入"):
            if verify_user(username, password):
                st.success("登入成功！")
                main(username)
            else:
                st.error("帳號或密碼錯誤！")

    elif choice == "註冊":
        username = st.text_input("輸入帳號")
        password = st.text_input("輸入密碼", type="password")
        if st.button("註冊"):
            if user_exists(username):
                st.error("帳號已存在！")
            else:
                add_user(username, password)
                st.success("註冊成功！請返回登入頁面。")

if __name__ == "__main__":
    init_user_file()
    login_page()