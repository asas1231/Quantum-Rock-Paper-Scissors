import streamlit as st
import pandas as pd
from datetime import datetime

# 修正後的 Qiskit 引入方式
from qiskit import QuantumCircuit
from qiskit_aer import Aer  # 注意這裡的改變

# --- 初始化量子後端 ---
backend = Aer.get_backend('qasm_simulator')

def get_quantum_move():
    """透過量子電路產生隨機出拳"""
    qc = QuantumCircuit(2, 2)
    qc.h([0, 1])  # 施加 Hadamard Gate
    qc.measure([0, 1], [0, 1])
    
    # 修正 Qiskit 1.0+ 的執行語法
    job = backend.run(qc, shots=1) 
    result = job.result().get_counts()
    
    while True:
        outcome = list(result.keys())[0] 
        mapping = {"00": "石頭", "01": "剪刀", "10": "布"}
        
        if outcome in mapping:
            return mapping[outcome]
        else:
            # 如果抽到 11，重新跑一次電路
            job = backend.run(qc, shots=1)
            result = job.result().get_counts()

# --- 網頁配置與自定義 CSS (讓按鈕變大) ---
st.set_page_config(page_title="量子猜拳大賽", layout="centered")

st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        height: 100px;
        font-size: 24px !important;
        font-weight: bold;
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🌌 量子隨機猜拳戰")

# 初始化狀態
if 'win_count' not in st.session_state:
    st.session_state.win_count = 0
if 'history' not in st.session_state:
    st.session_state.history = []
if 'game_over' not in st.session_state:
    st.session_state.game_over = False

def judge(user, computer):
    if user == computer: return "平手"
    winning_rules = {"石頭": "剪刀", "剪刀": "布", "布": "石頭"}
    return "勝利" if winning_rules[user] == computer else "失敗"

# --- 遊戲邏輯與 UI ---

# 1. 建立訊息預留區 (確保訊息出現在按鈕上方)
msg_placeholder = st.empty()

if not st.session_state.game_over:
    st.subheader(f"目前連勝次數： {st.session_state.win_count}")
    
    # 2. 按鈕並排佈局
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
        
        # 將結果顯示在預留區
        with msg_placeholder.container():
            st.info(f"你出：{user_choice} | 量子電腦出：{comp_choice}")
            if result == "勝利":
                st.success("🎉 你贏了！量子態站在你這邊！")
                st.session_state.win_count += 1
                st.subheader(f"目前連勝次數： {st.session_state.win_count}")
                st.balloons()
            elif result == "平手":
                st.warning("🤝 平手！再試一次。")
            else:
                st.error("💀 你輸了！遊戲結束。")
                st.session_state.history.append({
                    "時間": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "連勝紀錄": st.session_state.win_count
                })
                st.session_state.game_over = True
                # 注意：這裡不立刻 rerun，讓玩家看清楚最後一球
                if st.button("點擊確認結果"): st.rerun()

else:
    st.error(f"遊戲結束！最終連勝：{st.session_state.win_count}")
    if st.button("🔄 重新開始挑戰", use_container_width=True):
        st.session_state.win_count = 0
        st.session_state.game_over = False
        st.rerun()

# --- 歷史紀錄 ---
st.divider()
st.subheader("📜 歷史榮譽榜")
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    st.table(df.sort_values(by="連勝紀錄", ascending=False))