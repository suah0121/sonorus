import streamlit as st
import pandas as pd
import sqlite3
import time
from datetime import datetime

# ---------------------------------------------------------
# 1. 페이지 기본 설정 & 시안 기반 파스텔 라이트 UI CSS
# ---------------------------------------------------------
st.set_page_config(
    page_title="아이디어 경매전 - SONORUS",
    page_icon="🔨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 시안 컬러 팔레트: 메인 퍼플(#6C68FF), 보조 블루(#A7C7FF), 포인트 옐로우(#FFD868), 서브 핑크(#FFB6D9), 그레이(#F8FAFC)
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    * {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif !important;
    }

    /* Streamlit 기본 프레임워크 요소 숨김 */
    header[data-testid="stHeader"], 
    footer, 
    div[data-testid="stSidebarCollapseButton"],
    section[data-testid="stSidebar"],
    .stDeployButton {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }
    
    /* 소프트 퍼플-블루 라이트 배경 */
    .stApp {
        background: linear-gradient(180deg, #f0f4ff 0%, #f8fafc 100%) !important;
        color: #2d3748 !important;
    }
    
    .main .block-container {
        padding: 1.5rem 2rem !important;
        max-width: 1300px !important;
    }

    /* 입력창 디자인 - 소프트 그레이 보더 및 파스텔 포커스 */
    .stTextInput input, .stTextArea textarea, .stSelectbox select, .stNumberInput input {
        background-color: #ffffff !important;
        color: #1e293b !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 12px !important;
        font-size: 0.98rem !important;
        padding: 0.65rem 0.9rem !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02) !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #6C68FF !important;
        box-shadow: 0 0 0 3px rgba(108, 104, 255, 0.2) !important;
    }
    
    label {
        color: #475569 !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        margin-bottom: 0.4rem !important;
    }

    /* 시안 메인 퍼플 버튼(#6C68FF) */
    .stButton>button, div[data-testid="stFormSubmitButton"]>button {
        background: linear-gradient(135deg, #6C68FF 0%, #5752E5 100%) !important;
        color: #ffffff !important;
        font-size: 1.02rem !important;
        font-weight: 800 !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 0.75rem 1.4rem !important;
        box-shadow: 0 4px 14px rgba(108, 104, 255, 0.35) !important;
        width: 100% !important;
        transition: all 0.2s ease-in-out !important;
    }
    .stButton>button:hover, div[data-testid="stFormSubmitButton"]>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(108, 104, 255, 0.5) !important;
    }

    /* 시안 메인 상단 헤더 바 */
    .app-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #ffffff;
        padding: 18px 28px;
        border-radius: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 8px 25px rgba(108, 104, 255, 0.08);
        margin-bottom: 25px;
    }
    .app-title {
        font-size: 1.7rem;
        font-weight: 900;
        color: #6C68FF;
        letter-spacing: -0.5px;
    }
    .badge-stage {
        background: #F0F0FF;
        color: #6C68FF;
        padding: 8px 18px;
        border-radius: 30px;
        font-size: 0.88rem;
        font-weight: 800;
        border: 1px solid #A7C7FF;
    }

    /* 시안 카드 형태 UI */
    .glass-card {
        background: #ffffff;
        border: 1px solid #f1f5f9;
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(148, 163, 184, 0.12);
    }
    .card-myteam {
        border: 2px solid #6C68FF !important;
        background: linear-gradient(180deg, #ffffff 0%, #f5f3ff 100%) !important;
        box-shadow: 0 10px 30px rgba(108, 104, 255, 0.18) !important;
    }

    /* 시안 대형 카운트다운 전광판 */
    .countdown-container {
        text-align: center;
        padding: 60px 20px;
        background: linear-gradient(135deg, #ffffff 0%, #f0f4ff 100%);
        border-radius: 24px;
        border: 2px solid #A7C7FF;
        box-shadow: 0 15px 35px rgba(108, 104, 255, 0.15);
        margin: 30px auto;
        max-width: 750px;
    }
    .countdown-digit {
        font-size: 7.5rem;
        font-weight: 900;
        color: #6C68FF;
        margin: 10px 0;
        line-height: 1;
    }
    .point-badge {
        background: #FFD868;
        color: #1e1b4b;
        font-weight: 900;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.9rem;
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
    c.execute("DELETE FROM app_state WHERE key = 'cd_start'")
    c.execute("DELETE FROM app_state WHERE key = 'reveal_start'")
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# 3. 실시간 동기화 및 카운트다운 프래그먼트 엔진
# ---------------------------------------------------------
@st.fragment(run_every=1)
def live_sync_and_countdown():
    current_phase = get_state("phase", "prep")
    last_phase = st.session_state.get("last_synced_phase", None)
    
    # 1) Phase 변화 시 전체 페이지 갱신
    if last_phase != current_phase:
        st.session_state["last_synced_phase"] = current_phase
        st.rerun()

    # 2) 경매 시작 카운트다운 진행
    if current_phase == "countdown":
        try:
            cd_start = float(get_state("cd_start", time.time()))
        except (ValueError, TypeError):
            cd_start = time.time()
            
        elapsed = time.time() - cd_start
        remaining = max(0, int(5 - elapsed))
        
        if remaining > 0:
            st.markdown(f"""
                <div class="countdown-container">
                    <h2 style="color: #6C68FF; margin:0;">🔨 지금, 다음 아이디어를 경매해보세요!</h2>
                    <p style="color: #64748b; font-size: 1.1rem; margin-top: 10px;">사용자가 직접 참여하는 경매전이 곧 개장합니다.</p>
                    <div class="countdown-digit">{remaining}</div>
                    <p style="color: #475569; font-weight: 800;">초 후 실시간 경매장이 개장합니다...</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            set_state("phase", "auction")
            st.rerun()

    # 3) 결과 집계 카운트다운 연출
    elif current_phase == "result_reveal":
        try:
            reveal_start = float(get_state("reveal_start", time.time()))
        except (ValueError, TypeError):
            reveal_start = time.time()
            
        elapsed = time.time() - reveal_start
        remaining = max(0, int(5 - elapsed))
        
        if remaining > 0:
            st.markdown(f"""
                <div class="countdown-container" style="border-color:#FFD868;">
                    <h2 style="color: #1e1b4b; margin:0;">🎉 최종 경매 결과 집계 중!</h2>
                    <p style="color: #64748b; font-size: 1.1rem; margin-top: 10px;">과연 최고의 펀딩 유치 팀은 누구일까요?</p>
                    <div class="countdown-digit" style="color:#FFB6D9;">{remaining}</div>
                    <p style="color: #6C68FF; font-weight: 800;">초 후 최종 낙찰 결과가 공개됩니다!</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            set_state("phase", "finished")
            st.rerun()

# ---------------------------------------------------------
# 4. 메인 대시보드
# ---------------------------------------------------------
current_phase = get_state("phase", "prep")

phase_badge = {
    'prep': 'STAGE 1 : 준비 및 팀 등록',
    'countdown': '⏳ 경매 시작 5초 전!',
    'auction': 'STAGE 2 : 실시간 진행 중',
    'result_reveal': '🏆 결과 집계 중...',
    'finished': 'STAGE 3 : 최종 경매 결과'
}.get(current_phase, 'STAGE 1')

st.markdown(f"""
    <div class="app-header">
        <div class="app-title">🔨 아이디어 경매전</div>
        <div class="badge-stage">{phase_badge}</div>
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
    user_team = st.selectbox("소속 팀 선택", options=["팀 선택"] + team_options, index=0)
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
    st.markdown(f"<div style='font-size:1.4rem; font-weight:900; color:#6C68FF; margin-top:2px;'>🟡 {my_balance:,} P</div>", unsafe_allow_html=True)

with col_p4:
    admin_pwd = st.text_input("관리자 암호", type="password", placeholder="sonorus123")
    is_admin = (admin_pwd == "sonorus123")

if is_admin:
    st.success("🔒 관리자 권한 인증 완료")
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if current_phase == 'prep':
            if st.button("🚀 경매 시작 (5초 카운트다운)", use_container_width=True):
                set_state("cd_start", time.time())
                set_state("phase", "countdown")
                st.rerun()
        elif current_phase in ['auction', 'countdown']:
            if st.button("🚨 경매 마감 & 결과 발표 연출", use_container_width=True):
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
    st.subheader("💡 팀별 아이디어 등록 및 가이드")
    st.caption("새로운 아이디어 팀을 생성하거나, 우리 팀의 프로젝트 제목과 세부 설명을 작성하세요.")

    col_create, col_teams = st.columns([1, 2])

    with col_create:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### ➕ 신규 아이디어 등록")
        with st.form(key="add_team_form"):
            new_team_name = st.text_input("팀 이름", placeholder="예: 별빛팀")
            new_team_title = st.text_input("아이디어 / 주제명", placeholder="예: 인터랙티브 요소 추가하기")
            new_team_desc = st.text_area("상세 설명", placeholder="사용자가 직접 참여할 수 있는 요소를 설명하세요.")
            add_btn = st.form_submit_button("아이디어 등록하기", use_container_width=True)

            if add_btn:
                if not new_team_name or not new_team_title or not new_team_desc:
                    st.error("모든 항목을 작성해 주세요.")
                else:
                    if add_team(new_team_name, new_team_title, new_team_desc):
                        st.success(f"'{new_team_name}' 생성 완료!")
                        st.rerun()
                    else:
                        st.error("이미 존재하는 팀 이름입니다.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_teams:
        st.markdown("### 📋 등록된 아이디어 목록")
        if teams_df.empty:
            st.info("아직 등록된 아이디어가 없습니다. 왼쪽에서 신규 아이디어를 등록해 주세요.")
        else:
            for _, row in teams_df.iterrows():
                is_my_team = (user_team == row['name'])
                card_class = "glass-card card-myteam" if is_my_team else "glass-card"
                badge = "<span style='background:#FFD868; color:#1e1b4b; padding:2px 8px; border-radius:6px; font-size:0.8rem; font-weight:800; float:right;'>우리 팀</span>" if is_my_team else ""

                st.markdown(f"""
                    <div class="{card_class}">
                        <div style="font-size:1.15rem; font-weight:800; color:#6C68FF; margin-bottom:6px;">
                            팀명: {row['name']} {badge}
                        </div>
                        <div style="font-size:1.1rem; font-weight:800; color:#1e293b; margin-bottom:6px;">
                            주제: {row['title']}
                        </div>
                        <div style="color:#64748b; font-size:0.95rem;">
                            {row['description']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                if is_admin or is_my_team:
                    with st.form(key=f"edit_form_{row['id']}"):
                        edit_title = st.text_input("주제 수정", value=row['title'], key=f"title_{row['id']}")
                        edit_desc = st.text_area("설명 수정", value=row['description'], key=f"desc_{row['id']}")
                        if st.form_submit_button("✍️ 수정 내용 저장", use_container_width=True):
                            update_team_info(row['id'], edit_title, edit_desc)
                            st.success("수정사항이 저장되었습니다.")
                            st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# STAGE 1.5: 5초 카운트다운 화면 (프래그먼트 호출)
# ---------------------------------------------------------
elif current_phase == 'countdown':
    live_sync_and_countdown()

# ---------------------------------------------------------
# STAGE 2: 실시간 아이디어 경매 진행
# ---------------------------------------------------------
elif current_phase == 'auction':
    live_sync_and_countdown()
    st.subheader("🔨 실시간 아이디어 경매 진행 중")
    st.caption("타 팀 아이디어에 펀딩을 진행하고 조건부 피드백을 남겨주세요. (자기 팀 투자 불가)")

    col_auction, col_feed = st.columns([2, 1])

    with col_auction:
        if teams_df.empty:
            st.warning("등록된 팀이 없습니다.")
        else:
            for _, row in teams_df.iterrows():
                is_my_team = (user_team == row['name'])
                
                team_bids = bids_df[bids_df['target_team_id'] == row['id']]
                total_funding = team_bids['amount'].sum() if not team_bids.empty else 0

                card_style = "glass-card card-myteam" if is_my_team else "glass-card"
                badge_html = "<span style='background:#FFD868; color:#1e1b4b; padding:2px 8px; border-radius:6px; font-size:0.8rem; font-weight:800; float:right;'>우리 팀</span>" if is_my_team else ""

                st.markdown(f"""
                    <div class="{card_style}">
                        <div style="font-size:1.2rem; font-weight:800; color:#1e293b; margin-bottom:6px;">
                            팀명: {row['name']} | 주제: {row['title']} {badge_html}
                        </div>
                        <div style="color:#64748b; font-size:0.95rem; margin-bottom:12px;">{row['description']}</div>
                        <div style="font-size:0.85rem; color:#94a3b8; font-weight:700;">현재 누적 유치 포인트</div>
                        <div style="font-size:1.45rem; font-weight:900; color:#6C68FF;">🟡 {total_funding:,} P</div>
                    </div>
                """, unsafe_allow_html=True)

                if is_my_team:
                    st.caption("자기 팀에는 입찰할 수 없습니다.")
                else:
                    with st.form(key=f"bid_form_{row['id']}"):
                        bid_amount = st.number_input(
                            "입찰 포인트 (P)",
                            min_value=10000,
                            max_value=max(10000, my_balance),
                            step=50000,
                            key=f"amount_{row['id']}"
                        )
                        feedback = st.text_area(
                            "입찰 이유 및 조건부 피드백 (필수 작성)",
                            placeholder="이 아이디어가 매력적인 이유 및 보완 제안을 적어주세요.",
                            key=f"feedback_{row['id']}"
                        )
                        submit_bid = st.form_submit_button("입찰하기", use_container_width=True)

                        if submit_bid:
                            if not user_name or user_team == "팀 선택":
                                st.error("상단에서 내 이름과 팀을 먼저 설정해 주세요.")
                            elif bid_amount > my_balance:
                                st.error("잔액이 부족합니다.")
                            elif not feedback.strip():
                                st.error("피드백 내용을 작성해 주세요.")
                            else:
                                add_bid(user_name, user_team, row['id'], bid_amount, feedback)
                                st.success(f"{bid_amount:,} P 입찰 제출 완료!")
                                st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)

    with col_feed:
        st.subheader("⚡ 실시간 입찰 피드")
        if bids_df.empty:
            st.info("아직 입찰 내역이 없습니다.")
        else:
            for _, bid in bids_df.sort_values(by="id", ascending=False).head(10).iterrows():
                target_rows = teams_df[teams_df['id'] == bid['target_team_id']]
                target_name = target_rows['name'].values[0] if not target_rows.empty else "팀"
                
                st.markdown(f"""
                    <div style="background:#ffffff; border:1px solid #e2e8f0; padding:14px; border-radius:16px; margin-bottom:12px; box-shadow:0 4px 12px rgba(148, 163, 184, 0.12);">
                        <div style="font-size:0.85rem; color:#64748b;">
                            <strong style="color:#1e293b;">{bid['user_name']} ({bid['user_team']})</strong> ➔ <span style="color:#6C68FF; font-weight:800;">{target_name}</span>
                        </div>
                        <div style="font-size:1.15rem; font-weight:900; color:#6C68FF; margin:4px 0;">🟡 {bid['amount']:,} P</div>
                        <div style="color:#334155; font-size:0.9rem;">"{bid['feedback']}"</div>
                    </div>
                """, unsafe_allow_html=True)

# ---------------------------------------------------------
# STAGE 2.5: 결과 집계 연출 화면 (프래그먼트 호출)
# ---------------------------------------------------------
elif current_phase == 'result_reveal':
    live_sync_and_countdown()

# ---------------------------------------------------------
# STAGE 3: 경매 마감 및 결과 리포트
# ---------------------------------------------------------
elif current_phase == 'finished':
    live_sync_and_countdown()
    st.subheader("🏆 최종 낙찰 결과 현황")

    funding_summary = []
    for _, row in teams_df.iterrows():
        team_bids = bids_df[bids_df['target_team_id'] == row['id']]
        total_funding = team_bids['amount'].sum() if not team_bids.empty else 0
        funding_summary.append({"팀": row['name'], "주제": row['title'], "총 펀딩액": total_funding})
    
    summary_df = pd.DataFrame(funding_summary).sort_values(by="총 펀딩액", ascending=False) if funding_summary else pd.DataFrame()

    st.markdown("### 🥇 최고 낙찰 아이디어 순위")
    if not summary_df.empty:
        for idx, row in summary_df.reset_index(drop=True).iterrows():
            rank = idx + 1
            st.markdown(f"""
                <div class="glass-card" style="border-left: 6px solid #6C68FF;">
                    <div style="font-size:1.15rem; font-weight:800; color:#1e293b;">{rank}위 : 팀명 [{row['팀']}] — 주제: {row['주제']}</div>
                    <div style="font-size:1.4rem; font-weight:900; color:#6C68FF; margin-top:4px;">최종 낙찰가 🟡 {row['총 펀딩액']:,} P</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### 💎 최고의 엔젤 투자자 순위")
    if not bids_df.empty:
        investor_df = bids_df.groupby(["user_name", "user_team"])["amount"].sum().reset_index()
        investor_df = investor_df.sort_values(by="amount", ascending=False)
        
        for idx, row in investor_df.reset_index(drop=True).head(3).iterrows():
            rank = idx + 1
            st.markdown(f"""
                <div style="background:#ffffff; padding:14px; border-radius:12px; margin-bottom:10px; border:1px solid #e2e8f0; box-shadow:0 4px 12px rgba(148, 163, 184, 0.08);">
                    <strong style="color:#6C68FF;">{rank}위</strong> : {row['user_name']} ({row['user_team']}) — 총 <strong style="color:#1e293b;">🟡 {row['amount']:,} P</strong> 집행
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### 📥 전체 피드백 데이터 다운로드")
    if not bids_df.empty:
        csv_data = bids_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📄 전체 피드백 CSV 다운로드",
            data=csv_data,
            file_name="sonorus_auction_feedbacks.csv",
            mime="text/csv"
        )
