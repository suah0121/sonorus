import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# ---------------------------------------------------------
# 1. 페이지 기본 설정 & 깨진 위젯 요소 완벽 제거 CSS
# ---------------------------------------------------------
st.set_page_config(
    page_title="SONORUS 아이디어 경매전",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    * {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif !important;
    }

    /* 전체 배경 */
    .stApp {
        background-color: #0f172a !important;
        color: #f8fafc !important;
    }

    /* 상단 하얀색 헤더 바 및 깨진 아이콘 텍스트 제거 */
    header[data-testid="stHeader"] {
        background-color: #0f172a !important;
        border-bottom: none !important;
    }
    
    /* 사이드바 접기/열기 버튼의 깨진 텍스트(keyboard_double_...) 숨기기 */
    button[data-testid="stSidebarCollapseButton"], 
    button[data-testid="baseButton-header"],
    [data-testid="stHeader"] * {
        color: #0f172a !important;
        overflow: hidden !important;
    }
    
    /* 본문 상단 여백 축소 */
    .main .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
    }

    /* 사이드바 스타일링 */
    section[data-testid="stSidebar"] {
        background-color: #1e293b !important;
        border-right: 1px solid #334155 !important;
    }
    section[data-testid="stSidebar"] * {
        color: #f8fafc !important;
    }
    section[data-testid="stSidebar"] .stCaption {
        color: #94a3b8 !important;
    }

    /* Input/Textarea 가독성 및 비밀번호 보기 버튼 찌꺼기 제거 */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #0f172a !important;
        color: #f8fafc !important;
        border: 1px solid #475569 !important;
        border-radius: 8px !important;
    }
    
    /* 비밀번호 우측 눈 아이콘 깨짐 방지 */
    .stTextInput div[data-baseweb="input"] {
        background-color: #0f172a !important;
        border-radius: 8px !important;
    }
    .stTextInput button {
        background-color: transparent !important;
        border: none !important;
        color: #94a3b8 !important;
    }

    /* 버튼 스타일 */
    .stButton>button {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.6rem 1.2rem !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3) !important;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%) !important;
        box-shadow: 0 6px 16px rgba(99, 102, 241, 0.4) !important;
    }

    /* 카드 커스텀 UI */
    .glass-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .my-team-card {
        border: 2px solid #f59e0b !important;
        background-color: #1e2538 !important;
    }

    /* 배지 및 태그 */
    .badge-myteam {
        background-color: #f59e0b;
        color: #0f172a;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: bold;
        float: right;
    }
    .status-badge {
        background-color: #334155;
        color: #38bdf8;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 10px;
    }

    /* 헤더 텍스트 */
    .brand-header {
        font-size: 1.8rem;
        font-weight: 800;
        color: #818cf8;
        letter-spacing: -0.5px;
        margin-bottom: 5px;
    }
    .sub-text {
        color: #94a3b8;
        font-size: 0.95rem;
    }
    .accent-amount {
        color: #f59e0b;
        font-weight: 800;
        font-size: 1.4rem;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SQLite 데이터베이스
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
        (user_name, user_team, target_team_id, amount, feedback)
    )
    conn.commit()
    conn.close()

def get_phase():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT value FROM app_state WHERE key = 'phase'")
    row = c.fetchone()
    conn.close()
    return row[0] if row else 'prep'

def set_phase(new_phase):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("REPLACE INTO app_state (key, value) VALUES ('phase', ?)", (new_phase,))
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# 3. 사이드바 UI
# ---------------------------------------------------------
st.sidebar.markdown("<div class='brand-header'>SONORUS</div>", unsafe_allow_html=True)
st.sidebar.markdown("<div class='sub-text' style='margin-bottom:20px;'>아이디어 경매전 서비스</div>", unsafe_allow_html=True)

# 참가자 등록
st.sidebar.markdown("#### 참가자 프로필")
user_name = st.sidebar.text_input("이름", value=st.session_state.get("user_name", ""), placeholder="홍길동")

teams_df = get_teams()
team_options = teams_df['name'].tolist() if not teams_df.empty else []

user_team = st.sidebar.selectbox("소속 팀", options=["팀 선택"] + team_options, index=0)

if user_name and user_team != "팀 선택":
    st.session_state["user_name"] = user_name
    st.session_state["user_team"] = user_team
    st.sidebar.success(f"{user_name} ({user_team}) 접속 중")
else:
    st.sidebar.info("이름과 팀을 설정해 주세요.")

# 보유 자산
INITIAL_BALANCE = 1000000
bids_df = get_bids()

if user_name:
    my_bids = bids_df[bids_df['user_name'] == user_name]
    used_amount = my_bids['amount'].sum() if not my_bids.empty else 0
    my_balance = INITIAL_BALANCE - used_amount
else:
    my_balance = INITIAL_BALANCE

