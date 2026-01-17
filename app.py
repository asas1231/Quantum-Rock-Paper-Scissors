import streamlit as st
import pandas as pd
from datetime import datetime
from qiskit import QuantumCircuit
from qiskit_aer import Aer

# --- 初始化量子後端 ---
backend = Aer.get_backend('qasm_simulator')

def get_quantum_move():
    # 功能: 透過量子電路產生隨機出拳
    # input: 無
    # output: 字串 ("石頭", "剪刀", "布")
    qc = QuantumCircuit(2, 2)
    qc.h([0, 1])
    qc.measure([0, 1], [0, 1])
    
    job = backend.run(qc, shots=1)
    result = job.result().get_counts()
    
    while True:
        outcome = list(result.keys())[0] 
        mapping = {"00": "石頭", "01": "剪刀", "10": "布"}
        
        if outcome in mapping:
            return mapping[outcome]
        else:
            job = backend.run(qc, shots=1)
            result = job.result().get_counts()

def judge(user, computer):
    # 功能: 判斷猜拳勝負
    if user == computer: return "平手"
    winning_rules = {"石頭": "剪刀", "剪刀": "布", "布": "石頭"}
    return "勝利" if winning_rules[user] == computer else "失敗"

# --- UI 配置 ---
st.set_page_config(page_title="量子猜拳", layout="centered")

