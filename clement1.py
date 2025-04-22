import numpy as np 
import matplotlib.pyplot as plt

# Define constants
rho = 1000 # kg/m^3
cp = 4000 # J/kg/K
dt = 60 * 60 * 24 * 365 # % one year in seconds
end = 170

# Define time array
time = np.arange(0, end, 1) # time in years of our simulation

# Define forcing G
G = np.zeros(end)
G[:70] = np.linspace(0, 4, 70)
G[70:] = 4

# Function to integrate temperature
def integrate_temperature(H, alpha, G, dt, rho, cp):
    C = rho * cp * H
    T = np.zeros(len(G) + 1)
    for x in range(len(G)):
        T[x + 1] = T[x] + (dt / C) * (G[x] - alpha * T[x])
    
    return T

# Case #1: Large C, small alpha
H1 = 1000
alpha1 = 0.5
T1 = integrate_temperature(H1, alpha1, G, dt, rho, cp)

# Case #2: Small C, large alpha
H2 = 50
alpha2 = 1.6
T2 = integrate_temperature(H2, alpha2, G, dt, rho, cp)

# Case #3: Large C, large alpha
H3 = 1000
alpha3 = 1.6
T3 = integrate_temperature(H3, alpha3, G, dt, rho, cp)

# Plot the forcing G as a function of time
plt.figure()
plt.plot(time, G, label = 'Forcing (G)')
plt.xlabel('Time (years)')
plt.ylabel('Forcing (W/m^2)')
plt.title('Forcing as a Function of Time')
plt.legend()
plt.grid()
plt.savefig(r"C:\Users\deela\Downloads\clementplot1.png", dpi = 400, bbox_inches = 'tight')
plt.show()

# Plot the temperature for each case
plt.figure()
plt.plot(time, T1[:end], label = 'Case #1: Large C, small alpha')
plt.plot(time, T2[:end], label = 'Case #2: Small C, large alpha')
plt.plot(time, T3[:end], label = 'Case #3: Large C, large alpha')
plt.xlabel('Time (years)')
plt.ylabel('Temperature Anomaly (K)')
plt.title('Temperature Anomaly Over Time for Different Cases')
plt.legend()
plt.grid()
plt.savefig(r"C:\Users\deela\Downloads\clementplot2.png", dpi = 400, bbox_inches = 'tight')
plt.show()

# Calculate the transient climate response (TCR) at year 70 for each case
TCR_case1 = T1[70]
TCR_case2 = T2[70]
TCR_case3 = T3[70]

# Calculate the equilibrium climate sensitivity (ECS) for each case (assuming equilibrium at year 170)
ECS_case1 = T1[end]
ECS_case2 = T2[end]
ECS_case3 = T3[end]

print('Transient Climate Response (TCR) at year 70:')
print(f'Case #1: {TCR_case1} K')
print(f'Case #2: {TCR_case2} K')
print(f'Case #3: {TCR_case3} K')

print('\nEquilibrium Climate Sensitivity (ECS) at year 170:\n')
print(f'Case #1: {ECS_case1} K')
print(f'Case #2: {ECS_case2} K')
print(f'Case #3: {ECS_case3} K')