import streamlit as st
import csv
import os
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import hashlib

# 檔案名稱
FILENAME = "accounting_records.csv"
USER_FILE = "users.csv"  # 用於存儲帳號密碼的檔案

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

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, mode="r", newline="") as file:
            reader = csv.reader(file)
            return list(reader)
    return []

def save_users(users):
    with open(USER_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(users)

# 創建新帳號
def create_account(username, password):
    users = load_users()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    users.append([username, hashed_password])
    save_users(users)

# 驗證用戶登入
def validate_user(username, password):
    users = load_users()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    for user in users:
        if user[0] == username and user[1] == hashed_password:
            return True
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

# 畫圓餅圖
def plot_pie_chart(records):
    categories = [record[3] for record in records]
    category_counts = Counter(categories)

    labels = category_counts.keys()
    sizes = category_counts.values()

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie chart is circular.
    
    st.pyplot(fig)

# 主頁面
def main():
    st.title("記帳")
    st.sidebar.title("選單")
    menu = st.sidebar.selectbox("功能", ["登入", "創建帳號", "主頁"])

    # 登入頁面
    if menu == "登入":
        st.subheader("登入")
        username = st.text_input("帳號")
        password = st.text_input("密碼", type="password")
        
        if st.button("登入"):
            if validate_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("登入成功！")
                st.experimental_rerun()  # 重新載入頁面，跳轉至主頁面
            else:
                st.error("帳號或密碼錯誤！")

    # 創建帳號頁面
    elif menu == "創建帳號":
        st.subheader("創建帳號")
        new_username = st.text_input("新帳號")
        new_password = st.text_input("新密碼", type="password")

        if st.button("創建帳號"):
            create_account(new_username, new_password)
            st.success("帳號創建成功！")
            st.experimental_rerun()  # 重新載入頁面，跳轉至登入頁面

    # 主頁面
    if "logged_in" in st.session_state and st.session_state.logged_in:
        st.sidebar.selectbox("功能", ["新增記帳記錄", "查看記帳記錄", "計算總餘額", "圖表", "登出"])

        # 載入記錄
        records = load_records()

        # [新增記帳的地方]
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

        # [查看紀錄的地方]
        elif menu == "查看記帳記錄":
            st.subheader("查看記帳記錄")
            category_money_item = ["全部", "飲食", "通勤", "生活用品", "娛樂", "其他"]
            category_money = st.selectbox("選擇類別", category_money_item)

            if category_money == category_money_item[0]:
                if records:
                    df = pd.DataFrame(records, columns=["類別", "日期", "金額", "分類", "描述"])
                    st.table(df)
                else:
                    st.warning("目前沒有任何記帳記錄。")

        # [餘額的地方]
        elif menu == "計算總餘額":
            st.subheader("計算總餘額")
            balance = calculate_balance(records)
            st.write(f"目前總餘額為： **{balance:.2f}**")

        # [圖表的地方]
        elif menu == "圖表":
            st.subheader("記帳類別圓餅圖")
            if records:
                plot_pie_chart(records)
            else:
                st.warning("目前沒有任何記帳記錄。")

        # [登出]
        if st.button("登出"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.success("已登出！")
            st.experimental_rerun()  # 重新載入頁面，跳轉至登入頁面

# 啟動應用
if __name__ == "__main__":
    main()