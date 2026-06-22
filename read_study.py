
totals = {}

with open("study_record.txt", "r", encoding="utf-8") as file:
    for line in file:
        subject, minutes = line.strip().split(",")
        minutes = int(minutes)

        if subject in totals:
            totals[subject] += minutes

        else:
            totals[subject] = minutes

ranking = sorted(
    totals.items(),
    key=lambda x: x[1],
    reverse=True
)

for i, (subject, minutes) in enumerate(ranking, start=1):
    print(f"{i}位{subject}{minutes}分")