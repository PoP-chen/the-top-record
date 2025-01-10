import os

def delete_all_data():
    if os.path.exists(FILENAME):
        os.remove(FILENAME)
        st.success("所有數據已成功刪除！")
    else:
        st.error("未找到數據檔案。")