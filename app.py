import streamlit as st
import pandas as pd
import sqlite3
import time
from datetime import datetime

# ---------------------------------------------------------
# 1. 페이지 설정 & 실시간 반응형 CSS
# ---------------------------------------------------------
st.set_page_config(
    page_title="SONORUS 아이디어 경매전",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 화면 상단 여백 제거 및 가독성 다크 스타일
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
        background-color: #0b0f19 !important;
        color: #f1f5f9 !important;
    }
    
    .main .block-container {
        padding: 1.5rem 2rem !important;
        max-width: 1400px !important;
    }

    .stTextInput input, .stTextArea textarea, .stSelectbox select, .stNumberInput input {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border: 1px solid #475569 !important;
        border-radius: 8px !important;
        font-size: 1rem !important;
        padding: 0.6rem 0.8rem !important;
    }
    
    label {
        color: #cbd5e1 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        margin-bottom: 0.4rem !important;
    }

    .stButton>button, div[data-testid="stFormSubmitButton"]>button {
        background: #4f46e5 !important;
        color: #ffffff !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.75rem 1.2rem !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4) !important;
        width: 100% !important;
    }
    .stButton>button:hover, div[data-testid="stFormSubmitButton"]>button:hover {
        background: #4338ca !important;
        color: #ffffff !important;
    }

    .app-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #1e293b;
        padding: 18px 24px;
        border-radius: 12px;
        border: 1px solid #334155;
        margin-bottom: 24px;
    }
    .app-title {
        font-size: 1.6rem;
        font-weight: 800;
        color: #818cf8;
        letter-spacing: -0.5px;
    }
    .badge-stage {
        background: #312e81;
        color: #a5b4fc;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        border: 1px solid #4338ca;
    }
    .card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }
    .card-myteam {
        border: 2px solid #f59e0b !important;
        background-color: #1c1917 !important;
    }

    .countdown-box {
        text-align: center;
        padding: 60px 20px;
        background: radial-gradient(circle, #1e1b4b 0%, #0b0f19 100%);
        border-radius: 20px;
        border: 2px solid #6366f1;
        box-shadow: 0 0 40px rgba(99, 102, 241, 0.4);
        margin: 40px auto;
        max-width: 700px;
    }
    .countdown-number {
        font-size: 6rem;
        font-weight: 900;
        color: #f59e0b;
        text-shadow: 0 0 20px rgba(245, 158, 11, 0.8);
        margin: 20px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SQLite 데이터베이스 관리
# ---------------------------------------------------------
DB_FILE = "auction_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS bids (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            user_team TEXT NOT NULL,
            target_team_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            feedback TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS app_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')
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
        c.execute("INSERT INTO teams (name, title, description) VALUES (?, ?, ?)", (name, title, description))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def update_team_info(team_id, title, description):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE teams SET title = ?, description = ? WHERE id = ?", (title, description, team_id))
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
        "INSERT INTO bids (user_name, user_team, target_team_id, amount, feedback, created_at) VALUES (?, ?, ?, ?, ?, ?)",
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
    c.execute("DELETE FROM app_state WHERE key = 'countdown_start'")
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# 3. 실시간 자동 동기화 엔진 (@st.fragment)
# ---------------------------------------------------------
@st.fragment(run_every=1)
def live_sync_engine():
    current_phase = get_state("phase", "prep")
    last_phase = st.session_state.get("last_synced_phase", None)
    
    # 카운트다운 단계인 경우 매 초마다 UI 갱신
    if current_phase == "countdown":
        st.rerun()
    elif last_phase != current_phase:
        st.session_state["last_synced_phase"] = current_phase
        st.rerun()

live_sync_engine()

# ---------------------------------------------------------
# 4. 메인 애플리케이션
# ---------------------------------------------------------
current_phase = get_state("phase", "prep")

phase_text = {
    'prep': 'STAGE 1 : 준비 및 팀 소개',
    'countdown': '⏳ 경매 시작 카운트다운 중...',
    'auction': 'STAGE 2 : 실시간 경매 진행 중',
    'finished': 'STAGE 3 : 경매 마감 및 결과'
}.get(current_phase, 'STAGE 1')

st.markdown(f"""
    <div class="app-header">
        <div class="app-title">🎵 SONORUS 아이디어 경매전</div>
        <div class="badge-stage">{phase_text}</div>
    </div>
""", unsafe_allow_html=True)

# 접속자 데이터 & 잔액
teams_df = get_teams()
team_options = teams_df['name'].tolist() if not teams_df.empty else []

col_p1, col_p2, col_p3, col_p4 = st.columns([1.5, 1.5, 1.5, 2])

with col_p1:
    user_name = st.text_input("내 이름", value=st.session_state.get("user_name", ""), placeholder="홍길동")
    if user_name:
        st.session_state["user_name"] = user_name

with col_p2:
    user_team = st.selectbox("내 소속 팀", options=["팀 선택"] + team_options, index=0)
    if user_team != "팀 선택":
        st.session_state["user_team"] = user_team

INITIAL_BALANCE = 1000000
bids_df = get_bids()

if user_name:
    my_bids = bids_df[bids_df['user_name'] == user_name]
    used_amount = my_bids['amount'].sum() if not my_bids.empty else 0
    my_balance = INITIAL_BALANCE - used_amount
else:
    my_balance = INITIAL_BALANCE

with col_p3:
    st.markdown("<label>보유 잔액</label>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:1.4rem; font-weight:800; color:#f59e0b; margin-top:2px;'>{my_balance:,} 소노</div>", unsafe_allow_html=True)

with col_p4:
    admin_pwd = st.text_input("관리자 암호", type="password", placeholder="sonorus123")
    is_admin = (admin_pwd == "sonorus123")

# 관리자 제어 버튼
if is_admin:
    st.success("🔒 관리자 권한 활성화됨")
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if current_phase == 'prep':
            if st.button("🚀 경매 시작하기 (카운트다운)", use_container_width=True):
                set_state("countdown_start", time.time())
                set_state("phase", "countdown")
                st.rerun()
        elif current_phase in ['auction', 'countdown']:
            if st.button("🚨 경매 마감하기", use_container_width=True):
                set_state("phase", "finished")
                st.rerun()
        elif current_phase == 'finished':
            if st.button("🔄 준비로 돌아가기", use_container_width=True):
                set_state("phase", "prep")
                st.rerun()
    with c_btn2:
        if st.button("💥 전체 데이터 완전 초기화", use_container_width=True):
            reset_all_data()
            st.rerun()

st.markdown("---")

# ---------------------------------------------------------
# STAGE 1: 경매 준비
# ---------------------------------------------------------
if current_phase == 'prep':
    st.subheader("📢 팀별 주제 발표 및 작성")
    st.caption("팀을 새로 추가하거나, 우리 팀의 프로젝트 제목과 상세 내용을 작성하세요.")

    col_create, col_teams = st.columns([1, 2])

    with col_create:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### ➕ 신규 팀 등록")
        with st.form(key="add_team_form"):
            new_team_name = st.text_input("팀 이름", placeholder="예: 1팀")
            new_team_title = st.text_input("프로젝트 / 주제명", placeholder="예: AI 사운드 가이드")
            new_team_desc = st.text_area("핵심 내용 설명", placeholder="상세 활동 계획을 작성하세요.")
            add_btn = st.form_submit_button("팀 등록하기", use_container_width=True)

            if add_btn:
                if not new_team_name or not new_team_title or not new_team_desc:
                    st.error("모든 내용을 작성해야 합니다.")
                else:
                    if add_team(new_team_name, new_team_title, new_team_desc):
                        st.success(f"'{new_team_name}' 생성 완료!")
                        st.rerun()
                    else:
                        st.error("이미 존재하는 팀 이름입니다.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_teams:
        st.markdown("### 📋 등록된 팀 목록")
        if teams_df.empty:
            st.info("등록된 팀이 없습니다. 왼쪽에서 신규 팀을 등록해주세요.")
        else:
            for _, row in teams_df.iterrows():
                is_my_team = (user_team == row['name'])
                card_class = "card card-myteam" if is_my_team else "card"
                badge = "<span style='background:#f59e0b; color:#000; padding:2px 8px; border-radius:4px; font-size:0.8rem; font-weight:bold; float:right;'>우리 팀</span>" if is_my_team else ""

                st.markdown(f"""
                    <div class="{card_class}">
                        <div style="font-size:1.2rem; font-weight:bold; color:#818cf8; margin-bottom:8px;">
                            팀명: {row['name']} {badge}
                        </div>
                        <div style="font-size:1.1rem; font-weight:700; color:#ffffff; margin-bottom:6px;">
                            주제: {row['title']}
                        </div>
                        <div style="color:#cbd5e1; font-size:0.95rem;">
                            {row['description']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                if is_admin or is_my_team:
                    with st.form(key=f"edit_form_{row['id']}"):
                        edit_title = st.text_input("주제 제목 수정", value=row['title'], key=f"title_{row['id']}")
                        edit_desc = st.text_area("설명 및 목표 수정", value=row['description'], key=f"desc_{row['id']}")
                        if st.form_submit_button("✍️ 수정 내용 저장", use_container_width=True):
                            update_team_info(row['id'], edit_title, edit_desc)
                            st.success("저장되었습니다.")
                            st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# STAGE 1.5: 5초 긴장감 타임스탬프 카운트다운 화면
# ---------------------------------------------------------
elif current_phase == 'countdown':
    start_time = float(get_state("countdown_start", time.time()))
    elapsed = time.time() - start_time
    remaining = max(0, int(5 - elapsed))
    
    if remaining > 0:
        st.markdown(f"""
            <div class="countdown-box">
                <h2 style="color: #a5b4fc; margin:0;">🔥 실시간 아이디어 경매 시작 직전! 🔥</h2>
                <p style="color: #cbd5e1; font-size: 1.1rem; margin-top: 10px;">투자 전략을 최종 점검하세요!</p>
                <div class="countdown-number">{remaining}</div>
                <p style="color: #f59e0b; font-weight: bold;">초 후 경매장이 개장합니다...</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        # 5초 종료 시 실시간 경매(auction) 상태로 자동 전환
        set_state("phase", "auction")
        st.rerun()

# ---------------------------------------------------------
# STAGE 2: 실시간 아이디어 경매 진행
# ---------------------------------------------------------
elif current_phase == 'auction':
    st.subheader("🔨 실시간 아이디어 경매 진행 중")
    st.caption("타 팀의 프로젝트에 펀딩을 진행하고 조건부 피드백을 남겨주세요. (자기 팀 투자 불가)")

    col_auction, col_feed = st.columns([2, 1])

    with col_auction:
        if teams_df.empty:
            st.warning("등록된 팀이 없습니다.")
        else:
            for _, row in teams_df.iterrows():
                is_my_team = (user_team == row['name'])
                
                team_bids = bids_df[bids_df['target_team_id'] == row['id']]
                total_funding = team_bids['amount'].sum() if not team_bids.empty else 0

                card_style = "card card-myteam" if is_my_team else "card"
                badge_html = "<span style='background:#f59e0b; color:#000; padding:2px 8px; border-radius:4px; font-size:0.8rem; font-weight:bold; float:right;'>우리 팀</span>" if is_my_team else ""

                st.markdown(f"""
                    <div class="{card_style}">
                        <div style="font-size:1.2rem; font-weight:bold; color:#ffffff; margin-bottom:6px;">
                            팀명: {row['name']} | 주제: {row['title']} {badge_html}
                        </div>
                        <div style="color:#94a3b8; font-size:0.95rem; margin-bottom:12px;">{row['description']}</div>
                        <div style="font-size:0.85rem; color:#cbd5e1;">현재 누적 펀딩액</div>
                        <div style="font-size:1.4rem; font-weight:800; color:#f59e0b;">{total_funding:,} 소노</div>
                    </div>
                """, unsafe_allow_html=True)

                if is_my_team:
                    st.caption("자기 팀에는 투자할 수 없습니다.")
                else:
                    with st.form(key=f"bid_form_{row['id']}"):
                        bid_amount = st.number_input(
                            "투자 금액 (소노)",
                            min_value=10000,
                            max_value=max(10000, my_balance),
                            step=50000,
                            key=f"amount_{row['id']}"
                        )
                        feedback = st.text_area(
                            "투자 이유 및 조건부 피드백 (필수)",
                            placeholder="인상 깊은 점과 보완해야 할 점을 적어주세요.",
                            key=f"feedback_{row['id']}"
                        )
                        submit_bid = st.form_submit_button("💰 펀딩 및 피드백 제출", use_container_width=True)

                        if submit_bid:
                            if not user_name or user_team == "팀 선택":
                                st.error("상단에서 내 이름과 팀을 먼저 설정해주세요.")
                            elif bid_amount > my_balance:
                                st.error("잔액이 부족합니다.")
                            elif not feedback.strip():
                                st.error("피드백 내용을 작성해야 합니다.")
                            else:
                                add_bid(user_name, user_team, row['id'], bid_amount, feedback)
                                st.success(f"{bid_amount:,} 소노 펀딩 완료!")
                                st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)

    with col_feed:
        st.subheader("⚡ 라이브 피드백")
        if bids_df.empty:
            st.info("아직 피드백 내역이 없습니다.")
        else:
            for _, bid in bids_df.sort_values(by="id", ascending=False).head(10).iterrows():
                target_rows = teams_df[teams_df['id'] == bid['target_team_id']]
                target_name = target_rows['name'].values[0] if not target_rows.empty else "팀"
                
                st.markdown(f"""
                    <div style="background:#1e293b; border:1px solid #334155; padding:12px; border-radius:8px; margin-bottom:10px;">
                        <div style="font-size:0.85rem; color:#94a3b8;">
                            <strong style="color:#ffffff;">{bid['user_name']} ({bid['user_team']})</strong> ➔ <span style="color:#81
