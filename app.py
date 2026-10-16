
import streamlit as st
import pandas as pd
import sqlite3
import time
from datetime import datetime

# ---------------------------------------------------------
# 1. 페이지 설정 및 SONORUS 디자인 시스템
# ---------------------------------------------------------
st.set_page_config(
    page_title="SONORUS AUCTION",
    page_icon="🔨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

:root {
    --ink: #292943;
    --muted: #85849B;
    --purple: #7771C9;
    --purple-dark: #625BAF;
    --lavender: #F0EDFA;
    --paper: #FFFFFF;
    --canvas: #F7F6FA;
    --line: #E9E6F0;
    --gold: #B98B46;
}

html, body, [class*="css"] {
    font-family: 'Pretendard', sans-serif !important;
}

.stApp {
    background:
        radial-gradient(ellipse at 0% 0%, #EEEAF9 0%, transparent 42%),
        linear-gradient(180deg, #F8F7FB 0%, #F5F6FA 100%) !important;
    color: var(--ink) !important;
}

.main .block-container {
    max-width: 1320px !important;
    padding: 2.2rem 2rem 4rem !important;
}

header[data-testid="stHeader"],
footer,
div[data-testid="stSidebarCollapseButton"],
section[data-testid="stSidebar"],
.stDeployButton {
    display: none !important;
}

/* Typography */
h1, h2, h3 {
    color: var(--ink) !important;
    letter-spacing: -0.045em !important;
    font-weight: 750 !important;
}
h1 { font-size: 2rem !important; }
h2 { font-size: 1.55rem !important; }
h3 { font-size: 1.2rem !important; }

p { line-height: 1.75; }

[data-testid="stCaptionContainer"] p {
    color: var(--muted) !important;
    font-size: 0.9rem !important;
}

/* Header */
.sonorus-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    padding: 25px 30px;
    margin-bottom: 26px;
    background: rgba(255,255,255,0.88);
    border: 1px solid rgba(224,220,239,0.9);
    border-radius: 22px;
    box-shadow: 0 8px 30px rgba(54,46,94,0.045);
}

.app-header-title {
    display: flex;
    align-items: center;
    gap: 12px;
    color: var(--ink);
    font-size: 1.65rem;
    font-weight: 850;
    letter-spacing: -0.055em;
}

.badge-chip {
    display: inline-block;
    padding: 7px 13px;
    border-radius: 999px;
    background: #F0EDFA;
    color: #7169B5;
    font-size: 0.78rem;
    font-weight: 750;
    white-space: nowrap;
}

/* Buttons */
.stButton > button,
div[data-testid="stFormSubmitButton"] > button,
.stDownloadButton > button {
    min-height: 44px;
    padding: 0.72rem 1.15rem !important;
    border: 1px solid #7771C9 !important;
    border-radius: 12px !important;
    background: #7771C9 !important;
    color: #FFFFFF !important;
    font-size: 0.94rem !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 10px rgba(119,113,201,0.12) !important;
    transition: background .18s ease, transform .18s ease,
                box-shadow .18s ease !important;
}

.stButton > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover,
.stDownloadButton > button:hover {
    background: #625BAF !important;
    border-color: #625BAF !important;
    color: white !important;
    transform: translateY(-1px);
    box-shadow: 0 7px 16px rgba(98,91,175,0.2) !important;
}

.stButton > button:focus,
div[data-testid="stFormSubmitButton"] > button:focus {
    box-shadow: 0 0 0 3px rgba(119,113,201,0.18) !important;
}

/* Input fields */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background: #FFFFFF !important;
    color: var(--ink) !important;
    border: 1px solid #E2DFEB !important;
    border-radius: 11px !important;
    font-size: 0.94rem !important;
    padding: 0.7rem 0.85rem !important;
    transition: border-color .18s ease, box-shadow .18s ease;
}

.stTextInput input:focus,
.stTextArea textarea:focus,
.stNumberInput input:focus {
    border-color: #928BD7 !important;
    box-shadow: 0 0 0 3px rgba(146,139,215,0.12) !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #B0AEC0 !important;
}

.stSelectbox [data-baseweb="select"] > div {
    background: #FFFFFF !important;
    border-color: #E2DFEB !important;
    border-radius: 11px !important;
    color: var(--ink) !important;
}

label,
[data-testid="stWidgetLabel"] p {
    color: #5E5B76 !important;
    font-size: 0.88rem !important;
    font-weight: 650 !important;
}

/* Cards */
.app-card {
    box-sizing: border-box;
    padding: 23px;
    margin: 0 0 15px;
    background: rgba(255,255,255,0.94);
    border: 1px solid var(--line);
    border-radius: 17px;
    box-shadow: 0 4px 15px rgba(42,36,77,0.035);
    transition: border-color .2s ease, box-shadow .2s ease;
}

.app-card:hover {
    border-color: #D8D2EF;
    box-shadow: 0 8px 24px rgba(42,36,77,0.065);
}

.app-card-myteam {
    background: linear-gradient(135deg, #F7F4FF, #FFFFFF) !important;
    border: 1.5px solid #BEB5E9 !important;
    box-shadow: 0 5px 20px rgba(119,113,201,0.08) !important;
}

.tag-blue {
    display: inline-block;
    padding: 4px 9px;
    border-radius: 6px;
    background: #EEF0FB;
    color: #7069B8;
    font-size: 0.74rem;
    font-weight: 750;
}

/* Points */
.point-chip {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 7px;
    box-sizing: border-box;
    min-height: 44px;
    padding: 8px 14px;
    border-radius: 11px;
    background: #FBF6EA;
    border: 1px solid #EFE3C8;
    color: #A87A35;
    font-size: 0.95rem;
    font-weight: 800;
}

/* Alerts and dividers */
div[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: 1px solid var(--line) !important;
    box-shadow: none !important;
}

hr {
    border-color: #E8E5EF !important;
    margin: 2rem 0 !important;
}

/* Forms */
[data-testid="stForm"] {
    padding: 19px !important;
    border: 1px solid #EAE7F1 !important;
    border-radius: 15px !important;
    background: rgba(255,255,255,0.65) !important;
}

/* Countdown */
.countdown-box {
    box-sizing: border-box;
    max-width: 680px;
    margin: 30px auto;
    padding: 48px 24px;
    text-align: center;
    background:
        radial-gradient(ellipse at top right, #F0EDFC 0%, transparent 55%),
        #FFFFFF;
    border: 1px solid #DCD5F2;
    border-radius: 24px;
    box-shadow: 0 14px 40px rgba(61,50,110,0.08);
}

.countdown-box h2 {
    font-size: 1.45rem !important;
}

.countdown-num {
    margin: 18px 0;
    color: #7771C9;
    font-size: 6.5rem;
    font-weight: 850;
    letter-spacing: -0.08em;
    line-height: 1.1;
}

.stDownloadButton {
    width: 100%;
}

/* Responsive */
@media (max-width: 768px) {
    .main .block-container {
        padding: 1rem 0.85rem 2.5rem !important;
    }

    .sonorus-header {
        padding: 18px;
        gap: 10px;
        border-radius: 17px;
    }

    .app-header-title {
        font-size: 1.25rem;
    }

    .badge-chip {
        font-size: 0.68rem;
        padding: 6px 9px;
        white-space: normal;
        text-align: center;
    }

    .app-card {
        padding: 17px;
        border-radius: 14px;
    }

    .countdown-box {
        padding: 35px 16px;
    }

    .countdown-num {
        font-size: 5rem;
    }
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SVG Icons
# ---------------------------------------------------------
SVG_HAMMER = """<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M14.7 6.3L17.7 3.3C18.1 2.9 18.7 2.9 19.1 3.3L20.7 4.9C21.1 5.3 21.1 5.9 20.7 6.3L17.7 9.3M14.7 6.3L11.7 9.3M14.7 6.3L17.7 9.3M11.7 9.3L4.2 16.8C3.8 17.2 3.8 17.8 4.2 18.2L5.8 19.8C6.2 20.2 6.8 20.2 7.2 19.8L14.7 12.3M11.7 9.3L14.7 12.3" stroke="#7771C9" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>"""

SVG_STAR = """<svg width="22" height="22" viewBox="0 0 24 24" fill="#D6AC60" xmlns="http://www.w3.org/2000/svg"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/></svg>"""

# ---------------------------------------------------------
# 3. SQLite Database
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

    c.execute("""
        INSERT INTO bids
        (user_name, user_team, target_team_id, amount, feedback, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_name, user_team, target_team_id,
        amount, feedback, now_str
    ))

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
    c.execute(
        "REPLACE INTO app_state (key, value) VALUES (?, ?)",
        (key, str(value))
    )
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
# 4. Real-time Synchronization and Countdown
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

        elapsed = time.time() - cd_start
        remaining = max(0, int(5 - elapsed))

        if remaining > 0:
            st.markdown(f"""
                <div class="countdown-box">
                    <h2 style="color:#292943; margin:0;">
                        🔨 지금, 다음 아이디어를 경매해보세요!
                    </h2>
                    <p style="color:#85849B; font-size:1.05rem; margin-top:8px;">
                        실시간 아이디어 경매장이 개장 준비 중입니다.
                    </p>
                    <div class="countdown-num">{remaining}</div>
                    <p style="color:#7771C9; font-weight:800; font-size:1.1rem;">
                        초 후 실시간 입찰이 시작됩니다!
                    </p>
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

        elapsed = time.time() - reveal_start
        remaining = max(0, int(5 - elapsed))

        if remaining > 0:
            st.markdown(f"""
                <div class="countdown-box" style="border-color:#E5D3A8;">
                    <h2 style="color:#292943; margin:0;">
                        🎉 아이디어 낙찰 완료!
                    </h2>
                    <p style="color:#85849B; font-size:1.05rem; margin-top:8px;">
                        최종 펀딩 결과를 집계하고 있습니다.
                    </p>
                    <div class="countdown-num" style="color:#B98B46;">
                        {remaining}
                    </div>
                    <p style="color:#7771C9; font-weight:800; font-size:1.1rem;">
                        초 후 최종 시상식이 공개됩니다!
                    </p>
                </div>
            """, unsafe_allow_html=True)
        else:
            set_state("phase", "finished")
            st.rerun()


# ---------------------------------------------------------
# 5. Main Dashboard
# ---------------------------------------------------------
current_phase = get_state("phase", "prep")

phase_badge_text = {
    "prep": "STAGE 1 : 아이디어 등록",
    "countdown": "⏳ 경매 시작 5초 전!",
    "auction": "STAGE 2 : 실시간 경매 진행 중",
    "result_reveal": "🏆 결과 집계 중...",
    "finished": "STAGE 3 : 최종 낙찰 결과"
}.get(current_phase, "STAGE 1")

# Header
st.markdown(f"""
    <div class="sonorus-header">
        <div class="app-header-title">
            {SVG_HAMMER} SONORUS AUCTION
        </div>
        <div class="badge-chip">{phase_badge_text}</div>
    </div>
""", unsafe_allow_html=True)

teams_df = get_teams()
team_options = teams_df["name"].tolist() if not teams_df.empty else []

col_p1, col_p2, col_p3, col_p4 = st.columns(
    [1.5, 1.5, 1.5, 2],
    vertical_alignment="bottom"
)

with col_p1:
    user_name = st.text_input(
        "참가자 이름",
        value=st.session_state.get("user_name", ""),
        placeholder="예: 류우비"
    )
    if user_name:
        st.session_state["user_name"] = user_name

with col_p2:
    user_team = st.selectbox(
        "내 소속 팀",
        options=["팀 선택"] + team_options,
        index=0
    )
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
    st.markdown("<label>보유 포인트</label>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='point-chip'>{SVG_STAR} {my_balance:,} P</div>",
        unsafe_allow_html=True
    )

with col_p4:
    admin_pwd = st.text_input(
        "관리자 암호",
        type="password",
        placeholder="관리자 암호"
    )
    is_admin = (admin_pwd == "sonorus123")

if is_admin:
    st.success("🔒 관리자 권한 인증됨")

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
        if st.button("💥 전체 데이터 완전 초기화", use_container_width=True):
            reset_all_data()
            st.rerun()

st.markdown("---")


# ---------------------------------------------------------
# STAGE 1: Preparation
# ---------------------------------------------------------
if current_phase == "prep":
    st.subheader("💡 오늘 발표할 아이디어를 등록해보세요!")
    st.caption("좋은 아이디어는 언제나 누군가의 손을 기다리고 있어요.")

    col_create, col_teams = st.columns([1, 2])

    with col_create:
        st.markdown("<div class='app-card'>", unsafe_allow_html=True)
        st.markdown("### ➕ 신규 아이디어 등록")

        with st.form(key="add_team_form"):
            new_team_name = st.text_input(
                "팀 이름",
                placeholder="예: 별빛팀"
            )
            new_team_title = st.text_input(
                "아이디어 / 주제명",
                placeholder="예: 인터랙티브 요소 추가하기"
            )
            new_team_desc = st.text_area(
                "상세 설명",
                placeholder="사용자가 직접 참여할 수 있는 요소를 적어주세요."
            )
            add_btn = st.form_submit_button(
                "아이디어 등록하기",
                use_container_width=True
            )

            if add_btn:
                if not new_team_name or not new_team_title or not new_team_desc:
                    st.error("모든 항목을 입력해야 합니다.")
                else:
                    if add_team(new_team_name, new_team_title, new_team_desc):
                        st.success(f"'{new_team_name}' 등록 완료!")
                        st.rerun()
                    else:
                        st.error("이미 존재하는 팀 이름입니다.")

        st.markdown("</div>", unsafe_allow_html=True)

    with col_teams:
        st.markdown("### 📋 등록된 아이디어 리스트")

        if teams_df.empty:
            st.info("아직 등록된 아이디어가 없습니다.")
        else:
            for _, row in teams_df.iterrows():
                is_my_team = (user_team == row["name"])
                card_class = (
                    "app-card app-card-myteam"
                    if is_my_team else "app-card"
                )
                badge = (
                    "<span class='tag-blue'>우리 팀</span>"
                    if is_my_team else ""
                )

                st.markdown(f"""
                    <div class="{card_class}">
                        <div style="display:flex; justify-content:space-between;
                                    align-items:center; gap:10px; margin-bottom:8px;">
                            <span style="font-weight:800; color:#7771C9;
                                         font-size:1.05rem;">
                                {row['name']} {badge}
                            </span>
                            <span class="tag-blue">디자인 / 기획</span>
                        </div>
                        <div style="font-size:1.15rem; font-weight:800;
                                    color:#292943; margin-bottom:6px;">
                            {row['title']}
                        </div>
                        <div style="color:#85849B; font-size:0.95rem;">
                            {row['description']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                if is_admin or is_my_team:
                    with st.form(key=f"edit_form_{row['id']}"):
                        edit_title = st.text_input(
                            "주제 수정",
                            value=row["title"],
                            key=f"title_{row['id']}"
                        )
                        edit_desc = st.text_area(
                            "설명 수정",
                            value=row["description"],
                            key=f"desc_{row['id']}"
                        )

                        if st.form_submit_button(
                            "✍️ 내용 수정 저장",
                            use_container_width=True
                        ):
                            update_team_info(row["id"], edit_title, edit_desc)
                            st.success("수정 완료!")
                            st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)


# ---------------------------------------------------------
# STAGE 1.5: Countdown
# ---------------------------------------------------------
elif current_phase == "countdown":
    live_sync_and_countdown()


# ---------------------------------------------------------
# STAGE 2: Live Auction
# ---------------------------------------------------------
elif current_phase == "auction":
    live_sync_and_countdown()
    st.subheader("🔨 실시간 라이브 경매 진행 중")
    st.caption("타 팀 아이디어에 포인트를 입찰하고 조건부 피드백을 공유하세요.")

    col_auction, col_feed = st.columns([2, 1])

    with col_auction:
        if teams_df.empty:
            st.warning("등록된 팀이 없습니다.")
        else:
            for _, row in teams_df.iterrows():
                is_my_team = (user_team == row["name"])

                team_bids = bids_df[
                    bids_df["target_team_id"] == row["id"]
                ]
                total_funding = (
                    team_bids["amount"].sum()
                    if not team_bids.empty else 0
                )

                card_style = (
                    "app-card app-card-myteam"
                    if is_my_team else "app-card"
                )
                badge_html = (
                    "<span class='tag-blue'>우리 팀</span>"
                    if is_my_team else ""
                )

                st.markdown(f"""
                    <div class="{card_style}">
                        <div style="display:flex; justify-content:space-between;
                                    align-items:center; gap:10px; margin-bottom:6px;">
                            <span style="font-weight:800; color:#7771C9;
                                         font-size:1.05rem;">
                                {row['name']} {badge_html}
                            </span>
                            <span class="point-chip"
                                  style="font-size:0.85rem; padding:4px 10px; height:auto;">
                                현재 최고가 {total_funding:,} P
                            </span>
                        </div>
                        <div style="font-size:1.2rem; font-weight:900;
                                    color:#292943; margin-bottom:8px;">
                            {row['title']}
                        </div>
                        <div style="color:#85849B; font-size:0.95rem; margin-bottom:12px;">
                            {row['description']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                if is_my_team:
                    st.caption("자기 팀에는 입찰할 수 없습니다.")
                else:
                    with st.form(key=f"bid_form_{row['id']}"):
                        bid_amount = st.number_input(
                            "입찰 포인트 설정 (P)",
                            min_value=10000,
                            max_value=max(10000, my_balance),
                            step=50000,
                            key=f"amount_{row['id']}"
                        )

                        feedback = st.text_area(
                            "입찰 이유 및 조건부 피드백 (필수)",
                            placeholder="사용자가 직접 참여하는 인터랙티브 요소는 무엇인가요?",
                            key=f"feedback_{row['id']}"
                        )

                        submit_bid = st.form_submit_button(
                            "입찰하기",
                            use_container_width=True
                        )

                        if submit_bid:
                            if not user_name or user_team == "팀 선택":
                                st.error("상단에서 참가자 이름과 소속 팀을 선택하세요.")
                            elif bid_amount > my_balance:
                                st.error("포인트가 부족합니다.")
                            elif not feedback.strip():
                                st.error("피드백을 작성해야 합니다.")
                            else:
                                add_bid(
                                    user_name,
                                    user_team,
                                    row["id"],
                                    bid_amount,
                                    feedback
                                )
                                st.success(f"{bid_amount:,} P 입찰 완료!")
                                st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)

    with col_feed:
        st.subheader("⚡ 실시간 입찰 현황")

        if bids_df.empty:
            st.info("아직 제출된 입찰 내역이 없습니다.")
        else:
            for _, bid in bids_df.sort_values(
                by="id", ascending=False
            ).head(10).iterrows():

                target_rows = teams_df[
                    teams_df["id"] == bid["target_team_id"]
                ]
                target_name = (
                    target_rows["name"].values[0]
                    if not target_rows.empty else "팀"
                )

                st.markdown(f"""
                    <div style="background:#FFFFFF; border:1px solid #E9E6F0;
                                padding:16px; border-radius:15px; margin-bottom:10px;
                                box-shadow:0 4px 14px rgba(42,36,77,0.035);">
                        <div style="font-size:0.85rem; color:#85849B;
                                    display:flex; justify-content:space-between;
                                    gap:8px;">
                            <span>
                                <strong style="color:#292943;">
                                    {bid['user_name']}
                                </strong>
                                ({bid['user_team']})
                            </span>
                            <span class="badge-chip">입찰 중</span>
                        </div>
                        <div style="font-size:1.05rem; font-weight:850;
                                    color:#7771C9; margin:8px 0;">
                            ➔ {target_name} : {bid['amount']:,} P
                        </div>
                        <div style="color:#5E5B76; font-size:0.9rem;">
                            "{bid['feedback']}"
                        </div>
                    </div>
                """, unsafe_allow_html=True)


# ---------------------------------------------------------
# STAGE 2.5: Result Reveal
# ---------------------------------------------------------
elif current_phase == "result_reveal":
    live_sync_and_countdown()


# ---------------------------------------------------------
# STAGE 3: Final Results
# ---------------------------------------------------------
elif current_phase == "finished":
    live_sync_and_countdown()
    st.subheader("🏆 이번 경매 최종 결과")
    st.caption("아이디어에 모인 응원과 투자 결과를 확인해 보세요.")

    funding_summary = []

    for _, row in teams_df.iterrows():
        team_bids = bids_df[
            bids_df["target_team_id"] == row["id"]
        ]
        total_funding = (
            team_bids["amount"].sum()
            if not team_bids.empty else 0
        )

        funding_summary.append({
            "팀": row["name"],
            "주제": row["title"],
            "총 펀딩액": total_funding
        })

    summary_df = (
        pd.DataFrame(funding_summary).sort_values(
            by="총 펀딩액", ascending=False
        )
        if funding_summary else pd.DataFrame()
    )

    st.markdown("### 🥇 아이디어 낙찰 순위")

    if not summary_df.empty:
        for idx, row in summary_df.reset_index(drop=True).iterrows():
            rank = idx + 1

            st.markdown(f"""
                <div class="app-card"
                     style="border-left:4px solid #BEB5E9;">
                    <div style="display:flex; justify-content:space-between;
                                align-items:center; gap:12px;">
                        <span style="font-size:1.05rem; font-weight:800;
                                     color:#292943;">
                            {rank}위 : {row['팀']} - {row['주제']}
                        </span>
                        <span class="point-chip" style="height:auto;">
                            {row['총 펀딩액']:,} P 낙찰
                        </span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 💎 최고 엔젤 투자자 현황")

    if not bids_df.empty:
        investor_df = bids_df.groupby(
            ["user_name", "user_team"]
        )["amount"].sum().reset_index()

        investor_df = investor_df.sort_values(
            by="amount", ascending=False
        )

        for idx, row in investor_df.reset_index(drop=True).head(3).iterrows():
            rank = idx + 1

            st.markdown(f"""
                <div style="background:#FFFFFF; padding:16px;
                            border-radius:14px; margin-bottom:10px;
                            border:1px solid #E9E6F0;
                            display:flex; justify-content:space-between;
                            align-items:center; gap:12px;">
                    <span>
                        <strong style="color:#7771C9;">{rank}위</strong>
                        : {row['user_name']} ({row['user_team']})
                    </span>
                    <span style="font-weight:850; color:#292943;">
                        총 {row['amount']:,} P 투자
                    </span>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📥 전체 피드백 다운로드")

    if not bids_df.empty:
        csv_data = bids_df.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            label="📄 전체 피드백 리포트 CSV 다운로드",
            data=csv_data,
            file_name="sonorus_auction_feedbacks.csv",
            mime="text/csv"
        )
