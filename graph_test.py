import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Meiryo"

subjects = ["数学", "英語", "情報"]
minutes = [70, 30, 60]

plt.bar(subjects, minutes)
plt.show()

