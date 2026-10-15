import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# ---------------------------------------------------------
# 1. 페이지 기본 설정 & 블랙/노랑 커스텀 CSS 디자인
# ---------------------------------------------------------
st.set_page_config(
    page_title="SONORUS 아이디어 경매전",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 고급스러운 검은색 배경 + 밝은 노란색 포인트 테마
st.markdown("""
    <style>
    /* 전체 배경 및 기본 폰트 색상 */
    .stApp {
        background-color: #0a0a0c !important;
        color: #f8fafc;
    }
    
    /* 사이드바 스타일 */
    section[data-testid="stSidebar"] {
        background-color: #121215 !important;
        border-right: 1px solid #27272a;
    }
    
    /* 노란색 포인트 타이틀 & 강세 */
    .yellow-title {
        color: #facc15 !important;
        font-weight: 800;
    }
    .yellow-accent {
        color: #fde047 !important;
        font-weight: bold;
    }
    
    /* 카드 디자인 */
    .custom-card {
        background-color: #18181b;
        border: 1px solid #27272a;
        padding: 20px;
        border-radius: 14px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    .my-team-card {
        border: 2px solid #facc15 !important;
        background-color: #1f1d11 !important;
    }
    
    /* 버튼 커스텀 (기본 노란색 스타일) */
    .stButton>button {
        background-color: #facc15 !important;
        color: #000000 !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #eab308 !important;
        transform: translateY(-2px);
    }
    
    /* 내 팀 태그 */
    .badge-myteam {
        background-color: #facc15;
        color: #000000;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: bold;
        float: right;
    }
    
    /* 경매 마감 및 진행 상황 알림 */
    .status-banner {
        background: linear-gradient(90deg, #18181b 0%, #27272a 100%);
        border-left: 5px solid #facc15;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SQLite 데이터베이스 (지속성 및 동시 접속 지원)
# ---------------------------------------------------------
DB_FILE = "auction_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # 동적 팀 테이블
    c.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL
        )
    ''')
    
    # 펀딩/피드백 내역 테이블
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

    # 시스템 앱 진행 상태 (phase: 'prep' -> 'auction' -> 'finished')
    c.execute('''
        CREATE TABLE IF NOT EXISTS app_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')

    # 최초 진행 상태 기본값 설정
    c.execute("SELECT COUNT(*) FROM app_state WHERE key = 'phase'")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO app_state VALUES ('phase', 'prep')")
    
    conn.commit()
    conn.close()

init_db()

# DB 조작 함수들
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
# 3. 사이드바 - 내 정보 & 관리자 로그인
# ---------------------------------------------------------
st.sidebar.markdown("<h2 class='yellow-title'>🎵 SONORUS 경매전</h2>", unsafe_allow_html=True)

# 접속자 프로필 설정
st.sidebar.subheader("👤 참가자 정보 설정")
user_name = st.sidebar.text_input("이름 입력", value=st.session_state.get("user_name", ""), placeholder="예: 홍길동")

teams_df = get_teams()
team_options = teams_df['name'].tolist() if not teams_df.empty else []

user_team = st.sidebar.selectbox("내 소속 팀 선택", options=["팀 선택"] + team_options, index=0)

if user_name and user_team != "팀 선택":
    st.session_state["user_name"] = user_name
    st.session_state["user_team"] = user_team
    st.sidebar.success(f"**{user_name}** 님 ({user_team}) 접속 완료")
else:
    st.sidebar.warning("이름과 팀을 설정해야 투자가 가능합니다.")

# 내 잔액 계산 (초기 자본: 1,000,000 소노)
INITIAL_BALANCE = 1000000
bids_df = get_bids()

if user_name:
    my_bids = bids_df[bids_df['user_name'] == user_name]
    used_amount = my_bids['amount'].sum() if not my_bids.empty else 0
    my_balance = INITIAL_BALANCE - used_amount
else:
    my_balance = INITIAL_BALANCE

st.sidebar.markdown("---")
st.sidebar.markdown(f"### 💰 내 잔여 소노")
st.sidebar.markdown(f"<h2 class='yellow-title'>{my_balance:,} 소노</h2>", unsafe_allow_html=True)
st.sidebar.caption("⚠️ 남은 소노는 마감 시 자동 소멸됩니다.")

# 관리자 모드 설정 (암호: sonorus123)
st.sidebar.markdown("---")
st.sidebar.subheader("🔒 관리자(MC) 모드")
ADMIN_PASSWORD = "sonorus123"
admin_password = st.sidebar.text_input("관리자 암호", type="password")
is_admin = (admin_password == ADMIN_PASSWORD)

current_phase = get_phase()

if is_admin:
    st.sidebar.success("관리자 권한 활성화됨")
    
    st.sidebar.markdown("**[진행 단계 관리]**")
    if current_phase == 'prep':
        if st.sidebar.button("🚀 경매 준비 완료 -> 경매 시작"):
            set_phase('auction')
            st.rerun()
    elif current_phase == 'auction':
        if st.sidebar.button("🚨 경매 마감 -> 최종 시상식"):
            set_phase('finished')
            st.rerun()
    elif current_phase == 'finished':
        if st.sidebar.button("🔄 전체 상태 초기화 (준비단계로)"):
            set_phase('prep')
            st.rerun()

# ---------------------------------------------------------
# 4. 메인 화면 - 스테이지별 전환 (단방향 제어)
# ---------------------------------------------------------
st.markdown("<h1 class='yellow-title'>🎵 소노루스 아이디어 경매전</h1>", unsafe_allow_html=True)

# ---------------------------------------------------------
# STAGE 1: 경매 준비 화면 (팀 등록 및 주제 발표 작성)
# ---------------------------------------------------------
if current_phase == 'prep':
    st.markdown("""
        <div class="status-banner">
            <h3 class="yellow-accent" style="margin:0;">📢 1단계: 경매 준비 및 팀 소개 작성 중</h3>
            <p style="margin:5px 0 0 0; color:#a1a1aa;">팀원들과 상의하여 팀 이름, 발표 주제 및 핵심 활동 내용을 작성하세요. 완료되면 관리자가 경매를 개시합니다.</p>
        </div>
    """, unsafe_allow_html=True)

    col_add, col_list = st.columns([1, 2])

    # 신규 팀 등록 폼
    with col_add:
        st.subheader("➕ 신규 팀 등록")
        with st.form(key="add_team_form"):
            new_team_name = st.text_input("팀 이름 (예: 1팀, A팀 등)", placeholder="예: 5팀")
            new_team_title = st.text_input("주제 / 프로젝트명", placeholder="예: 소노루스 웹매거진")
            new_team_desc = st.text_area("활동 내용 및 핵심 목표", placeholder="상세 활동 계획을 작성하세요.")
            add_btn = st.form_submit_button("팀 등록하기")

            if add_btn:
                if not new_team_name or not new_team_title or not new_team_desc:
                    st.error("모든 항목을 입력해야 합니다!")
                else:
                    if add_team(new_team_name, new_team_title, new_team_desc):
                        st.success(f"'{new_team_name}'이(가) 등록되었습니다!")
                        st.rerun()
                    else:
                        st.error("이미 존재하는 팀 이름입니다. 다른 이름을 사용해주세요.")

    # 등록된 팀 상세 작성 및 확인
    with col_list:
        st.subheader("📋 등록된 팀 발표 주제 목록")
        if teams_df.empty:
            st.info("아직 등록된 팀이 없습니다. 왼쪽에서 팀을 추가해주세요!")
        else:
            for _, row in teams_df.iterrows():
                is_my_team = (user_team == row['name'])
                
                with st.expander(f"📌 {row['name']} : {row['title']}", expanded=True):
                    if is_admin or is_my_team:
                        st.caption("✍️ 내용 수정하기")
                        edit_title = st.text_input(f"주제 ({row['name']})", value=row['title'], key=f"title_{row['id']}")
                        edit_desc = st.text_area(f"설명 ({row['name']})", value=row['description'], key=f"desc_{row['id']}")
                        if st.button(f"{row['name']} 저장", key=f"btn_{row['id']}"):
                            update_team_info(row['id'], edit_title, edit_desc)
                            st.success("수정사항이 저장되었습니다!")
                            st.rerun()
                    else:
                        st.markdown(f"### {row['title']}")
                        st.write(row['description'])

    st.markdown("---")
    if is_admin:
        if st.button("🚀 모든 팀 준비 완료! 경매 화면으로 넘어가기 (이후 준비화면 복귀 불가)", use_container_width=True):
            set_phase('auction')
            st.rerun()

# ---------------------------------------------------------
# STAGE 2: 실시간 경매 진행 화면 (준비 화면 복귀 불가!)
# ---------------------------------------------------------
elif current_phase == 'auction':
    st.markdown("""
        <div class="status-banner">
            <h3 class="yellow-accent" style="margin:0;">🔨 2단계: 아이디어 경매전 라이브 진행 중!</h3>
            <p style="margin:5px 0 0 0; color:#a1a1aa;">다른 팀의 주제를 확인하고 펀딩금과 조건부 피드백을 남겨주세요. (자기 팀 투자 불가)</p>
        </div>
    """, unsafe_allow_html=True)

    col_teams, col_feed = st.columns([2, 1])

    with col_teams:
        st.subheader("🔨 팀별 펀딩 및 피드백 제출")
        if teams_df.empty:
            st.warning("등록된 팀이 없습니다.")
        else:
            for _, row in teams_df.iterrows():
                is_my_team = (user_team == row['name'])
                
                # 누적 펀딩액 계산
                team_bids = bids_df[bids_df['target_team_id'] == row['id']]
                total_funding = team_bids['amount'].sum() if not team_bids.empty else 0

                card_class = "custom-card my-team-card" if is_my_team else "custom-card"
                badge = "<span class='badge-myteam'>우리 팀 (투자 불가)</span>" if is_my_team else ""

                st.markdown(f"""
                    <div class="{card_class}">
                        <h3 style="margin:0;">{row['name']} - {row['title']} {badge}</h3>
                        <p style="color:#a1a1aa; margin:10px 0;">{row['description']}</p>
                        <h4 class="yellow-title" style="margin:0;">현재 누적 펀딩액: {total_funding:,} 소노</h4>
                    </div>
                """, unsafe_allow_html=True)

                if is_my_team:
                    st.info("💡 자기 팀에는 투자할 수 없습니다. 타 팀원들의 피드백을 기다려보세요!")
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
                            "조건부 피드백 / 투자 이유 (필수 작성)",
                            placeholder="이 기능이 인상적이어서 투자합니다 / ~한 점을 더 보완하면 대박날 것 같습니다.",
                            key=f"feedback_{row['id']}"
                        )
                        submit_bid = st.form_submit_button("💰 펀딩 & 피드백 제출하기")

                        if submit_bid:
                            if not user_name or user_team == "팀 선택":
                                st.error("사이드바에서 이름과 팀을 먼저 설정해 주세요!")
                            elif bid_amount > my_balance:
                                st.error("보유한 소노 잔액보다 큰 금액은 투자할 수 없습니다!")
                            elif not feedback.strip():
                                st.error("피드백/투자 조건을 필수 입력해야 합니다!")
                            else:
                                add_bid(user_name, user_team, row['id'], bid_amount, feedback)
                                st.success(f"성공적으로 {bid_amount:,} 소노를 펀딩했습니다!")
                                st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)

    with col_feed:
        st.subheader("⚡ 실시간 라이브 피드백")
        if bids_df.empty:
            st.info("아직 제출된 피드백이 없습니다. 첫 투자를 시작해보세요!")
        else:
            for _, bid in bids_df.sort_values(by="id", ascending=False).head(12).iterrows():
                target_team_rows = teams_df[teams_df['id'] == bid['target_team_id']]
                target_team_name = target_team_rows['name'].values[0] if not target_team_rows.empty else "팀"
                
                st.markdown(f"""
                    <div style="background:#18181b; border:1px solid #27272a; padding:12px; border-radius:10px; margin-bottom:10px;">
                        <strong>{bid['user_name']} ({bid['user_team']})</strong> ➡️ <span style="color:#facc15;">{target_team_name}</span><br>
                        <span class="yellow-accent">{bid['amount']:,} 소노</span><br>
                        <span style="color:#d4d4d8; font-size:0.95rem;">"{bid['feedback']}"</span>
                    </div>
                """, unsafe_allow_html=True)

# ---------------------------------------------------------
# STAGE 3: 최종 경매 마감 & 시상식 리포트 화면
# ---------------------------------------------------------
elif current_phase == 'finished':
    st.markdown("""
        <div class="status-banner" style="border-left-color: #ef4444;">
            <h3 style="color:#ef4444; margin:0;">🏆 3단계: 경매 마감 및 최종 결과 발표</h3>
            <p style="margin:5px 0 0 0; color:#a1a1aa;">모든 경매가 마감되었습니다! 각 부문별 수상 팀과 참가자를 확인하세요.</p>
        </div>
    """, unsafe_allow_html=True)

    # 1. 팀별 총 펀딩 순위 계산 (유니콘상)
    funding_summary = []
    for _, row in teams_df.iterrows():
        team_bids = bids_df[bids_df['target_team_id'] == row['id']]
        total_funding = team_bids['amount'].sum() if not team_bids.empty else 0
        funding_summary.append({"팀": row['name'], "주제": row['title'], "총 펀딩액": total_funding})
    
    summary_df = pd.DataFrame(funding_summary).sort_values(by="총 펀딩액", ascending=False) if funding_summary else pd.DataFrame()

    st.subheader("🦄 대박 유니콘상 (최고 펀딩 모금 팀)")
    
    if not summary_df.empty:
        for idx, row in summary_df.reset_index(drop=True).iterrows():
            rank = idx + 1
            badge = "🥇 1위" if rank == 1 else ("🥈 2위" if rank == 2 else ("🥉 3위" if rank == 3 else f"{rank}위"))
            
            st.markdown(f"""
                <div class="custom-card" style="border-left: 6px solid #facc15;">
                    <h3 style="margin:0;">{badge} : {row['팀']} - {row['주제']}</h3>
                    <h2 class="yellow-title" style="margin:8px 0 0 0;">총 {row['총 펀딩액']:,} 소노 유치</h2>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # 2. 개인별 투자 집행 순위 (엔젤 투자자상)
    st.subheader("💎 최고 엔젤 투자자상 (가장 적극적으로 피드백을 전달한 참가자)")
    if not bids_df.empty:
        investor_df = bids_df.groupby(["user_name", "user_team"])["amount"].sum().reset_index()
        investor_df = investor_df.sort_values(by="amount", ascending=False)
        
        for idx, row in investor_df.reset_index(drop=True).head(3).iterrows():
            rank = idx + 1
            st.markdown(f"""
                <div style="background:#18181b; padding:12px; border-radius:8px; margin-bottom:8px; border:1px solid #27272a;">
                    <strong class="yellow-accent">{rank}위</strong> : {row['user_name']} 님 ({row['user_team']}) — 총 <strong>{row['amount']:,} 소노</strong> 투자 완료
                </div>
            """, unsafe_allow_html=True)
    else:
        st.write("투자 내역이 없습니다.")

    st.markdown("---")

    # 3. CSV 결과 다운로드
    st.subheader("📥 팀별 수집 피드백 전체 리포트 다운로드")
    if not bids_df.empty:
        csv_data = bids_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📄 전체 피드백 CSV 파일 다운로드",
            data=csv_data,
            file_name="sonorus_auction_feedbacks.csv",
            mime="text/csv"
        )
