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

# --- UI 配置 ---
st.set_page_config(page_title="量子猜拳", layout="centered")

# 大按鈕 CSS, 按鈕左右排列
st.markdown("""
    <style>

    /* 2. 強制水平容器寬度 100% 且完全移除內部間距 */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        width: 100% !important;
        gap: 0px !important; /* 這是按鈕間唯一的間隔，可設為 0px 或 4px */
        padding: 0px !important;
    }

    /* 3. 移除每一個 Column 的預設間距 */
    div[data-testid="column"] {
        padding: 0px !important;
        margin: 0px !important;
        width: calc(33.33% - 2.66px) !important; /* 精確計算，確保不爆版 */
        flex: 1 1 auto !important;
        min-width: 0px !important;
    }

    /* 4. 按鈕外框修正，移除不必要的 Margin */
    div.stButton {
        padding: 0px !important;
        margin: 0px !important;
    }

    div.stButton > button {
        width: 100% !important;
        height: 70px !important;
        font-size: 18px !important;
        margin: 0px !important;
        border-radius: 8px;
        /* 增加邊框讓按鈕界線明顯（因為留白去除了） */
        border: 1px solid #ddd !important;
    }

    /* 手機版微調 */
    @media (max-width: 480px) {
        div.stButton > button {
            height: 60px !important;
            font-size: 16px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# 初始化 Session State
if 'win_count' not in st.session_state: st.session_state.win_count = 0
if 'history' not in st.session_state: st.session_state.history = []
if 'game_over' not in st.session_state: st.session_state.game_over = False
if 'is_balloon' not in st.session_state: st.session_state.is_balloon = 0
if 'comp_choice' not in st.session_state: st.session_state.comp_choice = ""
if 'times' not in st.session_state: st.session_state.times = 0

def judge(user, computer):
    if user == computer: return "平手"
    winning_rules = {"石頭": "剪刀", "剪刀": "布", "布": "石頭"}
    return "勝利" if winning_rules[user] == computer else "失敗"

# --- 遊戲畫面開始 ---
st.title("🌌 量子猜拳")
st.write("💪 以拳法的動作和理論為載體，去驗證和體悟「道」的真諦吧 👊")
msg_placeholder = st.empty()

loser_rules = {"石頭": "布", "剪刀": "石頭", "布": "剪刀"}

if st.session_state.win_count > 0:
    if st.session_state.game_over == False:
        st.subheader(f"🔥 目前已經連勝 {st.session_state.win_count} 次!!! 🔥")
        if st.session_state.is_balloon > 0:
            st.session_state.is_balloon = 0
            st.balloons()
            with msg_placeholder.container():
                st.success(f"第 {st.session_state.times} 次出拳\n\n恭喜🎉 你出拳 {loser_rules[st.session_state.comp_choice]} 贏了！量子電腦出拳 {st.session_state.comp_choice}")
else:
    if st.session_state.game_over == False:
        st.subheader("⚔️ 開始挑戰量子電腦吧！")

# 如果遊戲還沒結束，顯示出拳按鈕
if not st.session_state.game_over:
    # 這裡的 columns 在手機上會被上面的 CSS 強制水平排列
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
        
        st.session_state.times += 1
        if result == "勝利":
            st.session_state.win_count += 1
            #with msg_placeholder.container():
            #    st.success(f"🎉 贏了！電腦出：{comp_choice}")
            # st.balloons()
            st.session_state.comp_choice = comp_choice
            st.session_state.is_balloon = 1
            st.rerun()
        elif result == "平手":
            with msg_placeholder.container():
                st.warning(f"平手🤝 你和量子電腦都出拳 {comp_choice}")
        else:
            st.session_state.history.append({
                "時間": datetime.now().strftime("%m/%d %H:%M:%S"),
                "連勝紀錄": st.session_state.win_count
            })
            st.session_state.game_over = True
            with msg_placeholder.container():
                st.error(f"輸了💀 量子電腦出拳 {comp_choice}")
            st.rerun()

else:
    # 失敗畫面：按鈕已隱藏
    with msg_placeholder.container():
        st.error(f"第 {st.session_state.times} 次出拳\n\n輸了💀 你出拳 {loser_rules[st.session_state.comp_choice]} 贏了！量子電腦出拳 {st.session_state.comp_choice}")
    st.session_state.times = 0
    win_count_state = ""
    if st.session_state.win_count >= 21:
        win_count_state = "太神了! 看來你以拳證道稱霸此時空了🎉 "
    elif st.session_state.win_count >= 15:
        win_count_state = "看來進入大成之境, 繼續朝著大道合一前行吧🎉 "
    elif st.session_state.win_count >= 12:
        win_count_state = "不錯喔, 漸入佳境, 是不是有抓到感覺了🎉 "
    elif st.session_state.win_count >= 10:
        win_count_state = "在猜拳之道, 小有所成🎉 "
    elif st.session_state.win_count >= 8:
        win_count_state = "看來悟到了些皮毛🎉 "
    elif st.session_state.win_count >= 1:
        win_count_state = "還可以, 不到一天就突破至煉氣期🎉 "
    elif st.session_state.win_count == 0:
        win_count_state = "看你這根骨, 還是饕餮之道比較適合你😋 "
    st.error(f"{win_count_state}\n\n此回合猜拳連勝量子電腦 {st.session_state.win_count} 次")
    if st.button("🔄 重新開始新的時空\n\n再次和量子電腦較勁一輪吧", use_container_width=True):
        st.session_state.win_count = 0
        st.session_state.game_over = False
        st.rerun()

# --- 歷史紀錄 ---
st.divider()
st.subheader("📜 星橋管理局 - 記憶水晶")
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    df.index += 1
    st.table(df.sort_values(by="連勝紀錄", ascending=False))