import streamlit as st
import csv
import os
import pandas as pd

FILENAME = "accounting_records.csv"

# 初始化
def load_records():
    if os.path.exists(FILENAME):
        with open(FILENAME, mode="r", newline="") as file:
            reader = csv.reader(file)
            return list(reader)
    return []

# 保存記帳記錄
def save_records(records):
    with open(FILENAME, mode="w", newline="") as file:
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

# 主選單的地方
def main():
    st.title("記帳")
    st.sidebar.title("選單")
    menu = st.sidebar.selectbox("功能", ["新增記帳記錄", "查看記帳記錄", "計算總餘額"])

    # 載入記錄
    records = load_records()

    #[新增記帳的地方]
    if menu == "新增記帳記錄":
        st.subheader("新增記帳記錄")
        category = st.selectbox("選擇類別", ["收入", "支出"])
        date = st.date_input("請選擇日期")
        amount = st.text_input("輸入金額", "")
        description = st.selectbox("分類", ["飲食","通勤","生活用品","娛樂","其他"])
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


    #[查看紀錄的地方]
    elif menu == "查看記帳記錄":
        st.subheader("查看記帳記錄")
        category_money_item= ["全部","飲食","通勤","生活用品","娛樂","其他"]
        category_money = st.selectbox("選擇類別",category_money_item )


        #全部的地方
        if category_money == category_money_item[0]:
            if records:
                df = pd.DataFrame(records, columns=["類別", "日期", "金額", "分類","描述"])
                st.table(df)
            else:
                st.warning("目前沒有任何記帳記錄。")

        #飲食的地方
        if category_money == category_money_item[1]:
            def is_target_category_breakfast(record):
                target_category = "飲食"
                return record[3] == target_category

            filtered_records = list(filter(is_target_category_breakfast, records))
            if filtered_records:
                df = pd.DataFrame(filtered_records, columns=["類別", "日期", "金額", "分類", "描述"])
                st.table(df)
            else:
                st.warning("目前沒有任何記帳記錄。")

        #通勤的地方
        if category_money == category_money_item[2]:
            def is_target_category_go(record):
                target_category = "通勤"
                return record[3] == target_category
            filtered_records = list(filter(is_target_category_go, records))

            if filtered_records:
                df = pd.DataFrame(filtered_records, columns=["類別", "日期", "金額", "分類", "描述"])
                st.table(df)
            else:
                st.warning("目前沒有任何記帳記錄。")

        #生活用品的地方
        if category_money == category_money_item[3]:
            def is_target_category_use(record):
                target_category = "生活用品"
                return record[3] == target_category
            filtered_records = list(filter(is_target_category_use, records))

            if filtered_records:
                df = pd.DataFrame(filtered_records, columns=["類別", "日期", "金額", "分類", "描述"])
                st.table(df)
            else:
                st.warning("目前沒有任何記帳記錄。")

        #娛樂的地方
        if category_money == category_money_item[4]:
            def is_target_category_play(record):
                target_category = "娛樂"
                return record[3] == target_category
            filtered_records = list(filter(is_target_category_play, records))

            if filtered_records:
                df = pd.DataFrame(filtered_records, columns=["類別", "日期", "金額", "分類", "描述"])
                st.table(df)
            else:
                st.warning("目前沒有任何記帳記錄。")

        #其他的地方
        if category_money == category_money_item[5]:
            def is_target_category_another(record):
                target_category = "其他"
                return record[3] == target_category
            filtered_records = list(filter(is_target_category_another, records))

            if filtered_records:
                df = pd.DataFrame(filtered_records, columns=["類別", "日期", "金額", "分類", "描述"])
                st.table(df)
            else:
                st.warning("目前沒有任何記帳記錄。")

        #剛剛想到的刪資料按鍵
        if st.button('刪除所有資料'):
            if len(records) == 0:
                st.error("目前沒有任何記帳記錄。")
            else:
                records.clear()
                save_records(records)
                st.success("全部記錄已成功刪除！")


    #[餘額的地方]
    elif menu == "計算總餘額":

        st.subheader("計算總餘額")
        balance = calculate_balance(records)
        st.write(f"目前總餘額為： **{balance:.2f}**")

# 啟動應用
if __name__ == "__main__":
    main() 




以上是我的程式碼 希望可以幫我改成能登入帳號以利在GitHub 上使用
還有幫我增加一個menu是可以設定每個月或每週都扣款或增加收入的功能 也需要符合每一個欄位