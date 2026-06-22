total_legs = float(input('足の数を入力してください'))
num_turtles = float(input('亀の数を入力してください'))

num_cranes = (total_legs - 4*num_turtles) // 2
print(num_cranes)

