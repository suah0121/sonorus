import streamlit as st
import pandas as pd
import sqlite3
import time
from datetime import datetime

# ---------------------------------------------------------
# 1. 페이지 기본 설정 & 게이밍 네온 UI 디자인
# ---------------------------------------------------------
st.set_page_config(
    page_title="SONORUS 아이디어 경매전",
    page_icon="🪙",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 고급 다크 네온 & 게이밍 레이아웃 CSS
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    * {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif !important;
    }

    /* Streamlit 프레임워크 요소 완전 차단 */
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
        background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #090d16 70%) !important;
        color: #f8fafc !important;
    }
    
    .main .block-container {
        padding: 1.5rem 2rem !important;
        max-width: 1400px !important;
    }

    /* 폼 입력 필드 고대비 가독성 보장 */
    .stTextInput input, .stTextArea textarea, .stSelectbox select, .stNumberInput input {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border: 1px solid #3b82f6 !important;
        border-radius: 10px !important;
        font-size: 1rem !important;
        padding: 0.65rem 0.9rem !important;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.5) !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #ec4899 !important;
        box-shadow: 0 0 12px rgba(236, 72, 153, 0.5) !important;
    }
    
    label {
        color: #93c5fd !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        margin-bottom: 0.4rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* 버튼 게이밍 그래디언트 */
    .stButton>button, div[data-testid="stFormSubmitButton"]>button {
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%) !important;
        color: #ffffff !important;
        font-size: 1.05rem !important;
        font-weight: 800 !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 0.75rem 1.4rem !important;
        box-shadow: 0 0 18px rgba(236, 72, 153, 0.4) !important;
        width: 100% !important;
        transition: all 0.2s ease-in-out !important;
    }
    .stButton>button:hover, div[data-testid="stFormSubmitButton"]>button:hover {
        transform: translateY(-2px) scale(1.01) !important;
        box-shadow: 0 0 25px rgba(236, 72, 153, 0.7) !important;
    }

    /* 게임 전광판 커스텀 헤더 */
    .app-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(15, 23, 42, 0.85);
        padding: 20px 28px;
        border-radius: 16px;
        border: 1px solid #3b82f6;
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.2);
        backdrop-filter: blur(10px);
        margin-bottom: 25px;
    }
    .app-title {
        font-size: 1.8rem;
        font-weight: 900;
        background: linear-gradient(90deg, #f59e0b 0%, #ec4899 50%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
    }
    .badge-stage {
        background: linear-gradient(90deg, #312e81 0%, #4338ca 100%);
        color: #38bdf8;
        padding: 8px 18px;
        border-radius: 30px;
        font-size: 0.9rem;
        font-weight: 800;
        border: 1px solid #38bdf8;
        box-shadow: 0 0 12px rgba(56, 189, 248, 0.4);
    }

    /* 대시보드 커스텀 카드 */
    .glass-card {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(8px);
    }
    .card-myteam {
        border: 2px solid #f59e0b !important;
        box-shadow: 0 0 20px rgba(245, 158, 11, 0.35) !important;
        background: linear-gradient(145deg, #0f172a 0%, #1c1917 100%) !important;
    }

    /* 카운트다운 대형 네온 전광판 */
    .countdown-container {
        text-align: center;
        padding: 70px 20px;
        background: radial-gradient(circle, #311b92 0%, #090d16 100%);
        border-radius: 24px;
        border: 2px solid #ec4899;
        box-shadow: 0 0 50px rgba(236, 72, 153, 0.5);
        margin: 30px auto;
        max-width: 750px;
    }
    .countdown-digit {
        font-size: 7.5rem;
        font-weight: 900;
        color: #f59e0b;
        text-shadow: 0 0 30px rgba(245, 158, 11, 0.9), 0 0 60px rgba(236, 72, 153, 0.6);
        margin: 15px 0;
        line-height: 1;
    }
    .neon-gold {
        color: #f59e0b;
        font-weight: 900;
        text-shadow: 0 0 10px rgba(245, 158, 11, 0.5);
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
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# 3. 실시간 동기화 프래그먼트 엔진 (@st.fragment)
# ---------------------------------------------------------
@st.fragment(run_every=1)
def live_sync_engine():
    current_phase = get_state("phase", "prep")
    last_phase = st.session_state.get("last_synced_phase", None)
    
    if current_phase == "countdown":
        st.rerun()
    elif last_phase != current_phase:
        st.session_state["last_synced_phase"] = current_phase
        st.rerun()

live_sync_engine()

# ---------------------------------------------------------
# 4. 헤더 영역 & 사용자 대시보드
# ---------------------------------------------------------
current_phase = get_state("phase", "prep")

phase_badge = {
    'prep': 'STAGE 1 : 준비 및 팀 등록',
    'countdown': '⏳ 경매 개장 5초 전!',
    'auction': 'STAGE 2 : 실시간 경매 진행 중',
    'finished': 'STAGE 3 : 최종 경매 결과'
}.get(current_phase, 'STAGE 1')

st.markdown(f"""
    <div class="app-header">
        <div class="app-title">🪙 SONORUS AUCTION</div>
        <div class="badge-stage">{phase_badge}</div>
    </div>
""", unsafe_allow_html=True)

teams_df = get_teams()
team_options = teams_df['name'].tolist() if not teams_df.empty else []

col_p1, col_p2, col_p3, col_p4 = st.columns([1.5, 1.5, 1.5, 2])

with col_p1:
    user_name = st.text_input("참가자 이름", value=st.session_state.get("user_name", ""), placeholder="홍길동")
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
    st.markdown("<label>내 자산 잔액</label>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:1.45rem; font-weight:900; color:#f59e0b; margin-top:2px;'>🪙 {my_balance:,} 소노</div>", unsafe_allow_html=True)

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
            if st.button("🚨 경매 마감 및 시상식", use_container_width=True):
                set_state("phase", "finished")
                st.rerun()
        elif current_phase == 'finished':
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
    st.subheader("📋 팀별 주제 및 발표 내용 준비")
    st.caption("새로운 팀을 생성하거나, 내 팀의 발표 제목과 활동 내용을 작성해 주세요.")

    col_create, col_teams = st.columns([1, 2])

    with col_create:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### ➕ 신규 팀 등록")
        with st.form(key="add_team_form"):
            new_team_name = st.text_input("팀 이름", placeholder="예: 1팀")
            new_team_title = st.text_input("프로젝트 / 주제명", placeholder="예: AI 사운드 가이드")
            new_team_desc = st.text_area("활동 및 핵심 목표", placeholder="상세 계획을 작성하세요.")
            add_btn = st.form_submit_button("팀 등록하기", use_container_width=True)

            if add_btn:
                if not new_team_name or not new_team_title or not new_team_desc:
                    st.error("모든 항목을 입력해야 합니다.")
                else:
                    if add_team(new_team_name, new_team_title, new_team_desc):
                        st.success(f"'{new_team_name}' 생성 완료!")
                        st.rerun()
                    else:
                        st.error("이미 등록된 팀 이름입니다.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_teams:
        st.markdown("### 📋 등록된 팀 목록")
        if teams_df.empty:
            st.info("등록된 팀이 없습니다. 왼쪽에서 신규 팀을 등록해 주세요.")
        else:
            for _, row in teams_df.iterrows():
                is_my_team = (user_team == row['name'])
                card_class = "glass-card card-myteam" if is_my_team else "glass-card"
                badge = "<span style='background:#f59e0b; color:#000; padding:2px 8px; border-radius:6px; font-size:0.8rem; font-weight:800; float:right;'>우리 팀</span>" if is_my_team else ""

                st.markdown(f"""
                    <div class="{card_class}">
                        <div style="font-size:1.2rem; font-weight:800; color:#818cf8; margin-bottom:8px;">
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
                            st.success("수정사항이 저장되었습니다.")
                            st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# STAGE 1.5: 5초 긴장감 네온 전광판 카운트다운!
# ---------------------------------------------------------
elif current_phase == 'countdown':
    try:
        cd_start = float(get_state("cd_start", time.time()))
    except ValueError:
        cd_start = time.time()
        
    elapsed = time.time() - cd_start
    remaining = max(0, int(5 - elapsed))
    
    if remaining > 0:
        st.markdown(f"""
            <div class="countdown-container">
                <h2 style="color: #a5b4fc; margin:0; letter-spacing:1px;">🔥 SONORUS 아이디어 경매전 개장 직전! 🔥</h2>
                <p style="color: #cbd5e1; font-size: 1.15rem; margin-top: 10px;">투자 전략과 조건부 피드백을 준비하세요!</p>
                <div class="countdown-digit">{remaining}</div>
                <p style="color: #f59e0b; font-weight: 800; font-size:1.1rem;">초 후 실시간 경매장이 개장합니다...</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        set_state("phase", "auction")
        st.rerun()

# ---------------------------------------------------------
# STAGE 2: 실시간 아이디어 경매 진행
# ---------------------------------------------------------
elif current_phase == 'auction':
    st.subheader("🔨 실시간 라이브 경매 진행 중")
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

                card_style = "glass-card card-myteam" if is_my_team else "glass-card"
                badge_html = "<span style='background:#f59e0b; color:#000; padding:2px 8px; border-radius:6px; font-size:0.8rem; font-weight:800; float:right;'>우리 팀</span>" if is_my_team else ""

                st.markdown(f"""
                    <div class="{card_style}">
                        <div style="font-size:1.25rem; font-weight:800; color:#ffffff; margin-bottom:6px;">
                            팀명: {row['name']} | 주제: {row['title']} {badge_html}
                        </div>
                        <div style="color:#94a3b8; font-size:0.95rem; margin-bottom:12px;">{row['description']}</div>
                        <div style="font-size:0.85rem; color:#cbd5e1;">현재 누적 유치 펀딩액</div>
                        <div style="font-size:1.5rem; font-weight:900; color:#f59e0b;">🪙 {total_funding:,} 소노</div>
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
                            "투자 이유 및 조건부 피드백 (필수 작성)",
                            placeholder="인상 깊은 점과 보완해야 할 점을 상세히 작성해 주세요.",
                            key=f"feedback_{row['id']}"
                        )
                        submit_bid = st.form_submit_button("🪙 펀딩 & 피드백 제출", use_container_width=True)

                        if submit_bid:
                            if not user_name or user_team == "팀 선택":
                                st.error("상단에서 내 이름과 팀을 먼저 설정해 주세요.")
                            elif bid_amount > my_balance:
                                st.error("잔액이 부족합니다.")
                            elif not feedback.strip():
                                st.error("피드백 내용을 작성해 주세요.")
                            else:
                                add_bid(user_name, user_team, row['id'], bid_amount, feedback)
                                st.success(f"{bid_amount:,} 소노 펀딩 제출 완료!")
                                st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)

    with col_feed:
        st.subheader("⚡ 실시간 피드백 피드")
        if bids_df.empty:
            st.info("아직 제출된 피드백 내역이 없습니다.")
        else:
            for _, bid in bids_df.sort_values(by="id", ascending=False).head(10).iterrows():
                target_rows = teams_df[teams_df['id'] == bid['target_team_id']]
                target_name = target_rows['name'].values[0] if not target_rows.empty else "팀"
                
                st.markdown(f"""
                    <div style="background:rgba(15, 23, 42, 0.9); border:1px solid #334155; padding:14px; border-radius:12px; margin-bottom:12px; box-shadow:0 4px 12px rgba(0,0,0,0.3);">
                        <div style="font-size:0.85rem; color:#94a3b8;">
                            <strong style="color:#ffffff;">{bid['user_name']} ({bid['user_team']})</strong> ➔ <span style="color:#a855f7; font-weight:bold;">{target_name}</span>
                        </div>
                        <div style="font-size:1.15rem; font-weight:900; color:#f59e0b; margin:4px 0;">🪙 {bid['amount']:,} 소노</div>
                        <div style="color:#e2e8f0; font-size:0.9rem;">"{bid['feedback']}"</div>
                    </div>
                """, unsafe_allow_html=True)

# ---------------------------------------------------------
# STAGE 3: 경매 마감 및 결과 시상식
# ---------------------------------------------------------
elif current_phase == 'finished':
    st.subheader("🏆 최종 경매 마감 및 리포트")

    funding_summary = []
    for _, row in teams_df.iterrows():
        team_bids = bids_df[bids_df['target_team_id'] == row['id']]
        total_funding = team_bids['amount'].sum() if not team_bids.empty else 0
        funding_summary.append({"팀": row['name'], "주제": row['title'], "총 펀딩액": total_funding})
    
    summary_df = pd.DataFrame(funding_summary).sort_values(by="총 펀딩액", ascending=False) if funding_summary else pd.DataFrame()

    st.markdown("### 🥇 대박 유니콘상 (최고 펀딩 유치 팀)")
    if not summary_df.empty:
        for idx, row in summary_df.reset_index(drop=True).iterrows():
            rank = idx + 1
            st.markdown(f"""
                <div class="glass-card" style="border-left: 6px solid #f59e0b; box-shadow: 0 0 20px rgba(245, 158, 11, 0.2);">
                    <div style="font-size:1.15rem; font-weight:800;">{rank}위 : 팀명 [{row['팀']}] — 주제: {row['주제']}</div>
                    <div style="font-size:1.4rem; font-weight:900; color:#f59e0b; margin-top:4px;">총 🪙 {row['총 펀딩액']:,} 소노 유치</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### 💎 최고의 엔젤 투자자상")
    if not bids_df.empty:
        investor_df = bids_df.groupby(["user_name", "user_team"])["amount"].sum().reset_index()
        investor_df = investor_df.sort_values(by="amount", ascending=False)
        
        for idx, row in investor_df.reset_index(drop=True).head(3).iterrows():
            rank = idx + 1
            st.markdown(f"""
                <div style="background:#0f172a; padding:14px; border-radius:10px; margin-bottom:10px; border:1px solid #334155;">
                    <strong style="color:#a855f7;">{rank}위</strong> : {row['user_name']} ({row['user_team']}) — 총 <strong style="color:#ec4899;">🪙 {row['amount']:,} 소노</strong> 투자 완료
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### 📥 전체 제출 피드백 데이터 다운로드")
    if not bids_df.empty:
        csv_data = bids_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📄 전체 피드백 CSV 리포트 다운로드",
            data=csv_data,
            file_name="sonorus_auction_feedbacks.csv",
            mime="text/csv"
        )
