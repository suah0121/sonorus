import streamlit as st
import pandas as pd
import sqlite3
import time
from datetime import datetime

# ---------------------------------------------------------
# 1. 페이지 설정 및 UI 스타일
# ---------------------------------------------------------
st.set_page_config(
    page_title="프로젝트 경매전 - SONORUS",
    page_icon="🔨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

* {
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif !important;
}

header[data-testid="stHeader"],
footer,
div[data-testid="stSidebarCollapseButton"],
section[data-testid="stSidebar"],
.stDeployButton {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
}

.stApp {
    background: linear-gradient(180deg, #F4F2FB 0%, #FAFBFF 100%) !important;
    color: #27304A !important;
}

.main .block-container {
    padding: 1.5rem 1rem 3rem !important;
    max-width: 1400px !important;
}

.stButton > button,
div[data-testid="stFormSubmitButton"] > button,
div[data-testid="stDownloadButton"] > button {
    background: #7771D8 !important;
    color: #FFFFFF !important;
    font-size: 1rem !important;
    font-weight: 750 !important;
    border-radius: 12px !important;
    border: 1px solid #7771D8 !important;
    padding: 0.75rem 1.1rem !important;
    box-shadow: 0 5px 14px rgba(119, 113, 216, 0.16) !important;
    width: 100% !important;
    transition: all 0.18s ease-in-out !important;
}

.stButton > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover,
div[data-testid="stDownloadButton"] > button:hover {
    background: #625CC5 !important;
    border-color: #625CC5 !important;
    transform: translateY(-1px) !important;
}

.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div,
.stNumberInput input {
    background-color: #FFFFFF !important;
    color: #27304A !important;
    border: 1px solid #E0E2EF !important;
    border-radius: 10px !important;
    font-size: 0.95rem !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus,
.stNumberInput input:focus {
    border-color: #8983E6 !important;
    box-shadow: 0 0 0 3px rgba(137, 131, 230, 0.13) !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #A4A8BB !important;
}

label {
    color: #505875 !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
}

div[data-testid="stCaptionContainer"] {
    color: #7A8199 !important;
}

hr {
    border-color: #E4E3F0 !important;
    margin: 1.6rem 0 !important;
}

.app-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    background: rgba(255,255,255,0.94);
    padding: 22px 26px;
    border-radius: 24px;
    border: 1px solid #E2DFF4;
    box-shadow: 0 8px 28px rgba(50, 45, 100, 0.045);
    margin-bottom: 24px;
}

.app-header-title {
    font-size: 1.55rem;
    font-weight: 900;
    color: #282747;
    letter-spacing: -0.65px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.badge-chip {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: #F0EEFC;
    color: #6E68C9;
    font-weight: 800;
    font-size: 0.78rem;
    padding: 8px 13px;
    border-radius: 999px;
    white-space: nowrap;
}

.app-card {
    background: #FFFFFF;
    border-radius: 18px;
    padding: 21px;
    margin-bottom: 14px;
    border: 1px solid #E8E8F2;
    box-shadow: 0 6px 18px rgba(45, 43, 86, 0.045);
}

.app-card-myteam {
    border: 1.5px solid #8D86E7 !important;
    background: #FAF9FF !important;
}

.point-label {
    display: flex;
    align-items: center;
    height: 1.5rem;
    margin-bottom: 0.5rem;
    color: #505875;
    font-weight: 700;
    font-size: 0.9rem;
}

.point-chip {
    background: #FFF8E8;
    color: #B7791F;
    border: 1px solid #F2DFB5;
    font-weight: 800;
    padding: 0 16px;
    border-radius: 10px;
    font-size: 0.95rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 7px;
    height: 48px;
    width: 100%;
    box-sizing: border-box;
    margin: 0;
    white-space: nowrap;
}

.tag-blue {
    display: inline-block;
    background: #EEF3FF;
    color: #5D70B8;
    font-weight: 800;
    font-size: 0.75rem;
    padding: 4px 9px;
    border-radius: 7px;
}

.countdown-box {
    text-align: center;
    padding: 46px 20px;
    background: #FFFFFF;
    border-radius: 24px;
    border: 1.5px solid #DCD8F7;
    box-shadow: 0 12px 30px rgba(88, 80, 160, 0.09);
    margin: 20px auto;
    max-width: 680px;
}

.countdown-num {
    font-size: 7rem;
    font-weight: 900;
    color: #7771D8;
    line-height: 1;
    margin: 14px 0;
}

.section-kicker {
    color: #7771D8;
    font-weight: 800;
    font-size: 0.82rem;
    letter-spacing: 0.04em;
    margin-bottom: 4px;
}

@media (max-width: 760px) {
    .app-header {
        padding: 17px;
        border-radius: 18px;
        align-items: flex-start;
        flex-direction: column;
    }
    .app-header-title {
        font-size: 1.3rem;
    }
    .countdown-num {
        font-size: 5rem;
    }
    .app-card {
        padding: 16px;
    }
}
</style>
""", unsafe_allow_html=True)

SVG_HAMMER = """<svg width="27" height="27" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M14.7 6.3L17.7 3.3C18.1 2.9 18.7 2.9 19.1 3.3L20.7 4.9C21.1 5.3 21.1 5.9 20.7 6.3L17.7 9.3M14.7 6.3L11.7 9.3M14.7 6.3L17.7 9.3M11.7 9.3L4.2 16.8C3.8 17.2 3.8 17.8 4.2 18.2L5.8 19.8C6.2 20.2 6.8 20.2 7.2 19.8L14.7 12.3M11.7 9.3L14.7 12.3" stroke="#7771D8" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>"""
SVG_STAR = """<svg width="20" height="20" viewBox="0 0 24 24" fill="#D6A64D" xmlns="http://www.w3.org/2000/svg"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/></svg>"""

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
                    <h2 style="color:#282747; margin:0; font-size:1.5rem;">🔨 프로젝트 경매가 곧 시작됩니다!</h2>
                    <p style="color:#7A8199; font-size:1.05rem; margin-top:8px;">다른 팀의 프로젝트를 살펴보고 응원할 준비를 해주세요.</p>
                    <div class="countdown-num">{remaining}</div>
                    <p style="color:#7771D8; font-weight:800; font-size:1.1rem;">초 후 실시간 입찰이 시작됩니다.</p>
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
                <div class="countdown-box" style="border-color:#EBD9A9;">
                    <h2 style="color:#282747; margin:0; font-size:1.5rem;">🎉 프로젝트 경매 마감!</h2>
                    <p style="color:#7A8199; font-size:1.05rem; margin-top:8px;">팀별 투자 결과를 정리하고 있습니다.</p>
                    <div class="countdown-num" style="color:#D6A64D;">{remaining}</div>
                    <p style="color:#7771D8; font-weight:800; font-size:1.1rem;">초 후 최종 결과가 공개됩니다.</p>
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
        <div class="app-header-title">{SVG_HAMMER} SONORUS AUCTION</div>
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
    st.markdown("<div class='point-label'>보유 포인트</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='point-chip'>{SVG_STAR} {my_balance:,} P</div>",
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
    st.subheader("💡 오늘의 프로젝트 활동을 소개해보세요!")
    st.caption("우리 팀의 탐구 과정과 활동을 공유하고, 다른 팀의 피드백과 투자를 받아보세요.")

    col_create, col_teams = st.columns([1, 2])

    with col_create:
        st.markdown("<div class='app-card'>", unsafe_allow_html=True)
        st.markdown("### ✦ 프로젝트 활동 등록")
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
        st.markdown("### 📋 등록된 프로젝트 목록")
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
                            <span style="font-weight:800; color:#7771D8; font-size:1.02rem;">{row['name']} {badge}</span>
                            <span class="tag-blue">프로젝트 소개</span>
                        </div>
                        <div style="font-size:1.15rem; font-weight:850; color:#282747; margin-bottom:8px;">
                            {row['title']}
                        </div>
                        <div style="color:#68718B; font-size:0.95rem; line-height:1.7; white-space:pre-wrap;">
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
    st.subheader("🔨 실시간 프로젝트 경매")
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
                            <span style="font-weight:800; color:#7771D8; font-size:1.02rem;">{row['name']} {badge_html}</span>
                            <span class="point-chip" style="font-size:0.82rem; padding:5px 10px; height:auto; width:auto;">누적 투자 {total_funding:,} P</span>
                        </div>
                        <div style="font-size:1.2rem; font-weight:900; color:#282747; margin-bottom:8px;">{row['title']}</div>
                        <div style="color:#68718B; font-size:0.95rem; line-height:1.7; margin-bottom:8px; white-space:pre-wrap;">{row['description']}</div>
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
                    <div style="background:#FFFFFF; border:1px solid #E8E8F2; padding:14px; border-radius:15px; margin-bottom:10px; box-shadow:0 4px 12px rgba(45,43,86,0.04);">
                        <div style="font-size:0.85rem; color:#7A8199; display:flex; justify-content:space-between; gap:8px;">
                            <span><strong style="color:#282747;">{bid['user_name']}</strong> ({bid['user_team']})</span>
                            <span class="badge-chip">투자 완료</span>
                        </div>
                        <div style="font-size:1.05rem; font-weight:900; color:#7771D8; margin:8px 0;">
                            ➜ {target_name} · {bid['amount']:,} P
                        </div>
                        <div style="color:#505875; font-size:0.9rem; line-height:1.6;">“{bid['feedback']}”</div>
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
    st.subheader("🏆 프로젝트 투자 결과")

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
                        <span style="font-size:1.05rem; font-weight:800; color:#282747;">{rank}위 · {row['팀']} — {row['프로젝트']}</span>
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
                <div style="background:#FFFFFF; padding:15px; border-radius:14px; margin-bottom:10px; border:1px solid #E8E8F2; display:flex; justify-content:space-between; align-items:center; gap:12px;">
                    <span><strong style="color:#7771D8;">{rank}위</strong> · {row['user_name']} ({row['user_team']})</span>
                    <span style="font-weight:900; color:#282747;">총 {row['amount']:,} P 투자</span>
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
