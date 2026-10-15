import streamlit as st
import pandas as pd
import json
import os
import sqlite3
from datetime import datetime

# ---------------------------------------------------------
# 1. 페이지 기본 설정 & CSS 스타일
# ---------------------------------------------------------
st.set_page_config(
    page_title="SONORUS 아이디어 경매전",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 다크 모드 기반 커스텀 스타일
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .funding-card {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #334155;
        margin-bottom: 15px;
    }
    .my-team-card {
        border: 2px solid #f59e0b !important;
    }
    .highlight-text { color: #818cf8; font-weight: bold; }
    .badge-myteam {
        background-color: #f59e0b;
        color: #000;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SQLite 데이터베이스 (동시 접속 및 지속 데이터 관리)
# ---------------------------------------------------------
DB_FILE = "auction_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # 팀 테이블
    c.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
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
            target_team_id TEXT NOT NULL,
            amount INTEGER NOT NULL,
            feedback TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')

    # 시스템 상태 테이블 (경매 마감 여부)
    c.execute('''
        CREATE TABLE IF NOT EXISTS app_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')

    # 기본 팀 데이터 초기 삽입 (없을 경우)
    c.execute("SELECT COUNT(*) FROM teams")
    if c.fetchone()[0] == 0:
        default_teams = [
            ("team1", "1팀", "음악 취향 매칭 앱", "음악 취향 기반 실시간 소모임 매칭 및 플레이리스트 공유 서비스입니다."),
            ("team2", "2팀", "웹 인터랙티브 악기", "웹 오디오 API를 활용하여 브라우저에서 직접 연주하는 시각화 악기 페이지입니다."),
            ("team3", "3팀", "AI 화성학 튜터", "작곡 초보자를 위해 어울리는 코드를 자동으로 추천해주는 AI 사운드 툴입니다."),
            ("team4", "4팀", "소노루스 브랜드 굿즈", "동아리 아이덴티티를 담은 키링, 스티커 및 브랜드 웹 매거진 제작 프로젝트입니다.")
        ]
        c.executemany("INSERT INTO teams VALUES (?, ?, ?, ?)", default_teams)
        c.execute("INSERT INTO app_state VALUES ('is_finished', 'false')")
    
    conn.commit()
    conn.close()

init_db()

# DB 헬퍼 함수들
def get_teams():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM teams", conn)
    conn.close()
    return df

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

def update_team_info(team_id, title, description):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE teams SET title = ?, description = ? WHERE id = ?", (title, description, team_id))
    conn.commit()
    conn.close()

def get_auction_status():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT value FROM app_state WHERE key = 'is_finished'")
    row = c.fetchone()
    conn.close()
    return row[0] == 'true' if row else False

def set_auction_status(is_finished):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    val = 'true' if is_finished else 'false'
    c.execute("REPLACE INTO app_state (key, value) VALUES ('is_finished', ?)", (val,))
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# 3. 사이드바 - 내 프로필 & 관리자 로그인
# ---------------------------------------------------------
st.sidebar.title("🎵 SONORUS 경매전")

# 접속자 프로필 설정
st.sidebar.subheader("👤 참가자 정보")
user_name = st.sidebar.text_input("이름 입력", value=st.session_state.get("user_name", ""), placeholder="예: 홍길동")
teams_df = get_teams()
team_options = teams_df['name'].tolist()
user_team = st.sidebar.selectbox("내 소속 팀 선택", options=["팀 선택"] + team_options, index=0)

if user_name and user_team != "팀 선택":
    st.session_state["user_name"] = user_name
    st.session_state["user_team"] = user_team
    st.sidebar.success(f"**{user_name}** 님 ({user_team}) 접속 완료")
else:
    st.sidebar.warning("이름과 팀을 선택해야 투자가 가능합니다.")

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
st.sidebar.metric("💰 내 잔여 소노", f"{my_balance:,} 소노")
st.sidebar.caption("⚠️ 남은 소노는 경매 마감 시 자동 소멸됩니다.")

# 관리자 모드
st.sidebar.markdown("---")
st.sidebar.subheader("🔒 관리자(MC) 모드")
admin_password = st.sidebar.text_input("관리자 암호", type="password")
is_admin = (admin_password == "sonorus123") # 기본 암호: sonorus123

if is_admin:
    st.sidebar.success("관리자 권한 활성화됨")
    if st.sidebar.button("🚨 경매 마감 처리 / 리셋"):
        current_status = get_auction_status()
        set_auction_status(not current_status)
        st.rerun()

# ---------------------------------------------------------
# 4. 메인 화면 - 탭 구성
# ---------------------------------------------------------
st.title("🎵 소노루스 아이디어 경매전")

tab1, tab2, tab3 = st.tabs(["📢 1. 팀별 소개/준비", "🔨 2. 실시간 아이디어 경매", "🏆 3. 최종 시상식 & 결과"])

is_finished = get_auction_status()

# ---------------------------------------------------------
# TAB 1: 팀별 소개 및 준비 화면
# ---------------------------------------------------------
with tab1:
    st.header("📢 각 팀별 프로젝트 소개 및 내용")
    st.write("차시 결과물에 대한 각 팀의 발표 내용과 핵심 아이디어를 확인하세요.")

    for _, row in teams_df.iterrows():
        is_my_team = (user_team == row['name'])
        
        with st.expander(f"📌 {row['name']} : {row['title']}", expanded=True):
            if is_admin or (is_my_team and not is_finished):
                st.caption("✍️ 우리 팀 발표 내용 수정하기")
                new_title = st.text_input(f"주제 제목 ({row['name']})", value=row['title'], key=f"t_title_{row['id']}")
                new_desc = st.text_area(f"상세 설명 및 목표 ({row['name']})", value=row['description'], key=f"t_desc_{row['id']}")
                if st.button(f"{row['name']} 내용 저장", key=f"save_{row['id']}"):
                    update_team_info(row['id'], new_title, new_desc)
                    st.success("내용이 저장되었습니다!")
                    st.rerun()
            else:
                st.subheader(row['title'])
                st.write(row['description'])

# ---------------------------------------------------------
# TAB 2: 실시간 아이디어 경매 화면
# ---------------------------------------------------------
with tab2:
    if is_finished:
        st.error("🚨 현재 경매가 마감되었습니다! '3. 최종 시상식 & 결과' 탭에서 승자를 확인하세요.")
    else:
        st.header("🔨 아이디어 펀딩 및 피드백 제출")
        st.write("다른 팀의 아이디어에 펀딩을 진행하고, **필수 피드백/조건**을 남겨주세요.")

        col_left, col_right = st.columns([2, 1])

        with col_left:
            for _, row in teams_df.iterrows():
                is_my_team = (user_team == row['name'])
                
                # 누적 펀딩액 계산
                team_bids = bids_df[bids_df['target_team_id'] == row['id']]
                total_funding = team_bids['amount'].sum() if not team_bids.empty else 0

                card_class = "funding-card my-team-card" if is_my_team else "funding-card"
                badge_html = f"<span class='badge-myteam'>우리 팀 (투자 불가)</span>" if is_my_team else ""

                st.markdown(f"""
                    <div class="{card_class}">
                        <h3>{row['name']} - {row['title']} {badge_html}</h3>
                        <p style="color:#cbd5e1;">{row['description']}</p>
                        <h4 style="color:#f59e0b;">현재 누적 펀딩액: {total_funding:,} 소노</h4>
                    </div>
                """, unsafe_allow_html=True)

                if is_my_team:
                    st.info("💡 자기 팀에는 투자할 수 없습니다. 타 팀의 펀딩을 기다려주세요!")
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
                            "조건부 피드백 / 투자 이유 (필수)",
                            placeholder="이 기능이 매력적이어서 투자합니다 / ~한 점을 보완해 주면 좋겠습니다.",
                            key=f"feedback_{row['id']}"
                        )
                        submit_btn = st.form_submit_button("💰 펀딩 및 피드백 제출")

                        if submit_btn:
                            if not user_name or user_team == "팀 선택":
                                st.error("사이드바에서 이름과 팀을 먼저 설정해주세요!")
                            elif bid_amount > my_balance:
                                st.error("보유한 잔액보다 큰 금액은 투자할 수 없습니다.")
                            elif not feedback.strip():
                                st.error("투자 조건 및 피드백을 반드시 작성해야 합니다!")
                            else:
                                add_bid(user_name, user_team, row['id'], bid_amount, feedback)
                                st.success(f"{row['name']}에 {bid_amount:,} 소노 투자 완료!")
                                st.rerun()

                st.markdown("---")

        with col_right:
            st.subheader("⚡ 실시간 피드백 라이브 피드")
            if bids_df.empty:
                st.write("아직 제출된 펀딩 피드백이 없습니다.")
            else:
                for _, bid in bids_df.sort_values(by="id", ascending=False).head(10).iterrows():
                    target_team_name = teams_df[teams_df['id'] == bid['target_team_id']]['name'].values[0]
                    st.markdown(f"""
                        <div style="background:#1e293b; padding:10px; border-radius:8px; margin-bottom:8px; font-size:0.9rem;">
                            <strong>{bid['user_name']} ({bid['user_team']})</strong> ➡️ <span style="color:#38bdf8;">{target_team_name}</span><br>
                            <span style="color:#f59e0b; font-weight:bold;">{bid['amount']:,} 소노</span><br>
                            <span style="color:#e2e8f0;">"{bid['feedback']}"</span>
                        </div>
                    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 3: 최종 시상식 및 리포트 결과
# ---------------------------------------------------------
with tab3:
    st.header("🏆 경매 최종 시상식 & 피드백 리포트")

    if not is_finished and not is_admin:
        st.info("경매가 마감된 후 최종 결과가 공개됩니다. (관리자가 마감 처리 예정)")
    else:
        # 1. 팀별 총 펀딩 순위 계산
        funding_summary = []
        for _, row in teams_df.iterrows():
            team_bids = bids_df[bids_df['target_team_id'] == row['id']]
            total_funding = team_bids['amount'].sum() if not team_bids.empty else 0
            funding_summary.append({"팀": row['name'], "주제": row['title'], "총 펀딩액": total_funding})
        
        summary_df = pd.DataFrame(funding_summary).sort_values(by="총 펀딩액", ascending=False)

        st.subheader("🦄 대박 유니콘상 (최고 펀딩 모금 팀)")
        
        for idx, row in summary_df.reset_index(drop=True).iterrows():
            rank = idx + 1
            badge = "🥇 1위" if rank == 1 else ("🥈 2위" if rank == 2 else ("🥉 3위" if rank == 3 else f"{rank}위"))
            st.markdown(f"""
                <div style="background:#1e293b; padding:15px; border-radius:10px; margin-bottom:10px; border-left: 5px solid #f59e0b;">
                    <h4 style="margin:0;">{badge} : {row['팀']} - {row['주제']}</h4>
                    <h3 style="color:#f59e0b; margin:5px 0 0 0;">총 {row['총 펀딩액']:,} 소노 유치</h3>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # 2. 개인별 투자액 순위 (엔젤 투자자상)
        st.subheader("💎 최고 엔젤 투자자상 (가장 적극적으로 피드백을 남긴 참가자)")
        if not bids_df.empty:
            investor_df = bids_df.groupby(["user_name", "user_team"])["amount"].sum().reset_index()
            investor_df = investor_df.sort_values(by="amount", ascending=False)
            
            for idx, row in investor_df.reset_index(drop=True).head(3).iterrows():
                rank = idx + 1
                st.write(f"**{rank}위**: {row['user_name']} ({row['user_team']}) - 총 **{row['amount']:,} 소노** 투자 완료")
        else:
            st.write("투자 내역이 없습니다.")

        st.markdown("---")

        # 3. 전체 피드백 리포트 다운로드
        st.subheader("📥 팀별 피드백 전체 내역 다운로드")
        if not bids_df.empty:
            csv_data = bids_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📄 전체 피드백 CSV 리포트 다운로드",
                data=csv_data,
                file_name="sonorus_auction_feedbacks.csv",
                mime="text/csv"
            )
