import os
import csv
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

USER_FILE = "users.csv"

# 初始化使用者檔案
def load_users():
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, mode="w", newline="") as file:
            pass  # 如果檔案不存在，創建空白檔案
    with open(USER_FILE, mode="r", newline="") as file:
        return list(csv.reader(file))

# 驗證用戶登入
def validate_user(username, password):
    users = load_users()
    return any(user[0] == username and user[1] == password for user in users)

# 創建帳號
def create_account(username, password):
    users = load_users()
    if any(user[0] == username for user in users):
        st.error("此帳號已存在，請選擇其他帳號！")
        return False
    users.append([username, password])
    with open(USER_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(users)
    initialize_user_file(username)
    return True

# 初始化用戶的記帳檔案
def initialize_user_file(username):
    try:
        record_file = f"{username}_records.csv"
        if not os.path.exists(record_file):
            with open(record_file, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["類別", "日期", "金額", "描述"])

        category_file = f"{username}_categories.csv"
        if not os.path.exists(category_file):
            with open(category_file, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["類別"])
                writer.writerow(["收入"])
                writer.writerow(["支出"])
    except Exception as e:
        st.error(f"初始化檔案時發生錯誤: {str(e)}")

# 讀取記帳記錄
def load_records(username):
    try:
        record_file = f"{username}_records.csv"
        if not os.path.exists(record_file):
            initialize_user_file(username)
        with open(record_file, mode="r", newline="") as file:
            return list(csv.reader(file))[1:]  # 跳過標題行
    except Exception as e:
        st.error(f"讀取記帳記錄時發生錯誤: {str(e)}")
        return []

# 儲存記帳記錄
def save_records(username, records):
    try:
        record_file = f"{username}_records.csv"
        with open(record_file, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["類別", "日期", "金額", "描述"])
            writer.writerows(records)
    except Exception as e:
        st.error(f"儲存記帳記錄時發生錯誤: {str(e)}")

# 讀取類別
def load_categories(username):
    try:
        category_file = f"{username}_categories.csv"
        if not os.path.exists(category_file):
            initialize_user_file(username)
        with open(category_file, mode="r", newline="") as file:
            return [row[0] for row in csv.reader(file)][1:]  # 跳過標題行
    except Exception as e:
        st.error(f"讀取類別時發生錯誤: {str(e)}")
        return []

# 儲存新類別
def save_category(username, category):
    try:
        category_file = f"{username}_categories.csv"
        categories = load_categories(username)
        if category not in categories:
            with open(category_file, mode="a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([category])
            st.success(f"類別 '{category}' 已新增！")
    except Exception as e:
        st.error(f"保存類別時發生錯誤: {str(e)}")

# 計算總餘額
def calculate_balance(records):
    balance = 0
    for record in records:
        try:
            amount = float(record[2])
            if record[0] == "收入":
                balance += amount
            elif record[0] == "支出":
                balance -= amount
        except ValueError:
            continue
    return balance

# 主頁面
def main():
    st.title("記帳系統")
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.page = "login"

    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "dashboard":
        dashboard_page()

# 登入頁面
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
            if create_account(new_username, new_password):
                st.success("帳號創建成功，請重新登入！")
        else:
            st.error("請輸入有效的帳號與密碼！")

# 儀表板頁面
def dashboard_page():
    st.subheader(f"歡迎 {st.session_state.username}！")
    menu = st.sidebar.selectbox("選擇功能", ["新增記帳記錄", "查看記帳記錄", "計算總餘額", "圖表分析", "登出"])
    records = load_records(st.session_state.username)
    categories = load_categories(st.session_state.username)

    if menu == "新增記帳記錄":
        st.subheader("新增記帳記錄")
        category = st.selectbox("選擇類別", categories)
        new_category = st.text_input("新增類別", "")
        if st.button("添加新類別"):
            if new_category:
                save_category(st.session_state.username, new_category)
                st.success(f"類別 '{new_category}' 已新增！")
                st.experimental_rerun()

        date = st.date_input("請選擇日期")
        amount = st.text_input("輸入金額", "")
        description = st.text_input("輸入描述", "")

        if st.button("新增記錄"):
            try:
                amount = int(amount)  # 只允許正整數
                if amount <= 0:
                    st.error("金額必須是正整數！")
                else:
                    records.append([category, date, amount, description])
                    save_records(st.session_state.username, records)
                    st.success("記錄已成功新增！")
            except ValueError:
                st.error("金額必須是有效的正整數！")

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

# 繪製圖表
def plot_charts(records):
    df = pd.DataFrame(records, columns=["類別", "日期", "金額", "描述"])
    df["金額"] = pd.to_numeric(df["金額"], errors="coerce")
    df["日期"] = pd.to_datetime(df["日期"], errors="coerce")
    df = df.dropna(subset=["金額", "日期"])

    if df.empty:
        st.warning("沒有足夠數據生成圖表。")
        return

    category_sums = df.groupby("類別")["金額"].sum()
    fig1, ax1 = plt.subplots()
    ax1.pie(category_sums, labels=category_sums.index, autopct='%1.1f%%', startangle=90)
    ax1.axis("equal")
    st.pyplot(fig1)

    daily_sums = df.groupby("日期")["金額"].sum()
    fig2, ax2 = plt.subplots()
    ax2.plot(daily_sums.index, daily_sums.values, marker="o")
    ax2.set_title("每日記帳金額趨勢")
    ax2.set_xlabel("日期")
    ax2.set_ylabel("金額")
    st.pyplot(fig2)

# 啟動應用
if __name__ == "__main__":
    main()