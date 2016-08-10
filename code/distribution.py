import numpy as np
import matplotlib.pyplot as plt

L = 100. # mm
h = 290. # mm

# Normalization constant for the uniform case
c_uni = 1/np.pi
# Normalization constant for the cossquaredtheta case
c_cos = 2/np.pi

x = np.linspace(0.0, L, 200)
# First wire y-position: 110 mm
#z = np.linspace(0.0, h/2, 4)
z = np.array([110])
theta = np.linspace(-np.arctan(L/h), np.arctan(L/h), 200)

def n_x(x):
    first_order = 1/np.pi * (np.arctan((L - x)/h) + np.arctan(x/h))
    correction = 0
    return first_order + correction

def n_theta(theta):
    first_oder = 1 - h/L * np.tan(abs(theta))
    correction = 0
    return first_order + correction

def n_x_z(x, z, cos=True):
    s_1, s_2 = [], []
    for x_i in x:
        # "z-maessiger" Bereich (1 und 3)
        if abs(z/h - 0.5) >= abs(x_i/L - 0.5):
            s_1.append((L-x_i)/max(h-z, z))
            s_2.append(x_i/max(h-z, z))
        # "x-maessiger" Bereich (2 und 4)
        else:
            s_1.append(min(x_i, L-x_i)/z)
            s_2.append(min(x_i, L-x_i)/(h-z))

    s_1 = np.array(s_1)
    s_2 = np.array(s_2)

    first_order = (np.arctan(s_1) + np.arctan(s_2))
    correction = s_1/(s_1**2+1) + s_2/(s_2**2+1) 
    if cos:
        return c_cos * (first_order + correction)
    else:
        return c_uni * (first_order)

print(theta)

#styles = ['k-', 'k--', 'k-.', 'k:']
styles = ['k--']

plt.figure()
#plt.plot(x, n_x(x))
for i, z_i in enumerate(z):
    plt.plot(x, n_x_z(x, z_i), styles[i], label="y = {} mm".format(int(z_i+0.5)))
plt.legend(loc=0)
plt.xlabel("x position [mm]")
plt.ylabel("flux [arbitrary units]")
#plt.plot(theta, n_theta(theta))
#plt.ylim(0,1)
plt.show()
