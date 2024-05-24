num = int(input())
num = str(num)
w = []
w = w.append(num)
w = w.split()
a = int(w[0])
b = int(w[-1])
c = int(w[1])
d = int(w[2])
if a + b == d - c:
    print("Да")
else:
    print("НЕТ")
