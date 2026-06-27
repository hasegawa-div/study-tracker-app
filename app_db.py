import streamlit as st
import sqlite3
from datetime import date, datetime, timedelta
import plotly.express as px
import calendar
import bcrypt
# =====================
# DB
# =====================
conn = sqlite3.connect("study.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS study (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    subject TEXT,
    minutes INTEGER,
    username TEXT
)
""")
conn.commit()
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")
conn.commit()
c.execute("""
CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    subject TEXT,
    goal_minutes INTEGER
)
""")
conn.commit()
# =====================
# session
# =====================
if "user" not in st.session_state:
    st.session_state.user = None
def register_user(username, password):

    hashed = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    )

    try:
        c.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed.decode())
        )

        conn.commit()
        return True

    except:
        return False
def login_user(username, password):

    c.execute(
        "SELECT password FROM users WHERE username=?",
        (username,)
    )

    result = c.fetchone()

    if result is None:
        return False

    stored_hash = result[0]

    return bcrypt.checkpw(
        password.encode(),
        stored_hash.encode()
    )


# =====================
# login check
# =====================
if not st.session_state.user:

    st.title("🔐 勉強管理アプリ ログイン")

    tab1, tab2 = st.tabs(["ログイン", "新規登録"])

    # ログイン
    with tab1:
        username = st.text_input("ユーザー名", key="login_user")
        password = st.text_input("パスワード", type="password", key="login_pass")

        if st.button("ログイン"):
            user = login_user(username, password)

            if user:
                st.session_state.user = username
                st.success("ログイン成功！")
                st.rerun()
            else:
                st.error("ユーザー名またはパスワードが違います")

    # 新規登録
    with tab2:
        new_user = st.text_input("新しいユーザー名", key="reg_user")
        new_pass = st.text_input("パスワード", type="password", key="reg_pass")

        if st.button("登録"):
            if register_user(new_user, new_pass):
                st.success("登録成功！ログインしてください")
            else:
                st.error("そのユーザー名は使えません")

    st.stop()

# =====================
# data
# =====================
rows = c.execute(
    "SELECT date, subject, minutes FROM study WHERE username=?",
    (st.session_state.user,)
).fetchall()

weekly_total = 0
monthly_total = 0
monthly_subjects = {}
study_days = set()
daily_totals = {}

now = date.today()

for day, subject, minutes in rows:
    d = datetime.strptime(day, "%Y-%m-%d").date()
    minutes = int(minutes)

    study_days.add(d)
    daily_totals[day] = (
        daily_totals.get(day, 0)
        + minutes
    )

    if now - timedelta(days=6) <= d:
        weekly_total += minutes

    if d.year == now.year and d.month == now.month:
        monthly_total += minutes
        monthly_subjects[subject] = monthly_subjects.get(subject, 0) + minutes
streak = 0
best_streak = 0

if study_days:

    sorted_days = sorted(study_days)

    current = 1
    best_streak = 1

    for i in range(1, len(sorted_days)):

        diff = (sorted_days[i] - sorted_days[i - 1]).days

        if diff == 1:
            current += 1
        else:
            current = 1

        best_streak = max(best_streak, current)

    today_check = date.today()

    while today_check in study_days:
        streak += 1
        today_check -= timedelta(days=1)
# =====================
# sidebar
# =====================
st.sidebar.title("📚 メニュー")

menu = st.sidebar.radio(
    "移動",
    ["ダッシュボード", "記録追加", "ランキング", "記録削除", "記録編集", "目標設定"]
)
st.sidebar.divider()

if st.sidebar.button("🚪 ログアウト"):
    st.session_state.user = None
    st.rerun()
# =====================
# dashboard
# =====================
if menu == "ダッシュボード":

    st.title("📊 ダッシュボード")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("今週", f"{weekly_total}分")
    col2.metric("今月", f"{monthly_total}分")
    col3.metric("合計", f"{sum(monthly_subjects.values())}分")
    col4.metric("🔥 連続",f"{streak}日")
    st.subheader("🎯 試験日カウントダウン")

    exam_date = st.date_input(
        "試験日",
        value=date.today()
    )

    days_left = (exam_date - date.today()).days

    st.metric(
        "試験まで",
        f"あと {days_left} 日"
    )
    if monthly_subjects:
        subjects = list(monthly_subjects.keys())
        minutes = list(monthly_subjects.values())

        fig = px.bar(x=subjects, y=minutes)
        st.plotly_chart(fig, use_container_width=True)
        st.subheader("🔥 学習継続状況")

        cal = calendar.monthcalendar(now.year, now.month)

        text = ""

        for week in cal:
            for d in week:
                if d == 0:
                    text += "⬜ "
                elif d in {
                    day.day
                    for day in study_days
                    if day.month == now.month
                    }:
                    text += "🟩 "

                else:
                    text += "⬛ "

            text += "\n"

        st.code(text)
        st.subheader("🏆 実績")

        total_minutes = sum(monthly_subjects.values())

        if len(study_days) >= 1:
            st.success("🥉 初記録達成")

        if total_minutes >= 600:
            st.success("🥈 合計10時間達成")

        if len(study_days) >= 7:
            st.success("🥇 7日以上勉強")

        if total_minutes >= 6000:
            st.success("👑 合計100時間達成")
        st.subheader("📈 勉強時間推移")
        days = sorted(daily_totals.keys())

        times = [
            daily_totals[d]
            for d in days
            ]
        

        if days:

         fig_line = px.line(
         x=days,
         y=times,
         markers=True,
         labels={
             "x": "日付",
             "y": "勉強時間(分)"
             })

        st.plotly_chart(
            fig_line,
            use_container_width=True
            )
        st.metric("🏆 最長連続記録",f"{best_streak}日")
        st.subheader("🎯 目標達成率")

        goals = c.execute(
            """SELECT subject, goal_minutes
            FROM goals
            WHERE username=?
            """,
            (st.session_state.user,)
        ).fetchall()

        for subject, goal in goals:
            studied = monthly_subjects.get(subject, 0)

            progress = min(studied / goal, 1.0)
    
        st.write(f"{subject} : {studied}/{goal}分")

        st.progress(progress)
    
# =====================
# add
# =====================
elif menu == "記録追加":

    st.title("✏️ 記録追加")

    subject = st.text_input("科目")
    minutes = st.number_input("時間", min_value=1)

    if st.button("追加"):
        c.execute(
            "INSERT INTO study(date, subject, minutes, username) VALUES (?, ?, ?, ?)",
            (str(date.today()), subject, minutes, st.session_state.user)
        )
        conn.commit()
        st.success("追加しました")
        st.rerun()

# =====================
# ranking
# =====================
elif menu == "ランキング":

    st.title("🏆 ランキング")

    ranking = sorted(
        monthly_subjects.items(),
        key=lambda x: x[1],
        reverse=True
    )

    for i, (s, t) in enumerate(ranking, 1):
        st.write(f"{i}位 {s}：{t}分")
# =====================
# delete
# =====================
elif menu == "記録削除":

    st.title("🗑️ 記録削除")

    records = c.execute(
        """
        SELECT id, date, subject, minutes
        FROM study
        WHERE username=?
        ORDER BY date DESC
        """,
        (st.session_state.user,)
    ).fetchall()

    if not records:
        st.info("削除できる記録がありません")

    else:

        options = {
            f"{day} | {subject} | {minutes}分": record_id
            for record_id, day, subject, minutes in records
        }

        selected = st.selectbox(
            "削除する記録を選択",
            list(options.keys())
        )

        if st.checkbox("本当に削除する", key="confirm_delete"):

            if st.button("🗑️ 削除"):

                c.execute(
                    "DELETE FROM study WHERE id=?",
                    (options[selected],)
                )

                conn.commit()

                st.success("削除しました")
                st.rerun()
# =====================
# compile
# =====================
elif menu == "記録編集":

    st.title("✏️ 記録編集")

    records = c.execute(
        """
        SELECT id, date, subject, minutes
        FROM study
        WHERE username=?
        ORDER BY date DESC
        """,
        (st.session_state.user,)
    ).fetchall()

    if not records:
        st.info("編集できる記録がありません")

    else:

        options = {
            f"{day} | {subject} | {minutes}分": record_id
            for record_id, day, subject, minutes in records
        }

        selected = st.selectbox(
            "編集する記録",
            list(options.keys())
        )

        record_id = options[selected]

        current = next(
            r for r in records if r[0] == record_id
        )

        new_subject = st.text_input(
            "科目",
            value=current[2]
        )

        new_minutes = st.number_input(
            "時間",
            min_value=1,
            value=current[3]
        )

        if st.button("💾 保存"):

            c.execute(
                """
                UPDATE study
                SET subject=?,
                    minutes=?
                WHERE id=?
                """,
                (
                    new_subject,
                    new_minutes,
                    record_id
                )
            )

            conn.commit()

            st.success("更新しました")
            st.rerun()
# =====================
# target setting
# =====================
elif menu == "目標設定":

    st.title("🎯 目標設定")

    subject = st.text_input("科目")
    goal = st.number_input(
        "目標勉強時間（分）",
        min_value=1,
        value=1000
    )

    if st.button("保存"):

        c.execute(
            """
            INSERT INTO goals
            (username, subject, goal_minutes)
            VALUES (?, ?, ?)
            """,
            (
                st.session_state.user,
                subject,
                goal
            )
        )

        conn.commit()

        st.success("目標を保存しました")

    # ← if の外に出す
    goals = c.execute(
        """
        SELECT subject, goal_minutes
        FROM goals
        WHERE username=?
        """,
        (st.session_state.user,)
    ).fetchall()

    st.subheader("現在の目標")

    for subject, goal in goals:
        st.write(f"{subject} : {goal}分")