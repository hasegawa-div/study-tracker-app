from datetime import date

records = []
while True:
    subject = input("科目を入力（終了はｑ）")

    if subject == "q":
        break

    minutes = int(input("勉強時間（分）"))

    records.append({
      "subject":subject,
      "minutes":minutes  
    })
print("\n---勉強記録---")

total = 0

today = date.today()
with open("study_record2.txt", "a", encoding="utf-8") as file:
    for record in records:
        file.write(f"{today},{record['subject']},{record['minutes']}\n")
        print(f"{record['subject']}:{record['minutes']}分")
        total += record["minutes"]
print(f"\n合計：{total}分")

print("保存先確認")

with open ("study_record2.txt", "r", encoding="utf-8") as file:
    print(file.read())

import os

print("保存先")
print(os.path.abspath("study_record2.txt"))