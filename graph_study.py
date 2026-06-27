from datetime import date

today = str(date.today())

totals = {}

with open("study_record2.txt", "r", encoding="utf-8") as file:
    for line in file:
        day, subject, minutes = line.strip().split(",")
        if day != today:
            continue

        minutes = int(minutes)

        if subject not in totals:
            totals[subject] = 0
        totals[subject] += minutes

print(totals)

import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Meiryo"
subjects = list(totals.keys())
minutes = list(totals.values())


total_time = list(totals.values())

st.metric(
    label="📚 今日の勉強時間",
    value=f"{total_time}分"
)

goal = 180

achievement = total_time / goal * 100

st.subheader("🎯 目標達成率")

st.progress(min(achievement / 100, 1.0))

st.write(f"{achievement:.1f}% 達成")

if achievement >= 100:
    st.success("🎉 目標達成！")
else:
    remain = goal - total_time
    st.info(f"あと {remain} 分で目標達成")

plt.bar(subjects, minutes)

plt.title("勉強時間")
plt.xlabel("科目")
plt.ylabel("時間（分）")

ranking = sorted(
    totals.items(),
    key=lambda x: x[1],
    reverse=True
)

print("---勉強時間ランキング---")

for i, (subject, study_time) in enumerate(ranking, start=1):
    print(f"{i}位 {subject} {study_time}分")

plt.show()

plt.figure(figsize=(8, 8))

plt.pie(
    minutes,
    labels=subjects,
    autopct="%1.1f%%"
)
plt.title("科目ごとの勉強時間割合")

plt.show()