# 【關鍵修正點】全新 CSS：擴充標題置中支援 (h1-h6)
st.markdown("""
    <style>
    /* 1. 全局容器優化 */
    .block-container {
        padding-top: 3.5rem !important;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 600px;
    }

    /* 2. 按鈕樣式：保留全寬度與卡片視覺 */
    div.stButton > button {
        height: 80px !important;
        font-size: 22px !important;
        font-weight: 600 !important;
        margin-bottom: 12px !important;
        
        border-radius: 16px !important;
        border: 1px solid #e0e0e0 !important;
        background-color: white !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: transform 0.1s;
    }

    div.stButton > button:active {
        transform: scale(0.98);
        background-color: #f8f9fa !important;
        box-shadow: none !important;
    }

    /* 3. 文字排版：強制全域置中 */
    
    /* 【關鍵修正點】針對 h1 到 h6 所有標題層級設定置中 */
    h1, h2, h3, h4, h5, h6 {
        text-align: center !important;
    }
    
    /* 針對主標題 h1 的特別微調 */
    h1 {
        font-size: 1.8rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    .stMarkdown p {
        text-align: center !important;
        color: #666;
    }

    /* 4. 狀態通知框 (Alerts) 內容置中 */
    div[data-testid="stAlert"] > div {
        display: flex;
        justify-content: center; 
        text-align: center;      
    }
    
    /* 5. 隱藏水平 Block 間距干擾 */
    div[data-testid="stHorizontalBlock"] {
        gap: 0px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# // 功能: 設定 CSS 樣式
# // input: CSS 字串
# // output: 渲染後的 HTML/CSS
# // 其他補充: 
# // 1. 新增 h1, h2, h3... 的共用 text-align: center 規則，解決 Markdown 標題靠左問題。
# // 2. 維持之前的按鈕樣式與版面設定。

# --- Session State 初始化 ---
if 'win_count' not in st.session_state: st.session_state.win_count = 0
if 'history' not in st.session_state: st.session_state.history = []
if 'game_over' not in st.session_state: st.session_state.game_over = False
if 'times' not in st.session_state: st.session_state.times = 0
if 'last_result' not in st.session_state: st.session_state.last_result = None 
if 'comp_choice' not in st.session_state: st.session_state.comp_choice = ""

# --- 輔助邏輯字典 ---
loser_rules = {"石頭": "布", "剪刀": "石頭", "布": "剪刀"}

# --- 標題區 ---
st.title("🌌 量子猜拳")

# // 【關鍵修正點】三段式狀態判斷：初始 -> 結束 -> 進行中
# // 功能: 依據遊戲進度與勝負狀態切換顯示內容
# // input: st.session_state.times, st.session_state.game_over
# // output: 對應的 Markdown 文案
if st.session_state.times == 0:
    # 初始狀態：顯示原本的 Flavor Text
    st.markdown("💪 以拳法的動作和理論為載體💪\n\n👊去驗證和體悟「道」的真諦吧 👊") 

elif st.session_state.game_over:
    # 【關鍵修正點】遊戲結束狀態：顯示最終成績，不再顯示「第 X 回合」
    st.markdown(f"#### 🏁 挑戰結束 | 最終連勝：{st.session_state.win_count}")
    st.markdown("繼續挑戰，連勝次數越高會有不同獎勵喔！")

else:
    # 戰鬥進行狀態：顯示當前回合
    st.markdown(f"### 第 {st.session_state.times + 1} 回合 | 連勝：{st.session_state.win_count} 次")
    st.markdown("挑戰完成可以兌換小禮物🎁")

# --- 狀態儀表板 (Dashboard) ---
# 使用 st.info/success/error 區塊作為狀態顯示，在手機上非常清晰
if st.session_state.game_over:
    st.error(f"💀 **敗北！** (第 {st.session_state.times} 回合)\n\n對手出：{st.session_state.comp_choice} | 你出：{loser_rules[st.session_state.comp_choice]}")
elif st.session_state.last_result == "平手":
    st.warning(f"⚠️ **平手** (對手也出{st.session_state.comp_choice})\n\n氣息未定，請再次出拳！")
elif st.session_state.last_result == "勝利":
    st.success(f"🎉 **勝利！連勝 {st.session_state.win_count} 場**\n\n對手出：{st.session_state.comp_choice}，趁勝追擊！")
else:
    st.info("⚔️ **戰鬥準備**：請選擇你的招式")

st.write("") # 留一點空白

# --- 遊戲控制區 (垂直堆疊佈局) ---
# --- 遊戲控制區 (垂直堆疊佈局) ---
if not st.session_state.game_over:
    # // 【關鍵修正點】不使用 st.columns，直接呼叫按鈕並開啟 use_container_width=True
    
    user_choice = None
    
    # // 功能: 顯示石頭按鈕
    # // input: Label, use_container_width=True
    # // output: Boolean (是否被點擊)
    if st.button("🪨　石　頭", use_container_width=True): 
        user_choice = "石頭"
    
    # // 功能: 顯示剪刀按鈕
    if st.button("✂️　剪　刀", use_container_width=True): 
        user_choice = "剪刀"
    
    # // 功能: 顯示布按鈕
    if st.button("📄　　布　", use_container_width=True): 
        user_choice = "布"

    if user_choice:
        comp_choice = get_quantum_move()
        result = judge(user_choice, comp_choice)
        
        st.session_state.times += 1
        st.session_state.comp_choice = comp_choice
        st.session_state.last_result = result

        if result == "勝利":
            st.session_state.win_count += 1
            st.balloons()
            st.rerun()
            
        elif result == "平手":
            st.rerun()
            
        else: # 失敗
            st.session_state.history.append({
                "時間": datetime.now().strftime("%m/%d %H:%M:%S"),
                "連勝": st.session_state.win_count,
            })
            st.session_state.game_over = True
            st.rerun()

else:
    # --- 遊戲結束評語區 ---
    st.session_state.times = 0
    win_count_state = ""
    wc = st.session_state.win_count
    
    if wc >= 21: win_count_state = "太神了！看來你以拳證道稱霸此時空了🎉"
    elif wc >= 15: win_count_state = "看來進入大成之境，繼續朝著大道合一前行吧🎉"
    elif wc >= 12: win_count_state = "不錯喔，漸入佳境，是不是有抓到感覺了🎉"
    elif wc >= 10: win_count_state = "在猜拳之道，小有所成🎉 "
    elif wc >= 8: win_count_state = "看來悟到了些皮毛🎉"
    elif wc >= 1: win_count_state = "還可以，不到一天就突破至煉氣期🎉"
    elif wc == 0: win_count_state = "看你這根骨，還是饕餮之道比較適合你😋"
        
    st.error(f"{win_count_state}") # f"{win_count_state}\n\n此回合連勝 {wc} 次"
    
    if st.button("🔄 重新開始新的時空 🔄\n\n再次和量子電腦較勁一輪吧", use_container_width=True):
        st.session_state.win_count = 0
        st.session_state.game_over = False
        st.session_state.last_result = None
        st.session_state.comp_choice = ""
        st.rerun()

# --- 歷史紀錄區 ---
st.divider()
st.caption("📜 星橋管理局 - 記憶水晶")
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    # 使用 st.dataframe 並隱藏索引，比 table 更適合手機閱讀
    st.dataframe(
        df.sort_index(ascending=False), 
        use_container_width=True,
        hide_index=True
    )