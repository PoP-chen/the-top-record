import streamlit as st
import pandas as pd

# 模擬的帳號資料庫（用於儲存用戶資料）
if "user_db" not in st.session_state:
    st.session_state["user_db"] = {}  # 帳號: 密碼
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None
if "user_data" not in st.session_state:
    st.session_state["user_data"] = {}  # 各用戶的交易記錄

# 註冊功能
def register():
    st.title("註冊帳號")
    username = st.text_input("輸入帳號")
    password = st.text_input("輸入密碼", type="password")
    confirm_password = st.text_input("確認密碼", type="password")
    if st.button("註冊"):
        if not username or not password:
            st.error("帳號和密碼不得為空")
        elif username in st.session_state["user_db"]:
            st.error("此帳號已被註冊")
        elif password != confirm_password:
            st.error("密碼不一致")
        else:
            st.session_state["user_db"][username] = password
            st.session_state["user_data"][username] = []  # 初始化交易記錄
            st.success("註冊成功，請登入！")
            st.session_state["view"] = "login"

# 登入功能
def login():
    st.title("登入")
    username = st.text_input("帳號")
    password = st.text_input("密碼", type="password")
    if st.button("登入"):
        if username in st.session_state["user_db"] and st.session_state["user_db"][username] == password:
            st.success("登入成功！")
            st.session_state["logged_in"] = True
            st.session_state["current_user"] = username
        else:
            st.error("帳號或密碼錯誤")

# 記帳功能
def budget_tracker():
    st.title(f"記帳網站 - 歡迎 {st.session_state['current_user']}")

    # 表單：新增交易
    with st.form("add_transaction", clear_on_submit=True):
        description = st.text_input("描述")
        amount = st.number_input("金額", format="%.2f")
        submitted = st.form_submit_button("新增交易")
        if submitted:
            if description and amount:
                st.session_state["user_data"][st.session_state["current_user"]].append({"描述": description, "金額": amount})
                st.success("成功新增交易！")

    # 顯示交易記錄
    st.subheader("交易記錄")
    transactions = st.session_state["user_data"][st.session_state["current_user"]]
    if transactions:
        df = pd.DataFrame(transactions)
        st.table(df)
    else:
        st.write("目前尚無交易記錄。")

    # 總結
    st.subheader("統計")
    if transactions:
        total = sum([t["金額"] for t in transactions])
        st.metric("總金額", f"${total:.2f}")

    # 登出按鈕
    if st.button("登出"):
        st.session_state["logged_in"] = False
        st.session_state["current_user"] = None
        st.info("已登出")

# 主流程控制
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
    budget_tracker()