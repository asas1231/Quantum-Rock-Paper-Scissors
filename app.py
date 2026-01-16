import streamlit as st
from qiskit import QuantumCircuit, Aer, execute
import pandas as pd
from datetime import datetime

# --- 初始化量子後端 ---
backend = Aer.get_backend('qasm_simulator')

def get_quantum_move():
    """透過量子電路產生隨機出拳"""
    qc = QuantumCircuit(2, 2)
    qc.h([0, 1])  # 對兩個位元施加 Hadamard Gate
    qc.measure([0, 1], [0, 1])
    
    while True:
        job = execute(qc, backend, shots=1)
        result = job.result().get_counts()
        outcome = list(result.keys())[0] # 得到 '00', '01', '10' 或 '11'
        
        mapping = {"00": "石頭", "01": "剪刀", "10": "布"}
        if outcome in mapping:
            return mapping[outcome]

# --- 網頁介面與邏輯 ---
st.set_page_config(page_title="量子猜拳大賽", layout="centered")

st.title("🌌 量子隨機猜拳戰")
st.write("電腦的出拳是由量子疊加態崩塌產生的，絕對公平且不可預測！")

# 初始化 Session State
if 'win_count' not in st.session_state:
    st.session_state.win_count = 0
if 'history' not in st.session_state:
    st.session_state.history = []
if 'game_over' not in st.session_state:
    st.session_state.game_over = False

# 判斷勝負函數
def judge(user, computer):
    if user == computer: return "平手"
    winning_rules = {"石頭": "剪刀", "剪刀": "布", "布": "石頭"}
    return "勝利" if winning_rules[user] == computer else "失敗"

# 遊戲介面
if not st.session_state.game_over:
    st.subheader(f"目前連勝次數： {st.session_state.win_count}")
    
    col1, col2, col3 = st.columns(3)
    user_choice = None
    
    with col1:
        if st.button("🪨 石頭"): user_choice = "石頭"
    with col2:
        if st.button("✂️ 剪刀"): user_choice = "剪刀"
    with col3:
        if st.button("📄 布"): user_choice = "布"

    if user_choice:
        comp_choice = get_quantum_move()
        result = judge(user_choice, comp_choice)
        
        st.info(f"你出：{user_choice} | 量子電腦出：{comp_choice}")
        
        if result == "勝利":
            st.success("🎉 你贏了！量子態站在你這邊！")
            st.session_state.win_count += 1
            st.balloons()
        elif result == "平手":
            st.warning("🤝 平手！再試一次。")
        else:
            st.error("💀 你輸了！遊戲結束。")
            # 紀錄歷史
            st.session_state.history.append({
                "時間": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "連勝紀錄": st.session_state.win_count
            })
            st.session_state.game_over = True
            st.rerun()

else:
    st.error(f"遊戲結束！最終連勝：{st.session_state.win_count}")
    if st.button("🔄 重新開始挑戰"):
        st.session_state.win_count = 0
        st.session_state.game_over = False
        st.rerun()

# --- 歷史紀錄區 ---
st.divider()
st.subheader("📜 歷史榮譽榜")
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    st.table(df.sort_values(by="連勝紀錄", ascending=False))
else:
    st.write("尚無紀錄，開始你的第一場戰鬥吧！")

