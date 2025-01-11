import streamlit as st
import csv
import os
import matplotlib.pyplot as plt
import pandas as pd

USER_FILE = "users.csv"
RECORD_FILE = "accounting_records.csv"

# 初始化使用者檔案
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, mode="r", newline="") as file:
            return list(csv.reader(file))
    return []

def validate_user(username, password):
    users = load_users()
    return any(user[0] == username and user[1] == password for user in users)

def create_account(username, password):
    users = load_users()
    users.append([username, password])
    with open(USER_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(users)

# 初始化記帳檔案
def load_records():
    if os.path.exists(RECORD_FILE):
        with open(RECORD_FILE, mode="r", newline="") as file:
            return list(csv.reader(file))
    return []

def save_records(records):
    with open(RECORD_FILE, mode="w", newline="") as file:
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

# 主頁
def main():
    st.title("記帳系統")
    
    # 初始化 session_state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.page = "login"

    # 判斷當前頁面
    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "dashboard":
        dashboard_page()

def login_page():
    st.subheader("登入頁面")
    username = st.text_input("帳號", key="login_username")
    password = st.text_input("密碼", type="password", key="login_password")

    if st.button("登入"):
        if validate_user(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.page = "dashboard"
            st.experimental_rerun()
        else:
            st.error("帳號或密碼錯誤！")
    
    st.markdown("---")
    st.subheader("創建帳號")
    new_username = st.text_input("新帳號", key="create_account_username")
    new_password = st.text_input("新密碼", type="password", key="create_account_password")
    
    if st.button("創建新帳號"):
        if new_username and new_password:
            create_account(new_username, new_password)
            st.success("帳號創建成功，請重新登入！")
        else:
            st.error("請輸入有效的帳號與密碼！")

def dashboard_page():
    st.subheader(f"歡迎 {st.session_state.username}！")
    
    menu = st.sidebar.selectbox("選擇功能", ["新增記帳記錄", "查看記帳記錄", "計算總餘額", "圖表分析", "登出"])
    records = load_records()

    if menu == "新增記帳記錄":
        st.subheader("新增記帳記錄")
        category = st.selectbox("選擇類別", ["收入", "支出"])
        date = st.date_input("請選擇日期")
        amount = st.text_input("輸入金額", "")
        description = st.text_input("輸入描述", "")

        if st.button("新增記錄"):
            try:
                amount = float(amount)
                if amount <= 0:
                    st.error("金額必須是正數！")
                else:
                    records.append([category, date, amount, description])
                    save_records(records)
                    st.success("記錄已成功新增！")
            except ValueError:
                st.error("金額必須是有效的數字！")

    elif menu == "查看記帳記錄":
        st.subheader("查看記帳記錄")
        if records:
            st.table(records)
        else:
            st.warning("目前沒有任何記帳記錄。")

    elif menu == "計算總餘額":
        st.subheader("計算總餘額")
        balance = calculate_balance(records)
        st.write(f"目前總餘額為： **{balance:.2f}**")

    elif menu == "圖表分析":
        st.subheader("圖表分析")
        if records:
            plot_charts(records)
        else:
            st.warning("目前沒有足夠數據生成圖表。")

    elif menu == "登出":
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.page = "login"
        st.experimental_rerun()

def plot_charts(records):
    df = pd.DataFrame(records, columns=["類別", "日期", "金額", "描述"])
    df["金額"] = df["金額"].astype(float)
    df["日期"] = pd.to_datetime(df["日期"])

    # 繪製收入與支出總和圓餅圖
    category_sums = df.groupby("類別")["金額"].sum()
    fig1, ax1 = plt.subplots()
    ax1.pie(category_sums, labels=category_sums.index, autopct='%1.1f%%', startangle=90)
    ax1.axis("equal")  # 確保圓形
    ax1.set_title("收入與支出比例")
    st.pyplot(fig1)

    # 繪製時間序列圖
    daily_sums = df.groupby("日期")["金額"].sum()
    fig2, ax2 = plt.subplots()
    ax2.plot(daily_sums.index, daily_sums.values, marker="o")
    ax2.set_title("每日金額趨勢")
    ax2.set_xlabel("日期")
    ax2.set_ylabel("金額")
    st.pyplot(fig2)

# 啟動應用
if __name__ == "__main__":
    main()