st.sidebar.markdown("---")
st.sidebar.markdown("<div class='sub-text'>보유 자산</div>", unsafe_allow_html=True)
st.sidebar.markdown(f"<div class='accent-amount'>{my_balance:,} 소노</div>", unsafe_allow_html=True)
st.sidebar.caption("미사용 소노는 마감 시 자동 소멸됩니다.")

# 관리자 메뉴
st.sidebar.markdown("---")
st.sidebar.markdown("<div class='sub-text'>관리자 콘솔</div>", unsafe_allow_html=True)
ADMIN_PASSWORD = "sonorus123"
admin_password = st.sidebar.text_input("비밀번호", type="password", key="admin_pwd_input")
is_admin = (admin_password == ADMIN_PASSWORD)

current_phase = get_phase()

if is_admin:
    st.sidebar.success("관리자 권한 인증됨")
    
    if current_phase == 'prep':
        if st.sidebar.button("경매 시작하기", use_container_width=True):
            set_phase('auction')
            st.rerun()
    elif current_phase == 'auction':
        if st.sidebar.button("경매 마감 및 결과 발표", use_container_width=True):
            set_phase('finished')
            st.rerun()
    elif current_phase == 'finished':
        if st.sidebar.button("준비 단계로 리셋", use_container_width=True):
            set_phase('prep')
            st.rerun()

