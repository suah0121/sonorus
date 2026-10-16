import streamlit as st
import pandas as pd
import sqlite3
import time
from datetime import datetime

# ---------------------------------------------------------
# 1. 페이지 설정 및 시안 100% 동일 라이트 파스텔 모바일 UI CSS
# ---------------------------------------------------------
st.set_page_config(
    page_title="아이디어 경매전 - SONORUS",
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

    /* Streamlit 프레임워크 기본 UI 완벽 은폐 */
    header[data-testid="stHeader"], 
    footer, 
    div[data-testid="stSidebarCollapseButton"],
    section[data-testid="stSidebar"],
    .stDeployButton {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }
    
    /* 전체 부드러운 블루-파스텔 배경 */
    .stApp {
        background: linear-gradient(180deg, #EBF2FF 0%, #F5F8FF 100%) !important;
        color: #2D3748 !important;
    }
    
    .main .block-container {
        padding: 1.5rem 1rem !important;
        max-width: 1200px !important;
    }

    /* 시안 메인 보라색 버튼 (#6C68FF) */
    .stButton>button, div[data-testid="stFormSubmitButton"]>button {
        background: #6C68FF !important;
        color: #ffffff !important;
        font-size: 1rem !important;
        font-weight: 800 !important;
        border-radius: 14px !important;
        border: none !important;
        padding: 0.8rem 1.4rem !important;
        box-shadow: 0 6px 16px rgba(108, 104, 255, 0.3) !important;
        width: 100% !important;
        transition: all 0.2s ease-in-out !important;
    }
    .stButton>button:hover, div[data-testid="stFormSubmitButton"]>button:hover {
        background: #5752E5 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 22px rgba(108, 104, 255, 0.45) !important;
    }

    /* 입력창 시안 기반 디테일 */
    .stTextInput input, .stTextArea textarea, .stSelectbox select, .stNumberInput input {
        background-color: #F8FAFC !important;
        color: #1E293B !important;
        border: 1.5px solid #E2E8F0 !important;
        border-radius: 12px !important;
        font-size: 0.95rem !important;
        padding: 0.65rem 0.9rem !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #6C68FF !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 0 0 3px rgba(108, 104, 255, 0.15) !important;
    }

    label {
        color: #475569 !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
    }

    /* 시안 커스텀 모바일 프레임 & 카드 */
    .app-card {
        background: #FFFFFF;
        border-radius: 20px;
        padding: 22px;
        margin-bottom: 16px;
        border: 1px solid #EDF2F7;
        box-shadow: 0 8px 20px rgba(108, 104, 255, 0.06);
    }
    .app-card-myteam {
        border: 2px solid #6C68FF !important;
        background: #F8F7FF !important;
    }

    /* 헤더 및 배지 스타일 */
    .app-header-title {
        font-size: 1.6rem;
        font-weight: 900;
        color: #1E1B4B;
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .badge-chip {
        background: #E0E7FF;
        color: #4338CA;
        font-weight: 800;
        font-size: 0.8rem;
        padding: 4px 10px;
        border-radius: 20px;
    }
    .point-chip {
        background: #FFF9E6;
        color: #D97706;
        border: 1px solid #FDE68A;
        font-weight: 900;
        padding: 6px 14px;
        border-radius: 30px;
        font-size: 0.95rem;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .tag-blue {
        background: #E0F2FE;
        color: #0284C7;
        font-weight: 800;
        font-size: 0.75rem;
        padding: 2px 8px;
        border-radius: 6px;
    }

    /* 대형 카운트다운 연출 전광판 */
    .countdown-box {
        text-align: center;
        padding: 50px 20px;
        background: #FFFFFF;
        border-radius: 24px;
        border: 2px solid #6C68FF;
        box-shadow: 0 12px 30px rgba(108, 104, 255, 0.15);
        margin: 20px auto;
        max-width: 650px;
    }
    .countdown-num {
        font-size: 7rem;
        font-weight: 900;
        color: #6C68FF;
        line-height: 1;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Vector SVG 아이콘 정의 (시안 동일)
SVG_HAMMER = """<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M14.7 6.3L17.7 3.3C18.1 2.9 18.7 2.9 19.1 3.3L20.7 4.9C21.1 5.3 21.1 5.9 20.7 6.3L17.7 9.3M14.7 6.3L11.7 9.3M14.7 6.3L17.7 9.3M11.7 9.3L4.2 16.8C3.8 17.2 3.8 17.8 4.2 18.2L5.8 19.8C6.2 20.2 6.8 20.2 7.2 19.8L14.7 12.3M11.7 9.3L14.7 12.3" stroke="#6C68FF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>"""
SVG_STAR = """<svg width="22" height="22" viewBox="0 0 24 24" fill="#FFD868" xmlns="http://www.w3.org/2000/svg"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/></svg>"""

# ---------------------------------------------------------
# 2. SQLite DB 엔진
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
    c.execute("DELETE FROM app_state WHERE key = 'cd_start'")
    c.execute("DELETE FROM app_state WHERE key = 'reveal_start'")
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# 3. 실시간 동기화 및 카운트다운 엔진
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
                    <h2 style="color: #1E1B4B; margin:0; font-size:1.5rem;">🔨 지금, 다음 아이디어를 경매해보세요!</h2>
                    <p style="color: #64748B; font-size: 1.05rem; margin-top: 8px;">실시간 아이디어 경매장이 개장 준비 중입니다.</p>
                    <div class="countdown-num">{remaining}</div>
                    <p style="color: #6C68FF; font-weight: 800; font-size: 1.1rem;">초 후 실시간 입찰이 시작됩니다!</p>
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
                <div class="countdown-box" style="border-color:#FFD868;">
                    <h2 style="color: #1E1B4B; margin:0; font-size:1.5rem;">🎉 아이디어 낙찰 완료!</h2>
                    <p style="color: #64748B; font-size: 1.05rem; margin-top: 8px;">최종 펀딩 결과를 집계하고 있습니다.</p>
                    <div class="countdown-num" style="color:#FFB6D9;">{remaining}</div>
                    <p style="color: #6C68FF; font-weight: 800; font-size: 1.1rem;">초 후 최종 시상식이 공개됩니다!</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            set_state("phase", "finished")
            st.rerun()

# ---------------------------------------------------------
# 4. 메인 대시보드 (시안 프레임 렌더링)
# ---------------------------------------------------------
current_phase = get_state("phase", "prep")

phase_badge_text = {
    'prep': 'STAGE 1 : 아이디어 등록',
    'countdown': '⏳ 경매 시작 5초 전!',
    'auction': 'STAGE 2 : 실시간 경매 진행 중',
    'result_reveal': '🏆 결과 집계 중...',
    'finished': 'STAGE 3 : 최종 낙찰 결과'
}.get(current_phase, 'STAGE 1')

# 상단 헤더
st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; background:#FFFFFF; padding:18px 24px; border-radius:20px; border:1px solid #E2E8F0; box-shadow:0 6px 18px rgba(108,104,255,0.06); margin-bottom:20px;">
        <div class="app-header-title">{SVG_HAMMER} 아이디어 경매전</div>
        <div class="badge-chip">{phase_badge_text}</div>
    </div>
""", unsafe_allow_html=True)

teams_df = get_teams()
team_options = teams_df['name'].tolist() if not teams_df.empty else []

col_p1, col_p2, col_p3, col_p4 = st.columns([1.5, 1.5, 1.5, 2])

with col_p1:
    user_name = st.text_input("참가자 이름", value=st.session_state.get("user_name", ""), placeholder="예: 류우비")
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
    st.markdown("<label>보유 포인트</label>", unsafe_allow_html=True)
    st.markdown(f"<div class='point-chip'>{SVG_STAR} {my_balance:,} P</div>", unsafe_allow_html=True)

with col_p4:
    admin_pwd = st.text_input("관리자 암호", type="password", placeholder="sonorus123")
    is_admin = (admin_pwd == "sonorus123")

if is_admin:
    st.success("🔒 관리자 권한 인증됨")
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if current_phase == 'prep':
            if st.button("🚀 경매 시작 (5초 카운트다운)", use_container_width=True):
                set_state("cd_start", time.time())
                set_state("phase", "countdown")
                st.rerun()
        elif current_phase in ['auction', 'countdown']:
            if st.button("🚨 경매 마감 및 결과 발표", use_container_width=True):
                set_state("reveal_start", time.time())
                set_state("phase", "result_reveal")
                st.rerun()
        elif current_phase in ['finished', 'result_reveal']:
            if st.button("🔄 준비 화면으로 복귀", use_container_width=True):
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
    st.subheader("💡 오늘 발표할 아이디어를 등록해보세요!")
    st.caption("좋은 아이디어는 언제나 누군가의 손을 기다리고 있어요.")

    col_create, col_teams = st.columns([1, 2])

    with col_create:
        st.markdown("<div class='app-card'>", unsafe_allow_html=True)
        st.markdown("### ➕ 신규 아이디어 등록")
        with st.form(key="add_team_form"):
            new_team_name = st.text_input("팀 이름", placeholder="예: 별빛팀")
            new_team_title = st.text_input("아이디어 / 주제명", placeholder="예: 인터랙티브 요소 추가하기")
            new_team_desc = st.text_area("상세 설명", placeholder="사용자가 직접 참여할 수 있는 요소를 적어주세요.")
            add_btn = st.form_submit_button("아이디어 등록하기", use_container_width=True)

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
                is_my_team = (user_team == row['name'])
                card_class = "app-card app-card-myteam" if is_my_team else "app-card"
                badge = "<span class='tag-blue'>우리 팀</span>" if is_my_team else ""

                st.markdown(f"""
                    <div class="{card_class}">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                            <span style="font-weight:800; color:#6C68FF; font-size:1.05rem;">{row['name']} {badge}</span>
                            <span class="tag-blue">디자인 / 기획</span>
                        </div>
                        <div style="font-size:1.15rem; font-weight:800; color:#1E1B4B; margin-bottom:6px;">
                            {row['title']}
                        </div>
                        <div style="color:#64748B; font-size:0.95rem;">
                            {row['description']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                if is_admin or is_my_team:
                    with st.form(key=f"edit_form_{row['id']}"):
                        edit_title = st.text_input("주제 수정", value=row['title'], key=f"title_{row['id']}")
                        edit_desc = st.text_area("설명 수정", value=row['description'], key=f"desc_{row['id']}")
                        if st.form_submit_button("✍️ 내용 수정 저장", use_container_width=True):
                            update_team_info(row['id'], edit_title, edit_desc)
                            st.success("수정 완료!")
                            st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# STAGE 1.5: 5초 카운트다운 (프래그먼트 호출)
# ---------------------------------------------------------
elif current_phase == 'countdown':
    live_sync_and_countdown()

# ---------------------------------------------------------
# STAGE 2: 실시간 아이디어 경매 진행
# ---------------------------------------------------------
elif current_phase == 'auction':
    live_sync_and_countdown()
    st.subheader("🔨 실시간 라이브 경매 진행 중")
    st.caption("타 팀 아이디어에 포인트를 입찰하고 조건부 피드백을 공유하세요.")

    col_auction, col_feed = st.columns([2, 1])

    with col_auction:
        if teams_df.empty:
            st.warning("등록된 팀이 없습니다.")
        else:
            for _, row in teams_df.iterrows():
                is_my_team = (user_team == row['name'])
                
                team_bids = bids_df[bids_df['target_team_id'] == row['id']]
                total_funding = team_bids['amount'].sum() if not team_bids.empty else 0

                card_style = "app-card app-card-myteam" if is_my_team else "app-card"
                badge_html = "<span class='tag-blue'>우리 팀</span>" if is_my_team else ""

                st.markdown(f"""
                    <div class="{card_style}">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                            <span style="font-weight:800; color:#6C68FF; font-size:1.05rem;">{row['name']} {badge_html}</span>
                            <span class="point-chip" style="font-size:0.85rem; padding:4px 10px;">현재 최고가 {total_funding:,} P</span>
                        </div>
                        <div style="font-size:1.2rem; font-weight:900; color:#1E1B4B; margin-bottom:8px;">{row['title']}</div>
                        <div style="color:#64748B; font-size:0.95rem; margin-bottom:12px;">{row['description']}</div>
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
                        submit_bid = st.form_submit_button("입찰하기", use_container_width=True)

                        if submit_bid:
                            if not user_name or user_team == "팀 선택":
                                st.error("상단에서 참가자 이름과 소속 팀을 선택하세요.")
                            elif bid_amount > my_balance:
                                st.error("포인트가 부족합니다.")
                            elif not feedback.strip():
                                st.error("피드백을 작성해야 합니다.")
                            else:
                                add_bid(user_name, user_team, row['id'], bid_amount, feedback)
                                st.success(f"{bid_amount:,} P 입찰 완료!")
                                st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)

    with col_feed:
        st.subheader("⚡ 실시간 입찰 현황")
        if bids_df.empty:
            st.info("아직 제출된 입찰 내역이 없습니다.")
        else:
            for _, bid in bids_df.sort_values(by="id", ascending=False).head(10).iterrows():
                target_rows = teams_df[teams_df['id'] == bid['target_team_id']]
                target_name = target_rows['name'].values[0] if not target_rows.empty else "팀"
                
                st.markdown(f"""
                    <div style="background:#FFFFFF; border:1px solid #E2E8F0; padding:14px; border-radius:16px; margin-bottom:10px; box-shadow:0 4px 12px rgba(108,104,255,0.06);">
                        <div style="font-size:0.85rem; color:#64748B; display:flex; justify-content:space-between;">
                            <span><strong style="color:#1E1B4B;">{bid['user_name']}</strong> ({bid['user_team']})</span>
                            <span class="badge-chip">입찰 중</span>
                        </div>
                        <div style="font-size:1.1rem; font-weight:900; color:#6C68FF; margin:6px 0;">
                            ➔ {target_name} : {bid['amount']:,} P
                        </div>
                        <div style="color:#334155; font-size:0.9rem;">"{bid['feedback']}"</div>
                    </div>
                """, unsafe_allow_html=True)

# ---------------------------------------------------------
# STAGE 2.5: 결과 연출 화면 (프래그먼트 호출)
# ---------------------------------------------------------
elif current_phase == 'result_reveal':
    live_sync_and_countdown()

# ---------------------------------------------------------
# STAGE 3: 경매 마감 및 결과 리포트
# ---------------------------------------------------------
elif current_phase == 'finished':
    live_sync_and_countdown()
    st.subheader("🏆 이번 경매 최종 결과")

    funding_summary = []
    for _, row in teams_df.iterrows():
        team_bids = bids_df[bids_df['target_team_id'] == row['id']]
        total_funding = team_bids['amount'].sum() if not team_bids.empty else 0
        funding_summary.append({"팀": row['name'], "주제": row['title'], "총 펀딩액": total_funding})
    
    summary_df = pd.DataFrame(funding_summary).sort_values(by="총 펀딩액", ascending=False) if funding_summary else pd.DataFrame()

    st.markdown("### 🥇 아이디어 낙찰 순위")
    if not summary_df.empty:
        for idx, row in summary_df.reset_index(drop=True).iterrows():
            rank = idx + 1
            st.markdown(f"""
                <div class="app-card" style="border-left: 6px solid #6C68FF;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:1.15rem; font-weight:800; color:#1E1B4B;">{rank}위 : {row['팀']} - {row['주제']}</span>
                        <span class="point-chip">{row['총 펀딩액']:,} P 낙찰</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### 💎 최고 엔젤 투자자 현황")
    if not bids_df.empty:
        investor_df = bids_df.groupby(["user_name", "user_team"])["amount"].sum().reset_index()
        investor_df = investor_df.sort_values(by="amount", ascending=False)
        
        for idx, row in investor_df.reset_index(drop=True).head(3).iterrows():
            rank = idx + 1
            st.markdown(f"""
                <div style="background:#FFFFFF; padding:14px; border-radius:14px; margin-bottom:10px; border:1px solid #E2E8F0; display:flex; justify-content:space-between; align-items:center;">
                    <span><strong style="color:#6C68FF;">{rank}위</strong> : {row['user_name']} ({row['user_team']})</span>
                    <span style="font-weight:900; color:#1E1B4B;">총 {row['amount']:,} P 투자</span>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### 📥 전체 피드백 다운로드")
    if not bids_df.empty:
        csv_data = bids_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📄 전체 피드백 리포트 CSV 다운로드",
            data=csv_data,
            file_name="sonorus_auction_feedbacks.csv",
            mime="text/csv"
        )
