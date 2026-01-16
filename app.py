import streamlit as st
import pandas as pd
from datetime import datetime

# 修正後的 Qiskit 引入方式
from qiskit import QuantumCircuit
from qiskit_aer import Aer  # 注意這裡的改變

def get_quantum_move():
    qc = QuantumCircuit(2, 2)
    qc.h([0, 1])
    qc.measure([0, 1], [0, 1])
    while True:
        job = backend.run(qc, shots=1)
        result = job.result().get_counts()
        outcome = list(result.keys())[0]
        mapping = {"00": "石頭", "01": "剪刀", "10": "布"}
        if outcome in mapping:
            return mapping[outcome]

# --- UI 配置 ---
st.set_page_config(page_title="量子猜拳", layout="centered")

# 大按鈕 CSS
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        height: 100px;
        font-size: 24px !important;
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# 初始化 Session State
if 'win_count' not in st.session_state: st.session_state.win_count = 0
if 'history' not in st.session_state: st.session_state.history = []
if 'game_over' not in st.session_state: st.session_state.game_over = False

def judge(user, computer):
    if user == computer: return "平手"
    winning_rules = {"石頭": "剪刀", "剪刀": "布", "布": "石頭"}
    return "勝利" if winning_rules[user] == computer else "失敗"

# --- 遊戲畫面開始 ---
st.title("🌌 量子隨機猜拳戰")
msg_placeholder = st.empty()  # 訊息預留區

# 顯示目前分數
if st.session_state.win_count > 0:
    st.subheader(f"🔥 目前連勝：{st.session_state.win_count}")
else:
    st.subheader("⚔️ 開始挑戰量子電腦吧！")

# 核心邏輯：如果遊戲還沒結束，顯示出拳按鈕
if not st.session_state.game_over:
    col1, col2, col3 = st.columns(3)
    user_choice = None
    with col1:
        if st.button("🪨\n石頭"): user_choice = "石頭"
    with col2:
        if st.button("✂️\n剪刀"): user_choice = "剪刀"
    with col3:
        if st.button("📄\n布"): user_choice = "布"

    if user_choice:
        comp_choice = get_quantum_move()
        result = judge(user_choice, comp_choice)
        
        if result == "勝利":
            st.session_state.win_count += 1
            with msg_placeholder.container():
                st.success(f"🎉 你贏了！電腦出：{comp_choice}")
            st.balloons()
            st.rerun() # 立即重新整理以更新上方連勝數字
        elif result == "平手":
            with msg_placeholder.container():
                st.warning(f"🤝 平手！電腦也出：{comp_choice}")
        else:
            # 輸掉的處理
            st.session_state.history.append({
                "時間": datetime.now().strftime("%m/%d %H:%M"),
                "連勝紀錄": st.session_state.win_count
            })
            st.session_state.game_over = True
            with msg_placeholder.container():
                st.error(f"💀 輸了！電腦出：{comp_choice}")
            st.rerun() # 立即重新整理以隱藏按鈕

# 如果遊戲結束，顯示結算畫面與重新開始按鈕
else:
    st.error(f"遊戲結束！最終連勝紀錄為： {st.session_state.win_count}")
    if st.button("🔄 重新開始新賽局", use_container_width=True):
        st.session_state.win_count = 0
        st.session_state.game_over = False
        st.rerun()

# --- 歷史紀錄 ---
st.divider()
st.subheader("📜 歷史榮譽榜")
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    st.table(df.sort_values(by="連勝紀錄", ascending=False))
