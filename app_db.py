import streamlit as st
import sqlite3
from datetime import date, datetime, timedelta
import plotly.express as px
import calendar
import bcrypt

# =====================
# DB
# =====================
@st.cache_resource
def get_cursor():
    conn = sqlite3.connect("study.db", check_same_thread=False)
    return conn, conn.cursor()

conn, c = get_cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS study (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    subject TEXT,
    minutes INTEGER,
    username TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    subject TEXT,
    goal_minutes INTEGER,
    UNIQUE(username, subject)
)
""")

conn.commit()

# =====================
# session
# =====================
if "user" not in st.session_state:
    st.session_state.user = None

# =====================
# auth
# =====================
def register_user(username, password):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        c.execute(
            "INSERT INTO users VALUES (NULL, ?, ?)",
            (username, hashed.decode())
        )
        conn.commit()
        return True
    except:
        return False


def login_user(username, password):
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    result = c.fetchone()

    if not result:
        return False

    return bcrypt.checkpw(password.encode(), result[0].encode())


# =====================
# login
# =====================
if not st.session_state.user:

    st.title("🔐 ログイン")

    tab1, tab2 = st.tabs(["ログイン", "登録"])

    with tab1:
        u = st.text_input("ユーザー名", key="login_user")
        p = st.text_input("パスワード", type="password", key="login_pass")

        if st.button("ログイン"):
            if login_user(u, p):
                st.session_state.user = u
                st.rerun()
            else:
                st.error("失敗")

    with tab2:
        nu = st.text_input("新規ユーザー", key="reg_user")
        np = st.text_input("パスワード", type="password", key="reg_pass")

        if st.button("登録"):
            if register_user(nu, np):
                st.success("OK")
            else:
                st.error("NG")

    st.stop()


# =====================
# data
# =====================
rows = c.execute(
    "SELECT date, subject, minutes FROM study WHERE username=?",
    (st.session_state.user,)
).fetchall()

study_days = set()
daily_totals = {}
monthly_subjects = {}
weekly_total = 0
monthly_total = 0

now = date.today()

for day, subject, minutes in rows:
    d = datetime.strptime(day, "%Y-%m-%d").date()
    study_days.add(d)

    daily_totals[day] = daily_totals.get(day, 0) + minutes

    if now - timedelta(days=6) <= d:
        weekly_total += minutes

    if d.month == now.month and d.year == now.year:
        monthly_total += minutes
        monthly_subjects[subject] = monthly_subjects.get(subject, 0) + minutes


# =====================
# streak
# =====================
streak = 0
best_streak = 0

if study_days:
    sorted_days = sorted(study_days)
    current = 1
    best_streak = 1

    for i in range(1, len(sorted_days)):
        if (sorted_days[i] - sorted_days[i-1]).days == 1:
            current += 1
        else:
            current = 1
        best_streak = max(best_streak, current)

    today_check = date.today()
    while today_check in study_days:
        streak += 1
        today_check -= timedelta(days=1)


# =====================
# next target
# =====================
targets = [7, 14, 30, 100]
next_target = next((t for t in targets if streak < t), None)

if next_target:
    remain_days = next_target - streak
    streak_progress = streak / next_target
else:
    remain_days = 0
    streak_progress = 1.0


# =====================
# menu
# =====================
st.sidebar.title("📚 メニュー")

menu = st.sidebar.radio(
    "移動",
    ["ダッシュボード", "記録追加", "ランキング", "記録削除", "記録編集", "目標設定"]
)

st.sidebar.write(st.session_state.user)

if st.sidebar.button("ログアウト"):
    st.session_state.user = None
    st.rerun()


# =====================
# DASHBOARD
# =====================
if menu == "ダッシュボード":

    st.title("📊 ダッシュボード")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("今週", f"{weekly_total}分")
    col2.metric("今月", f"{monthly_total}分")
    col3.metric("合計", f"{sum(monthly_subjects.values())}分")
    col4.metric("🔥 連続", f"{streak}日")
    # =====================
    # 🎯 今日のミッション
    # =====================
    mission_exp = 0
    exp = sum(monthly_subjects.values()) + mission_exp

    
    st.subheader("🎯 今日のミッション")
    
    today_minutes = daily_totals.get(date.today().isoformat(), 0)

    if today_minutes == 0:
        mission_exp = 0
        st.info("📚 まずは10分やろう！")
    elif today_minutes < 60:
        mission_exp = today_minutes // 10 * 5
        st.warning(f"🔥 あと {60 - today_minutes} 分で1時間！")
    else:
        mission_exp = 50
        st.success("🎉 いい感じ！")

    
    
    # =====================
    # 🔥 ストリークエリア
    #=====================
    st.subheader("🔥 ストリーク")

    st.metric("現在", f"{streak}日連続")
    st.write(f"🏆 最長 {best_streak}日")

    # 次の目標
    targets = [7, 14, 30, 100]
    next_target = next((t for t in targets if streak < t), None)

    if next_target:
        remain_days = next_target - streak
        streak_progress = streak / next_target

        st.subheader("🏅 ストリーク目標")
        st.write(f"次の目標：**{next_target}日連続**")
        st.write(f"あと **{remain_days}日** で達成！🔥")
        st.progress(streak_progress)

    else:
        st.success("🎉 すべてのストリーク目標を達成済み！")


    # =====================
    # 🏅 実績バッジ
    # =====================
    st.subheader("🏅 実績バッジ")

    if best_streak >= 7:
        st.success("🥇 7日連続達成バッジ")
        st.balloons()

    if best_streak >= 14:
        st.success("🥈 14日連続達成バッジ")

    if best_streak >= 30:
        st.success("🥉 30日連続達成バッジ")

    if best_streak >= 100:
        st.success("👑 100日達成マスター")


    # =====================
    # ⚠️ ストリーク警告
    # =====================
    st.subheader("⚠️ ストリーク状況")

    today = date.today()
    yesterday = today - timedelta(days=1)
    two_days_ago = today - timedelta(days=2)

    if today not in study_days:
        
        if yesterday in study_days:
            st.warning("⚠️ 今日やらないとストリークが切れます！")
            
        elif two_days_ago in study_days:
            st.error("🚨 危険！明日でストリーク終了")

        else:
            st.info("📚 今日はまだ勉強していません")


    # =====================
    # 🐣 学習キャラ
    # =====================
    st.subheader("🐣 学習キャラ")

    if best_streak < 3:
        st.write("🥚 卵（準備中）")

    elif best_streak < 7:
        st.write("🐣 ひよこ")

    elif best_streak < 14:
        st.write("🐤 小鳥")

    elif best_streak < 30:
        st.write("🦉 賢者")

    else:
        st.write("🐉 伝説ドラゴン🔥")


    # =====================
    # 🎉 達成演出
    # =====================
    if best_streak == 7:
        st.success("🎉 7日達成！")
        st.balloons()

    elif best_streak == 14:
        st.success("🔥 14日達成！")
        st.snow()

    elif best_streak == 30:
        st.success("🏆 30日達成！")
        st.balloons()

    elif best_streak == 100:
        st.success("👑 100日達成！")
        st.snow()


    # 🏅 レベルシステム
    mission_exp = 0
    exp = sum(monthly_subjects.values()) + mission_exp

    level = exp // 300 + 1
    remain = (level * 300) - exp
    progress = (exp % 300) / 300

    st.subheader("🏅 レベル")
    st.metric("現在レベル", f"Lv.{level}")

    if level < 5:
        title = "🥉 Beginner"
    elif level < 10:
        title = "🥈 Bronze"
    elif level < 20:
        title = "🥇 Silver"
    elif level < 40:
        title = "💎 Gold"
    else:title = "👑 Master"

    st.write(title)
    st.progress(progress)

    st.write(f"次のレベルまで **あと {remain} 分**")
    

# =====================
# ADD
# =====================
elif menu == "記録追加":
    st.title("✏️ 追加")

    s = st.text_input("科目")
    m = st.number_input("分", min_value=1)

    if st.button("追加"):
        c.execute(
            "INSERT INTO study VALUES (NULL, ?, ?, ?, ?)",
            (str(date.today()), s, m, st.session_state.user)
        )
        conn.commit()
        st.rerun()


# =====================
# ranking
# =====================
elif menu == "ランキング":

    st.title("🏆 ランキング")

    ranking = sorted(monthly_subjects.items(), key=lambda x: x[1], reverse=True)

    for i, (s, m) in enumerate(ranking, 1):
        st.write(i, s, m)


# =====================
# delete
# =====================
elif menu == "記録削除":

    st.title("🗑️ 削除")

    records = c.execute(
        "SELECT id, date, subject, minutes FROM study WHERE username=?",
        (st.session_state.user,)
    ).fetchall()

    options = {f"{d}|{s}|{m}": rid for rid, d, s, m in records}

    sel = st.selectbox("削除", list(options.keys()))

    if st.button("削除"):
        c.execute("DELETE FROM study WHERE id=?", (options[sel],))
        conn.commit()
        st.rerun()


# =====================
# edit
# =====================
elif menu == "記録編集":

    st.title("✏️ 編集")
    st.info("簡略版（必要なら拡張できる）")


# =====================
# goal
# =====================
elif menu == "目標設定":

    st.title("🎯 目標")

    subject = st.text_input("科目")
    goal = st.number_input("分", min_value=1)

    if st.button("保存"):
         c.execute("""
            INSERT INTO goals (username, subject, goal_minutes)
            VALUES (?, ?, ?)
            ON CONFLICT(username, subject)
            DO UPDATE SET goal_minutes=excluded.goal_minutes
         """, (st.session_state.user, subject, goal))
         
         
         conn.commit()
         st.success("OK")