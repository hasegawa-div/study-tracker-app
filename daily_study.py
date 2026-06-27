daily_totals = {}

with open("study_record2.txt", "r", encoding="utf-8") as file:
    for line in file:
        day, subject, minutes = line.strip().split(",")
        minutes = int(minutes)

        if day not in daily_totals:
            daily_totals[day] = 0

        daily_totals[day] += minutes

print("---日ごとの勉強時間---")

for day, total in daily_totals.items():
    print(f"{day}:{total}分")
total_time = sum(daily_totals.values())

average = total_time / len(daily_totals)

best_day = max(
daily_totals,
key=daily_totals.get
)

print(f"\n合計 : {total_time}分")
print(f"平均 : {average:.1f}分")
print(f"最高 : {daily_totals[best_day]}分 ({best_day})")

import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Meiryo"

days = list(daily_totals.keys())
totals = list(daily_totals.values())

plt.plot(days, totals, marker="o")

plt.title("日ごとの勉強時間")
plt.xlabel("日付")
plt.ylabel("勉強時間（分）")

plt.show()

total_time = sum(daily_totals.values())




