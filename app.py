import streamlit as st
import pandas as pd
from datetime import date

# 初始化用戶數據
if "user_db" not in st.session_state:
    st.session_state["user_db"] = {}  # 帳號: 密碼
if "user_data" not in st.session_state:
    st.session_state["user_data"] = {}  # 帳號: 交易紀錄
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None

# 類別選項
CATEGORIES = ["娛樂", "飲食", "住宿", "生活用品", "其他"]

# 註冊功能
def register():
    st.title("註冊帳號")
    username = st.text_input("輸入帳號", key="register_username")
    password = st.text_input("輸入密碼", type="password", key="register_password")
    confirm_password = st.text_input("確認密碼", type="password", key="register_confirm_password")
    if st.button("註冊"):
        if not username or not password:
            st.error("帳號和密碼不得為空")
        elif username in st.session_state["user_db"]:
            st.error("此帳號已被註冊")
        elif password != confirm_password:
            st.error("密碼不一致")
        else:
            st.session_state["user_db"][username] = password
            st.session_state["user_data"][username] = []
            st.success("註冊成功，請登入！")
            st.session_state["view"] = "login"

# 登入功能
def login():
    st.title("登入")
    username = st.text_input("帳號", key="login_username")
    password = st.text_input("密碼", type="password", key="login_password")
    if st.button("登入"):
        if username in st.session_state["user_db"] and st.session_state["user_db"][username] == password:
            st.success(f"登入成功！歡迎 {username}")
            st.session_state["logged_in"] = True
            st.session_state["current_user"] = username
        else:
            st.error("帳號或密碼錯誤")

# 新增交易紀錄
def add_transaction():
    st.title("新增交易紀錄")
    col1, col2 = st.columns(2)
    with col1:
        transaction_type = st.radio("類型", ["收入", "支出"])
    with col2:
        category = st.selectbox("類別", CATEGORIES)

    description = st.text_input("描述")
    amount = st.number_input("金額", min_value=0.0, step=0.01)
    transaction_date = st.date_input("日期", value=date.today())

    if st.button("新增交易"):
        if description and amount > 0:
            transaction = {
                "日期": transaction_date,
                "類型": transaction_type,
                "類別": category,
                "描述": description,
                "金額": amount,
            }
            st.session_state["user_data"][st.session_state["current_user"]].append(transaction)
            st.success("成功新增交易！")
        else:
            st.error("請完整填寫交易資訊")

# 查看交易紀錄
def view_transactions():
    st.title("查看交易紀錄")
    transactions = st.session_state["user_data"][st.session_state["current_user"]]
    if transactions:
        df = pd.DataFrame(transactions)
        st.dataframe(df)
    else:
        st.write("目前尚無交易記錄")

# 查看總餘額
def view_balance():
    st.title("查看總餘額")
    transactions = st.session_state["user_data"][st.session_state["current_user"]]
    if transactions:
        df = pd.DataFrame(transactions)
        income = df[df["類型"] == "收入"]["金額"].sum()
        expense = df[df["類型"] == "支出"]["金額"].sum()
        balance = income - expense

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("總收入", f"${income:.2f}")
        with col2:
            st.metric("總支出", f"${expense:.2f}")
        with col3:
            st.metric("餘額", f"${balance:.2f}")
    else:
        st.write("目前尚無交易記錄")

# 主邏輯控制
if "view" not in st.session_state:
    st.session_state["view"] = "login"

if not st.session_state["logged_in"]:
    if st.session_state["view"] == "login":
        login()
        if st.button("還沒有帳號？前往註冊"):
            st.session_state["view"] = "register"
    elif st.session_state["view"] == "register":
        register()
        if st.button("已有帳號？前往登入"):
            st.session_state["view"] = "login"
else:
    # 導覽選單
    menu = st.sidebar.radio("功能選單", ["新增交易", "查看交易紀錄", "查看總餘額", "登出"])
    if menu == "新增交易":
        add_transaction()
    elif menu == "查看交易紀錄":
        view_transactions()
    elif menu == "查看總餘額":
        view_balance()
    elif menu == "登出":
        st.session_state["logged_in"] = False
        st.session_state["current_user"] = None
        st.info("已登出，請重新登入")