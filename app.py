import streamlit as st
from datetime import date, datetime, timedelta
import calendar
import matplotlib.pyplot as plt


plt.rcParams["font.family"] = "Meiryo"
plt.rcParams["axes.unicode_minus"] = False
st.title("📚 勉強時間管理アプリ")

st.subheader("✏️ 勉強記録を追加")

subject_input = st.text_input("科目")
minutes_input = st.number_input("勉強時間（分）", min_value=1, step=1)
today = st.date_input("日付を選んでね", value=date.today())
today = str(today)
if st.button("追加"):
    if subject_input:
        with open("study_record2.txt", "a", encoding="utf-8") as file:
            file.write(f"{today},{subject_input},{minutes_input}\n")

        st.success("記録を追加しました！")
        st.rerun()
    else:
        st.warning("科目を入力してください")

weekly_total = 0
daily_totals = {}
study_days = set()

all_totals = {}


totals= {}

# データ読み込み
try:
    with open("study_record2.txt", "r", encoding="utf-8") as file:
        for line in file:
            day, subject, minutes = line.strip().split(",")
            minutes = int(minutes)

            if subject not in all_totals:
                all_totals[subject] = 0

            all_totals[subject] += minutes

            record_date = datetime.strptime(day, "%Y-%m-%d").date()
            study_days.add(record_date)

            # 今週の勉強時間
            if date.today() - timedelta(days=6) <= record_date <= date.today():
                weekly_total += int(minutes)
                
                day_str = str(record_date)

                if day_str not in daily_totals:
                    daily_totals[day_str] = 0

                daily_totals[day_str] += int(minutes)
            # 今日以外はスキップ
            if day != today:
                continue


            if subject not in totals:
                totals[subject] = 0

            totals[subject] += minutes

except FileNotFoundError:
    st.error("study_record2.txt が見つかりません")
    st.stop()

except FileNotFoundError:
    st.error("study_record2.txt が見つかりません")
    st.stop()
streak = 0
check_day = date.today()

while check_day in study_days:
    streak += 1
    check_day -= timedelta(days=1)
if not totals:
    st.warning("この日のデータはありません")
    st.stop()

# 表示用データ
subjects = list(totals.keys())
minutes = list(totals.values())

total_time = sum(minutes)


st.metric(
    label="📚 今日の勉強時間",
    value=f"{total_time}分"
)
st.metric(
    label="📅 今週の勉強時間",
    value=f"{weekly_total}分"
)
st.metric(
    label="🔥 連続勉強日数",
    value=f"{streak}日"
)
goal = st.number_input("🎯 目標勉強時間（分）",
    min_value=1,
    value=180,
    step=10)

achievement = total_time / goal * 100

st.subheader("🎯 目標達成率")

st.progress(min(achievement / 100, 1.0))

st.write(f"{achievement:.1f}% 達成")

if achievement >= 100:
    st.success("🎉 目標達成！")
else:
    remain = goal - total_time
    st.info(f"あと {remain} 分で目標達成")


# ランキング
ranking = sorted(totals.items(), key=lambda x: x[1], reverse=True)
all_ranking = sorted(
    all_totals.items(),
    key=lambda x: x[1],
    reverse=True
)
st.subheader("🗑️ 記録削除")
records = []
records.append(line.strip())
record_to_delete = st.selectbox(
    "削除する記録を選択",
    records
)
if st.button("削除"):
    with open("study_record2.txt", "w", encoding="utf-8") as file:
        for record in records:
            if record != record_to_delete:
                file.write(record + "\n")

    st.success("削除しました")
    st.rerun()

st.subheader("🏅 累計ランキング")

for i, (subject, time) in enumerate(all_ranking, start=1):
    st.write(f"{i}位 {subject}：{time}分")
st.subheader("🏆 勉強時間ランキング")
for i, (subject, time) in enumerate(ranking, start=1):
    st.write(f"{i}位 {subject}：{time}分")

# グラフ（棒）
st.subheader("📊 科目別勉強時間")
fig1, ax1 = plt.subplots()
ax1.bar(subjects, minutes)
ax1.set_xlabel("科目")
ax1.set_ylabel("分")
st.pyplot(fig1)

# グラフ（円）
st.subheader("🥧 割合")
fig2, ax2 = plt.subplots()
ax2.pie(minutes, labels=subjects, autopct="%1.1f%%")
ax2.set_title("科目ごとの勉強時間割合")
st.pyplot(fig2)

#折れ線グラフ
st.subheader("📈 1週間の勉強時間推移")

days = sorted(daily_totals.keys())
times = [daily_totals[d] for d in days]

fig3, ax3 = plt.subplots()

ax3.plot(days, times, marker="o")

ax3.set_xlabel("日付")
ax3.set_ylabel("勉強時間（分）")

plt.xticks(rotation=45)

st.pyplot(fig3)

#月間カレンダー
st.subheader("📅 勉強カレンダー")

year = date.today().year
month = date.today().month

cal = calendar.monthcalendar(year, month)

study_day_numbers = set()

for d in study_days:
    if d.year == year and d.month == month:
        study_day_numbers.add(d.day)

calendar_text = "月 火 水 木 金 土 日\n"

for week in cal:
    for day in week:

        if day == 0:
            calendar_text += "⬜ "

        elif day in study_day_numbers:
            calendar_text += "🟩 "

        else:
            calendar_text += "⬛ "

    calendar_text += "\n"

st.code(calendar_text)