# ---------------------------------------------------------
# 4. 메인 영역
# ---------------------------------------------------------
st.markdown("<div class='brand-header' style='font-size: 2.2rem;'>SONORUS 아이디어 경매전</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# STAGE 1: 경매 준비
# ---------------------------------------------------------
if current_phase == 'prep':
    st.markdown("<div class='status-badge'>STAGE 1 : 준비 및 팀 소개</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-text' style='margin-bottom: 25px;'>팀별 프로젝트 주제와 활동 내용을 작성하고 공유하는 단계입니다.</div>", unsafe_allow_html=True)

    col_add, col_list = st.columns([1, 2])

    with col_add:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 팀 신규 등록")
        with st.form(key="add_team_form"):
            new_team_name = st.text_input("팀 이름", placeholder="예: 1팀")
            new_team_title = st.text_input("프로젝트 / 주제명", placeholder="예: AI 사운드 가이드")
            new_team_desc = st.text_area("핵심 활동 및 목표 설명", placeholder="활동에 대한 세부 설명을 작성하세요.")
            add_btn = st.form_submit_button("팀 생성", use_container_width=True)

            if add_btn:
                if not new_team_name or not new_team_title or not new_team_desc:
                    st.error("모든 입력란을 작성해 주세요.")
                else:
                    if add_team(new_team_name, new_team_title, new_team_desc):
                        st.success(f"'{new_team_name}' 생성 완료!")
                        st.rerun()
                    else:
                        st.error("동일한 이름의 팀이 이미 존재합니다.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_list:
        st.markdown("### 등록된 팀 프로젝트 목록")
        if teams_df.empty:
            st.info("아직 등록된 팀이 없습니다. 왼쪽에서 팀을 생성해 주세요.")
        else:
            for _, row in teams_df.iterrows():
                is_my_team = (user_team == row['name'])
                
                with st.expander(f"📌 {row['name']} : {row['title']}", expanded=True):
                    if is_admin or is_my_team:
                        st.caption("내용 수정 (내 팀 또는 관리자만 가능)")
                        edit_title = st.text_input("주제", value=row['title'], key=f"title_{row['id']}")
                        edit_desc = st.text_area("설명", value=row['description'], key=f"desc_{row['id']}")
                        if st.button("수정 내용 저장", key=f"btn_{row['id']}"):
                            update_team_info(row['id'], edit_title, edit_desc)
                            st.success("저장되었습니다.")
                            st.rerun()
                    else:
                        st.markdown(f"#### {row['title']}")
                        st.write(row['description'])

    st.markdown("---")
    if is_admin:
        if st.button("경매 시작하기 (준비 단계 종료)", use_container_width=True):
            set_phase('auction')
            st.rerun()

# ---------------------------------------------------------
# STAGE 2: 실시간 경매 진행
# ---------------------------------------------------------
elif current_phase == 'auction':
    st.markdown("<div class='status-badge' style='color:#10b981; background:#064e3b;'>STAGE 2 : 실시간 경매 진행 중</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-text' style='margin-bottom: 25px;'>타 팀 프로젝트에 펀딩금과 조건부 피드백을 전달해 주세요.</div>", unsafe_allow_html=True)

    col_teams, col_feed = st.columns([2, 1])

    with col_teams:
        st.markdown("### 프로젝트 펀딩 및 피드백")
        if teams_df.empty:
            st.warning("등록된 팀이 없습니다.")
        else:
            for _, row in teams_df.iterrows():
                is_my_team = (user_team == row['name'])
                
                team_bids = bids_df[bids_df['target_team_id'] == row['id']]
                total_funding = team_bids['amount'].sum() if not team_bids.empty else 0

                card_class = "glass-card my-team-card" if is_my_team else "glass-card"
                badge = "<span class='badge-myteam'>우리 팀</span>" if is_my_team else ""

                st.markdown(f"""
                    <div class="{card_class}">
                        <div style="font-size:1.2rem; font-weight:bold; color:#f8fafc; margin-bottom:4px;">
                            {row['name']} : {row['title']} {badge}
                        </div>
                        <div style="color:#94a3b8; font-size:0.95rem; margin-bottom:12px;">{row['description']}</div>
                        <div style="font-size:0.9rem; color:#cbd5e1;">현재 누적 펀딩금</div>
                        <div class="accent-amount">{total_funding:,} 소노</div>
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
                            placeholder="이 기능이 인상적입니다 / 보완하면 좋을 점을 작성해 주세요.",
                            key=f"feedback_{row['id']}"
                        )
                        submit_bid = st.form_submit_button("펀딩 및 피드백 제출", use_container_width=True)

                        if submit_bid:
                            if not user_name or user_team == "팀 선택":
                                st.error("사이드바에서 이름과 팀을 설정해 주세요.")
                            elif bid_amount > my_balance:
                                st.error("잔액이 부족합니다.")
                            elif not feedback.strip():
                                st.error("피드백 내용을 작성해 주세요.")
                            else:
                                add_bid(user_name, user_team, row['id'], bid_amount, feedback)
                                st.success(f"{bid_amount:,} 소노 펀딩 완료!")
                                st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)

    with col_feed:
        st.markdown("### 실시간 라이브 피드")
        if bids_df.empty:
            st.info("아직 피드백 내역이 없습니다.")
        else:
            for _, bid in bids_df.sort_values(by="id", ascending=False).head(10).iterrows():
                target_team_rows = teams_df[teams_df['id'] == bid['target_team_id']]
                target_team_name = target_team_rows['name'].values[0] if not target_team_rows.empty else "팀"
                
                st.markdown(f"""
                    <div style="background:#1e293b; border:1px solid #334155; padding:12px; border-radius:8px; margin-bottom:10px;">
                        <div style="font-size:0.85rem; color:#94a3b8;">
                            <strong style="color:#f8fafc;">{bid['user_name']} ({bid['user_team']})</strong> ➔ <span style="color:#818cf8;">{target_team_name}</span>
                        </div>
                        <div style="color:#f59e0b; font-weight:bold; margin:3px 0;">{bid['amount']:,} 소노</div>
                        <div style="color:#e2e8f0; font-size:0.9rem;">"{bid['feedback']}"</div>
                    </div>
                """, unsafe_allow_html=True)

# ---------------------------------------------------------
# STAGE 3: 경매 마감 및 결과
# ---------------------------------------------------------
elif current_phase == 'finished':
    st.markdown("<div class='status-badge' style='color:#f87171; background:#451a1a;'>STAGE 3 : 경매 마감</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-text' style='margin-bottom: 25px;'>최종 경매 결과 및 팀별 피드백 수집 결과입니다.</div>", unsafe_allow_html=True)

    funding_summary = []
    for _, row in teams_df.iterrows():
        team_bids = bids_df[bids_df['target_team_id'] == row['id']]
        total_funding = team_bids['amount'].sum() if not team_bids.empty else 0
        funding_summary.append({"팀": row['name'], "주제": row['title'], "총 펀딩액": total_funding})
    
    summary_df = pd.DataFrame(funding_summary).sort_values(by="총 펀딩액", ascending=False) if funding_summary else pd.DataFrame()

    st.markdown("### 최고 펀딩 유치 팀 순위")
    
    if not summary_df.empty:
        for idx, row in summary_df.reset_index(drop=True).iterrows():
            rank = idx + 1
            badge = "1위" if rank == 1 else ("2위" if rank == 2 else f"{rank}위")
            
            st.markdown(f"""
                <div class="glass-card" style="border-left: 5px solid #818cf8;">
                    <div style="font-size:1.1rem; font-weight:bold;">{badge} : {row['팀']} - {row['주제']}</div>
                    <div class="accent-amount" style="margin-top:5px;">총 {row['총 펀딩액']:,} 소노 유치</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### 엔젤 투자자 순위")
    if not bids_df.empty:
        investor_df = bids_df.groupby(["user_name", "user_team"])["amount"].sum().reset_index()
        investor_df = investor_df.sort_values(by="amount", ascending=False)
        
        for idx, row in investor_df.reset_index(drop=True).head(3).iterrows():
            rank = idx + 1
            st.markdown(f"""
                <div style="background:#1e293b; padding:12px; border-radius:8px; margin-bottom:8px; border:1px solid #334155;">
                    <strong>{rank}위</strong> : {row['user_name']} ({row['user_team']}) — 총 <strong>{row['amount']:,} 소노</strong> 집행
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### 팀별 피드백 다운로드")
    if not bids_df.empty:
        csv_data = bids_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="전체 피드백 CSV 다운로드",
            data=csv_data,
            file_name="sonorus_auction_feedbacks.csv",
            mime="text/csv"
        )
