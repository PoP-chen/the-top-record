import streamlit as st
import csv
import os
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt

ACCOUNT_FILE = "users.csv"
RECORDS_FILE = "accounting_records.csv"
AUTO_TRANSACTIONS_FILE = "auto_transactions.csv"

# 初始化
def load_records(filename):
    if os.path.exists(filename):
        with open(filename, mode="r", newline="") as file:
            reader = csv.reader(file)
            return list(reader)
    return []

def save_records(filename, records):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(records)

def calculate_balance(records):
    balance = 0
    for record in records:
        amount = float(record[2])
        if record[0] == "收入":
            balance += amount
        elif record[0] == "支出":
            balance -= amount
    return balance

# 更新自動交易
def update_auto_transactions(records, auto_transactions):
    today = dt.date.today()
    for transaction in auto_transactions:
        category, frequency, amount, description, last_updated = transaction
        amount = float(amount)
        last_updated = dt.datetime.strptime(last_updated, "%Y-%m-%d").date()

        if frequency == "每週" and (today - last_updated).days >= 7:
            while (today - last_updated).days >= 7:
                last_updated += dt.timedelta(days=7)
                records.append(["支出" if amount < 0 else "收入", last_updated, abs(amount), description, "自動扣款"])
        elif frequency == "每月" and (today.year > last_updated.year or today.month > last_updated.month):
            while today.year > last_updated.year or today.month > last_updated.month:
                next_month = last_updated.month % 12 + 1
                next_year = last_updated.year + (last_updated.month // 12)
                last_updated = dt.date(next_year, next_month, last_updated.day)
                records.append(["支出" if amount < 0 else "收入", last_updated, abs(amount), description, "自動扣款"])
        transaction[4] = last_updated.strftime("%Y-%m-%d")

    save_records(RECORDS_FILE, records)
    save_records(AUTO_TRANSACTIONS_FILE, auto_transactions)

# 繪製圓餅圖
def plot_pie_chart(data, labels, title):
    plt.figure(figsize=(6, 6))
    plt.pie(data, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title(title)
    st.pyplot(plt)

# 登入功能
def authenticate(username, password):
    users = load_records(ACCOUNT_FILE)
    for user in users:
        if user[0] == username and user[1] == password:
            return True
    return False

def main():
    st.title("記帳應用程式")

    # 初始化 Session State
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    # 登入頁面
    if not st.session_state["authenticated"]:
        st.subheader("登入")
        username = st.text_input("使用者名稱")
        password = st.text_input("密碼", type="password")
        if st.button("登入"):
            if authenticate(username, password):
                st.session_state["authenticated"] = True
                st.success("登入成功！")
            else:
                st.error("登入失敗，請檢查帳號密碼。")
        return

    # 主選單
    st.sidebar.title("選單")
    menu = st.sidebar.selectbox("功能", ["新增記帳記錄", "查看記帳記錄", "計算總餘額", "設定自動扣款/收入", "登出"])

    # 載入資料
    records = load_records(RECORDS_FILE)
    auto_transactions = load_records(AUTO_TRANSACTIONS_FILE)
    update_auto_transactions(records, auto_transactions)

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
                amount = int(amount)
                if amount <= 0:
                    st.error("金額必須是正數！")
                else:
                    records.append([category, date, amount, description, des])
                    save_records(RECORDS_FILE, records)
                    st.success("記錄已成功新增！")
            except ValueError:
                st.error("金額必須是有效的數字！")

    # 查看記帳記錄
    elif menu == "查看記帳記錄":
        st.subheader("查看記帳記錄")
        category_money_item = ["全部", "飲食", "通勤", "生活用品", "娛樂", "其他"]
        category_money = st.selectbox("選擇類別", category_money_item)

        if category_money == "全部":
            if records:
                df = pd.DataFrame(records, columns=["類別", "日期", "金額", "分類", "描述"])
                st.table(df)
            else:
                st.warning("目前沒有任何記帳記錄。")
        else:
            filtered_records = [r for r in records if r[3] == category_money]
            if filtered_records:
                df = pd.DataFrame(filtered_records, columns=["類別", "日期", "金額", "分類", "描述"])
                st.table(df)

                # 繪製分類圓餅圖
                amounts = [float(r[2]) for r in filtered_records]
                dates = [r[1] for r in filtered_records]
                plot_pie_chart(amounts, dates, f"{category_money}的花費分布")
            else:
                st.warning("目前沒有任何記帳記錄。")

    # 計算總餘額
    elif menu == "計算總餘額":
        st.subheader("計算總餘額")
        balance = calculate_balance(records)
        st.write(f"目前總餘額為： **{balance:.2f}**")

    # 設定自動扣款/收入
    elif menu == "設定自動扣款/收入":
        st.subheader("設定自動扣款/收入")
        category = st.selectbox("選擇類別", ["支出", "收入"])
        frequency = st.selectbox("選擇頻率", ["每週", "每月"])
        amount = st.text_input("輸入金額", "")
        description = st.text_input("輸入描述", "")

        if st.button("新增自動扣款/收入"):
            try:
                amount = float(amount)
                if amount <= 0:
                    st.error("金額必須是正數！")
                else:
                    today = dt.date.today().strftime("%Y-%m-%d")
                    auto_transactions.append([category, frequency, amount, description, today])
                    save_records(AUTO_TRANSACTIONS_FILE, auto_transactions)
                    st.success("已成功新增自動扣款/收入！")
            except ValueError:
                st.error("金額必須是有效的數字！")

    # 登出
    elif menu == "登出":
        st.session_state["authenticated"] = False
        st.success("已成功登出！")

# 啟動應用
if __name__ == "__main__":
    main()