import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(-5, 7, 100)
y = x**2 - 2*x + 1

plt.figure(figsize=(8, 6))
plt.plot(x,y)
plt.show()
