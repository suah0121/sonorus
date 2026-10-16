import streamlit as st
import pandas as pd
import sqlite3
import time
from datetime import datetime

# ---------------------------------------------------------
# 1. 페이지 설정 및 UI 스타일
# ---------------------------------------------------------
st.set_page_config(
    page_title="SONORUS AUCTION | PIXEL QUEST",
    page_icon="🔨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
:root {
  --sky:#dcecff; --sky2:#f4f8ff; --navy:#203b78; --navy2:#294c91;
  --ink:#24365e; --muted:#687da7; --cream:#fffaf0; --cream2:#fff3d8;
  --line:#8fa8d5; --blue:#477be7; --blue2:#6d8ff4; --lav:#a99ae9;
  --gold:#f2b84b; --mint:#9bd9c7; --pink:#f3a6c7;
}
* { font-family:'Pretendard',sans-serif !important; }
.stApp {
  color:var(--ink) !important;
  background:
    radial-gradient(ellipse at 12% 8%,rgba(255,255,255,.94),transparent 28%),
    radial-gradient(ellipse at 90% 14%,rgba(173,211,255,.72),transparent 28%),
    linear-gradient(180deg,#d9eaff 0%,#eef5ff 45%,#e5efff 100%) !important;
}
.main .block-container { padding:1.25rem 1.25rem 3rem !important; max-width:1500px !important; }
header[data-testid="stHeader"], footer, div[data-testid="stSidebarCollapseButton"], section[data-testid="stSidebar"], .stDeployButton { display:none !important; }
[data-testid="stVerticalBlock"] { gap:.8rem; }
/* RPG window frames: creamy parchment, pixel-like double borders, soft toy-box shadows */
.app-header,.app-card,.countdown-box,div[data-testid="stForm"] {
  border:3px solid var(--line) !important; border-radius:7px !important;
  box-shadow:4px 4px 0 rgba(49,76,132,.18), inset 0 0 0 2px rgba(255,255,255,.9) !important;
}
.app-header {
  display:flex; justify-content:space-between; align-items:center; gap:16px; padding:18px 24px;
  background:linear-gradient(110deg,#233f83 0%,#315aa7 62%,#426fc1 100%) !important;
  border-color:#91c7ff !important; margin-bottom:18px; color:#fff !important;
}
.app-header-title { font-size:1.35rem; font-weight:950; color:#fff !important; display:flex; align-items:center; gap:12px; letter-spacing:.01em; text-shadow:2px 2px 0 #162d63; }
.badge-chip { display:inline-flex; align-items:center; justify-content:center; background:#fff0c9 !important; color:#70512a !important; border:2px solid #f0c36b; font-weight:850; font-size:.78rem; padding:8px 12px; border-radius:5px !important; white-space:nowrap; box-shadow:2px 2px 0 rgba(23,47,99,.2); }
.app-card { background:linear-gradient(145deg,#fffdf7,#fff5df) !important; padding:19px; margin-bottom:14px; border-color:#b5c5e2 !important; color:var(--ink) !important; }
.app-card-myteam { border-color:#7f9af0 !important; background:linear-gradient(145deg,#f0f4ff,#fff8e9) !important; box-shadow:4px 4px 0 rgba(64,93,163,.18), inset 0 0 0 2px #fff !important; }
.point-label { display:flex; align-items:center; min-height:1.35rem; margin:0 0 .35rem 0; line-height:1.2; color:#536b99 !important; font-weight:850 !important; }
.balance-field { width:100%; display:flex; flex-direction:column; gap:0; margin:0; padding:0; }
.point-chip { background:#fff1ce !important; color:#99631b !important; border:2px solid #f1cf85 !important; font-weight:950; padding:0 12px; border-radius:5px !important; font-size:.95rem; display:flex; align-items:center; justify-content:center; gap:7px; height:48px; width:100%; box-sizing:border-box; margin:0; white-space:nowrap; box-shadow:2px 2px 0 rgba(151,112,46,.12); }
.tag-blue { display:inline-block; background:#e4edff !important; color:#4264b3 !important; border:1px solid #a9bee9; font-weight:850; font-size:.75rem; padding:4px 8px; border-radius:4px !important; }
.stButton>button,div[data-testid="stFormSubmitButton"]>button,div[data-testid="stDownloadButton"]>button {
  background:linear-gradient(180deg,#8c80ed 0%,#655cce 100%) !important; color:#fff !important; font-weight:900 !important;
  border:2px solid #c2bbff !important; border-radius:5px !important; padding:.78rem 1rem !important; width:100% !important;
  box-shadow:3px 3px 0 rgba(53,66,131,.22) !important; transition:transform .12s ease,filter .12s ease !important;
}
.stButton>button:hover,div[data-testid="stFormSubmitButton"]>button:hover,div[data-testid="stDownloadButton"]>button:hover { filter:brightness(1.06); transform:translateY(-1px) !important; box-shadow:3px 4px 0 rgba(53,66,131,.22) !important; }
.stTextInput input,.stTextArea textarea,.stSelectbox div[data-baseweb="select"]>div,.stNumberInput input {
  background:#fffdf8 !important; color:#293b64 !important; border:2px solid #d5dfef !important; border-radius:5px !important; font-size:.95rem !important;
}
.stTextInput input:focus,.stTextArea textarea:focus,.stNumberInput input:focus { border-color:#8a9fe7 !important; box-shadow:0 0 0 2px rgba(138,159,231,.16) !important; }
.stTextInput input::placeholder,.stTextArea textarea::placeholder { color:#9aa9c5 !important; }
label { color:#536b99 !important; font-weight:850 !important; font-size:.9rem !important; }
div[data-testid="stCaptionContainer"] { color:var(--muted) !important; }
.stMarkdown,.stMarkdown p,.stMarkdown li,[data-testid="stMarkdownContainer"] { color:inherit; }
h1,h2,h3,h4 { color:#2c467d !important; letter-spacing:-.02em; }
h1,h2,h3 { text-shadow:1px 1px 0 rgba(255,255,255,.9); }
hr { border-color:#cbd8ee !important; margin:1.35rem 0 !important; }
.countdown-box { text-align:center; padding:42px 20px; background:linear-gradient(145deg,#fffdf7,#edf4ff) !important; border-color:#9db5e2 !important; margin:20px auto; max-width:680px; }
.countdown-box h2 { color:#2c467d !important; }
.countdown-num { font-family:'Press Start 2P',monospace !important; font-size:4.2rem; font-weight:900; color:#f0b84c !important; line-height:1.4; margin:18px 0; text-shadow:3px 3px 0 #e9d5a2; }
.stAlert { background:#fff9e9 !important; border:2px solid #e6c984 !important; border-radius:5px !important; color:#4b5f86 !important; }
div[data-testid="stForm"] { background:rgba(255,251,240,.96) !important; border-color:#c2cfe7 !important; padding:14px; }
div[data-testid="stDataFrame"],div[data-testid="stTable"] { background:#fffaf0 !important; }
/* Harmonize older inline card styles with the new pastel RPG palette */
[style*="background:#101426"],[style*="background: #101426"],[style*="background:#0d204d"],[style*="background: #0d204d"] { background:#fffaf0 !important; }
[style*="color:#EAF4FF"],[style*="color: #EAF4FF"],[style*="color:#A9C3EA"],[style*="color:#9BBBE8"],[style*="color:#53F4FF"] { color:#526b9b !important; }
@media(max-width:760px) { .app-header { padding:15px; align-items:flex-start; flex-direction:column; } .app-header-title { font-size:1rem; } .countdown-num { font-size:2.8rem; } .app-card { padding:14px; } }
</style>
""", unsafe_allow_html=True)

SVG_HAMMER = """<svg width="27" height="27" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M14.7 6.3L17.7 3.3C18.1 2.9 18.7 2.9 19.1 3.3L20.7 4.9C21.1 5.3 21.1 5.9 20.7 6.3L17.7 9.3M14.7 6.3L11.7 9.3M14.7 6.3L17.7 9.3M11.7 9.3L4.2 16.8C3.8 17.2 3.8 17.8 4.2 18.2L5.8 19.8C6.2 20.2 6.8 20.2 7.2 19.8L14.7 12.3M11.7 9.3L14.7 12.3" stroke="#53F4FF" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>"""
SVG_STAR = """<svg width="20" height="20" viewBox="0 0 24 24" fill="#FFD76A" xmlns="http://www.w3.org/2000/svg"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/></svg>"""

# ---------------------------------------------------------
# 2. SQLite DB 엔진
# ---------------------------------------------------------
DB_FILE = "auction_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS bids (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            user_team TEXT NOT NULL,
            target_team_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            feedback TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS app_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    c.execute("SELECT COUNT(*) FROM app_state WHERE key = 'phase'")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO app_state VALUES ('phase', 'prep')")
    conn.commit()
    conn.close()

init_db()

def get_teams():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM teams", conn)
    conn.close()
    return df

def add_team(name, title, description):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO teams (name, title, description) VALUES (?, ?, ?)",
            (name, title, description)
        )
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def update_team_info(team_id, title, description):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "UPDATE teams SET title = ?, description = ? WHERE id = ?",
        (title, description, team_id)
    )
    conn.commit()
    conn.close()

def get_bids():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM bids", conn)
    conn.close()
    return df

def add_bid(user_name, user_team, target_team_id, amount, feedback):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute(
        """INSERT INTO bids
        (user_name, user_team, target_team_id, amount, feedback, created_at)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (user_name, user_team, target_team_id, amount, feedback, now_str)
    )
    conn.commit()
    conn.close()

def get_state(key, default="prep"):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT value FROM app_state WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else default

def set_state(key, value):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("REPLACE INTO app_state (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()

def reset_all_data():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM teams")
    c.execute("DELETE FROM bids")
    c.execute("REPLACE INTO app_state (key, value) VALUES ('phase', 'prep')")
    c.execute("DELETE FROM app_state WHERE key = 'cd_start'")
    c.execute("DELETE FROM app_state WHERE key = 'reveal_start'")
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# 3. 실시간 동기화 및 카운트다운
# ---------------------------------------------------------
@st.fragment(run_every=1)
def live_sync_and_countdown():
    current_phase = get_state("phase", "prep")
    last_phase = st.session_state.get("last_synced_phase", None)

    if last_phase != current_phase:
        st.session_state["last_synced_phase"] = current_phase
        st.rerun()

    if current_phase == "countdown":
        try:
            cd_start = float(get_state("cd_start", time.time()))
        except (ValueError, TypeError):
            cd_start = time.time()

        remaining = max(0, int(5 - (time.time() - cd_start)))
        if remaining > 0:
            st.markdown(f"""
                <div class="countdown-box">
                    <h2 style="color:#EAF4FF; margin:0; font-size:1.5rem;">🔨 프로젝트 경매가 곧 시작됩니다!</h2>
                    <p style="color:#9BBBE8; font-size:1.05rem; margin-top:8px;">다른 팀의 프로젝트를 살펴보고 응원할 준비를 해주세요.</p>
                    <div class="countdown-num">{remaining}</div>
                    <p style="color:#53F4FF; font-weight:800; font-size:1.1rem;">초 후 실시간 입찰이 시작됩니다.</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            set_state("phase", "auction")
            st.rerun()

    elif current_phase == "result_reveal":
        try:
            reveal_start = float(get_state("reveal_start", time.time()))
        except (ValueError, TypeError):
            reveal_start = time.time()

        remaining = max(0, int(5 - (time.time() - reveal_start)))
        if remaining > 0:
            st.markdown(f"""
                <div class="countdown-box" style="border-color:#FF8ED8;">
                    <h2 style="color:#EAF4FF; margin:0; font-size:1.5rem;">🎉 프로젝트 경매 마감!</h2>
                    <p style="color:#9BBBE8; font-size:1.05rem; margin-top:8px;">팀별 투자 결과를 정리하고 있습니다.</p>
                    <div class="countdown-num" style="color:#FFD76A;">{remaining}</div>
                    <p style="color:#53F4FF; font-weight:800; font-size:1.1rem;">초 후 최종 결과가 공개됩니다.</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            set_state("phase", "finished")
            st.rerun()

# ---------------------------------------------------------
# 4. 메인 대시보드
# ---------------------------------------------------------
current_phase = get_state("phase", "prep")

phase_badge_text = {
    "prep": "STAGE 1 : 프로젝트 등록",
    "countdown": "경매 시작 카운트다운",
    "auction": "STAGE 2 : 실시간 경매 진행 중",
    "result_reveal": "결과 집계 중",
    "finished": "STAGE 3 : 최종 투자 결과"
}.get(current_phase, "STAGE 1")

st.markdown(f"""
    <div class="app-header">
        <div class="app-header-title">{SVG_HAMMER} SONORUS ✦ 아이디어 경매전</div>
        <div class="badge-chip">{phase_badge_text}</div>
    </div>
""", unsafe_allow_html=True)

teams_df = get_teams()
team_options = teams_df["name"].tolist() if not teams_df.empty else []

col_p1, col_p2, col_p3, col_p4 = st.columns([1.5, 1.5, 1.5, 2], vertical_alignment="bottom")

with col_p1:
    user_name = st.text_input(
        "참가자 이름",
        value=st.session_state.get("user_name", ""),
        placeholder="예: 김소노"
    )
    if user_name:
        st.session_state["user_name"] = user_name

with col_p2:
    user_team = st.selectbox("내 소속 팀", options=["팀 선택"] + team_options, index=0)
    if user_team != "팀 선택":
        st.session_state["user_team"] = user_team

INITIAL_BALANCE = 1000000
bids_df = get_bids()

if user_name:
    my_bids = bids_df[bids_df["user_name"] == user_name]
    used_amount = my_bids["amount"].sum() if not my_bids.empty else 0
    my_balance = INITIAL_BALANCE - used_amount
else:
    my_balance = INITIAL_BALANCE

with col_p3:
    # 라벨과 포인트 칩을 하나의 HTML 블록으로 묶어 Streamlit 요소 간 간격 때문에
    # 포인트 칸만 아래로 밀리는 현상을 방지합니다.
    st.markdown(
        f"""
        <div class="balance-field">
            <div class="point-label">보유 포인트</div>
            <div class="point-chip">{SVG_STAR} {my_balance:,} P</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_p4:
    admin_pwd = st.text_input("관리자 암호", type="password", placeholder="관리자 암호")
    is_admin = (admin_pwd == "sonorus123")

if is_admin:
    st.success("🔒 관리자 권한 인증 완료")
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if current_phase == "prep":
            if st.button("🚀 경매 시작 (5초 카운트다운)", use_container_width=True):
                set_state("cd_start", time.time())
                set_state("phase", "countdown")
                st.rerun()
        elif current_phase in ["auction", "countdown"]:
            if st.button("🚨 경매 마감 및 결과 발표", use_container_width=True):
                set_state("reveal_start", time.time())
                set_state("phase", "result_reveal")
                st.rerun()
        elif current_phase in ["finished", "result_reveal"]:
            if st.button("🔄 준비 화면으로 복귀", use_container_width=True):
                set_state("phase", "prep")
                st.rerun()

    with c_btn2:
        if st.button("💥 전체 데이터 초기화", use_container_width=True):
            reset_all_data()
            st.rerun()

st.markdown("---")

# ---------------------------------------------------------
# STAGE 1: 프로젝트 활동 등록 및 소개
# ---------------------------------------------------------
if current_phase == "prep":
    st.subheader("🗺️ 오늘의 퀘스트 : 프로젝트 활동 소개")
    st.caption("우리 팀의 탐구 여정을 소개하고, 다른 팀의 응원 포인트와 피드백을 받아보세요!")

    col_create, col_teams = st.columns([1, 2])

    with col_create:
        st.markdown("<div class='app-card'>", unsafe_allow_html=True)
        st.markdown("### 📜 퀘스트 기록 등록")
        with st.form(key="add_team_form"):
            new_team_name = st.text_input("팀 이름", placeholder="예: 소노루스 1팀")
            new_team_title = st.text_input("프로젝트명", placeholder="예: 온라인 소통과 청소년의 감정 탐구")
            new_team_desc = st.text_area(
                "프로젝트 활동 내용",
                placeholder="탐구 동기, 진행 과정, 주요 활동 및 결과를 다른 팀이 이해할 수 있도록 소개해 주세요.",
                height=150
            )
            add_btn = st.form_submit_button("프로젝트 등록하기", use_container_width=True)

            if add_btn:
                if not new_team_name.strip() or not new_team_title.strip() or not new_team_desc.strip():
                    st.error("모든 항목을 입력해야 합니다.")
                else:
                    if add_team(new_team_name.strip(), new_team_title.strip(), new_team_desc.strip()):
                        st.success(f"'{new_team_name}' 프로젝트 등록 완료!")
                        st.rerun()
                    else:
                        st.error("이미 존재하는 팀 이름입니다.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_teams:
        st.markdown("### 🧳 등록된 프로젝트 목록")
        if teams_df.empty:
            st.info("아직 등록된 프로젝트가 없습니다. 왼쪽에서 우리 팀의 활동을 소개해 주세요.")
        else:
            for _, row in teams_df.iterrows():
                is_my_team = (user_team == row["name"])
                card_class = "app-card app-card-myteam" if is_my_team else "app-card"
                badge = "<span class='tag-blue'>우리 팀</span>" if is_my_team else ""

                st.markdown(f"""
                    <div class="{card_class}">
                        <div style="display:flex; justify-content:space-between; align-items:center; gap:10px; margin-bottom:10px;">
                            <span style="font-weight:800; color:#53F4FF; font-size:1.02rem;">{row['name']} {badge}</span>
                            <span class="tag-blue">프로젝트 소개</span>
                        </div>
                        <div style="font-size:1.15rem; font-weight:850; color:#EAF4FF; margin-bottom:8px;">
                            {row['title']}
                        </div>
                        <div style="color:#A9C3EA; font-size:0.95rem; line-height:1.7; white-space:pre-wrap;">
                            {row['description']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                if is_admin or is_my_team:
                    with st.form(key=f"edit_form_{row['id']}"):
                        edit_title = st.text_input("프로젝트명 수정", value=row["title"], key=f"title_{row['id']}")
                        edit_desc = st.text_area(
                            "프로젝트 활동 내용 수정",
                            value=row["description"],
                            key=f"desc_{row['id']}"
                        )
                        if st.form_submit_button("✍️ 수정 내용 저장", use_container_width=True):
                            update_team_info(row["id"], edit_title, edit_desc)
                            st.success("프로젝트 소개가 수정되었습니다.")
                            st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# STAGE 1.5: 5초 카운트다운
# ---------------------------------------------------------
elif current_phase == "countdown":
    live_sync_and_countdown()

# ---------------------------------------------------------
# STAGE 2: 실시간 프로젝트 경매
# ---------------------------------------------------------
elif current_phase == "auction":
    live_sync_and_countdown()
    st.subheader("⚔️ 실시간 프로젝트 경매")
    st.caption("다른 팀의 프로젝트 활동에 포인트를 투자하고, 도움이 되는 피드백을 남겨보세요.")

    col_auction, col_feed = st.columns([2, 1])

    with col_auction:
        if teams_df.empty:
            st.warning("등록된 프로젝트가 없습니다.")
        else:
            for _, row in teams_df.iterrows():
                is_my_team = (user_team == row["name"])
                team_bids = bids_df[bids_df["target_team_id"] == row["id"]]
                total_funding = team_bids["amount"].sum() if not team_bids.empty else 0

                card_class = "app-card app-card-myteam" if is_my_team else "app-card"
                badge_html = "<span class='tag-blue'>우리 팀</span>" if is_my_team else ""

                st.markdown(f"""
                    <div class="{card_class}">
                        <div style="display:flex; justify-content:space-between; align-items:center; gap:10px; margin-bottom:8px;">
                            <span style="font-weight:800; color:#53F4FF; font-size:1.02rem;">{row['name']} {badge_html}</span>
                            <span class="point-chip" style="font-size:0.82rem; padding:5px 10px; height:auto; width:auto;">누적 투자 {total_funding:,} P</span>
                        </div>
                        <div style="font-size:1.2rem; font-weight:900; color:#EAF4FF; margin-bottom:8px;">{row['title']}</div>
                        <div style="color:#A9C3EA; font-size:0.95rem; line-height:1.7; margin-bottom:8px; white-space:pre-wrap;">{row['description']}</div>
                    </div>
                """, unsafe_allow_html=True)

                if is_my_team:
                    st.caption("우리 팀 프로젝트에는 입찰할 수 없습니다.")
                else:
                    with st.form(key=f"bid_form_{row['id']}"):
                        bid_amount = st.number_input(
                            "투자 포인트 설정 (P)",
                            min_value=10000,
                            max_value=max(10000, my_balance),
                            step=50000,
                            key=f"amount_{row['id']}"
                        )
                        feedback = st.text_area(
                            "투자 이유 및 프로젝트 피드백 (필수)",
                            placeholder="인상 깊었던 점이나 더 발전하면 좋을 점을 적어주세요.",
                            key=f"feedback_{row['id']}"
                        )
                        submit_bid = st.form_submit_button("포인트 투자하기", use_container_width=True)

                        if submit_bid:
                            if not user_name or user_team == "팀 선택":
                                st.error("상단에서 참가자 이름과 소속 팀을 선택하세요.")
                            elif bid_amount > my_balance:
                                st.error("포인트가 부족합니다.")
                            elif not feedback.strip():
                                st.error("프로젝트 피드백을 작성해야 합니다.")
                            else:
                                add_bid(user_name, user_team, int(row["id"]), int(bid_amount), feedback.strip())
                                st.success(f"{bid_amount:,} P 투자가 완료되었습니다!")
                                st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)

    with col_feed:
        st.subheader("⚡ 실시간 투자 현황")
        if bids_df.empty:
            st.info("아직 제출된 투자 내역이 없습니다.")
        else:
            for _, bid in bids_df.sort_values(by="id", ascending=False).head(10).iterrows():
                target_rows = teams_df[teams_df["id"] == bid["target_team_id"]]
                target_name = target_rows["name"].values[0] if not target_rows.empty else "프로젝트"

                st.markdown(f"""
                    <div style="background:#101426; border:1px solid #29314F; padding:14px; border-radius:3px; margin-bottom:10px; box-shadow:0 0 14px rgba(0,245,255,0.05);">
                        <div style="font-size:0.85rem; color:#9BBBE8; display:flex; justify-content:space-between; gap:8px;">
                            <span><strong style="color:#EAF4FF;">{bid['user_name']}</strong> ({bid['user_team']})</span>
                            <span class="badge-chip">투자 완료</span>
                        </div>
                        <div style="font-size:1.05rem; font-weight:900; color:#53F4FF; margin:8px 0;">
                            ➜ {target_name} · {bid['amount']:,} P
                        </div>
                        <div style="color:#A9C3EA; font-size:0.9rem; line-height:1.6;">“{bid['feedback']}”</div>
                    </div>
                """, unsafe_allow_html=True)

# ---------------------------------------------------------
# STAGE 2.5: 결과 연출 화면
# ---------------------------------------------------------
elif current_phase == "result_reveal":
    live_sync_and_countdown()

# ---------------------------------------------------------
# STAGE 3: 경매 마감 및 결과 리포트
# ---------------------------------------------------------
elif current_phase == "finished":
    live_sync_and_countdown()
    st.subheader("🏆 퀘스트 클리어 결과")

    funding_summary = []
    for _, row in teams_df.iterrows():
        team_bids = bids_df[bids_df["target_team_id"] == row["id"]]
        total_funding = team_bids["amount"].sum() if not team_bids.empty else 0
        funding_summary.append({
            "팀": row["name"],
            "프로젝트": row["title"],
            "총 투자액": total_funding
        })

    summary_df = (
        pd.DataFrame(funding_summary).sort_values(by="총 투자액", ascending=False)
        if funding_summary else pd.DataFrame()
    )

    st.markdown("### 🥇 프로젝트 투자 순위")
    if not summary_df.empty:
        for idx, row in summary_df.reset_index(drop=True).iterrows():
            rank = idx + 1
            st.markdown(f"""
                <div class="app-card" style="border-left:5px solid #8D86E7;">
                    <div style="display:flex; justify-content:space-between; align-items:center; gap:12px;">
                        <span style="font-size:1.05rem; font-weight:800; color:#EAF4FF;">{rank}위 · {row['팀']} — {row['프로젝트']}</span>
                        <span class="point-chip" style="height:auto; width:auto; padding:8px 12px;">{row['총 투자액']:,} P</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 💎 가장 적극적으로 투자한 참가자")
    if not bids_df.empty:
        investor_df = bids_df.groupby(["user_name", "user_team"])["amount"].sum().reset_index()
        investor_df = investor_df.sort_values(by="amount", ascending=False)

        for idx, row in investor_df.reset_index(drop=True).head(3).iterrows():
            rank = idx + 1
            st.markdown(f"""
                <div style="background:#101426; padding:15px; border-radius:3px; margin-bottom:10px; border:1px solid #29314F; display:flex; justify-content:space-between; align-items:center; gap:12px;">
                    <span><strong style="color:#53F4FF;">{rank}위</strong> · {row['user_name']} ({row['user_team']})</span>
                    <span style="font-weight:900; color:#EAF4FF;">총 {row['amount']:,} P 투자</span>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📥 프로젝트 피드백 다운로드")
    if not bids_df.empty:
        csv_data = bids_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📄 전체 프로젝트 피드백 CSV 다운로드",
            data=csv_data,
            file_name="sonorus_project_feedback.csv",
            mime="text/csv"
        )
