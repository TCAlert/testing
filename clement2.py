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
G_original = np.zeros(end)
G_original[:70] = np.linspace(0, 4, 70)
G_original[70:] = 4

# Define new forcing G with geoengineering intervention (stabilizes at 3 W/m²)
G_geoengineering = np.zeros(end)
G_geoengineering[:70] = np.linspace(0, 3, 70)
G_geoengineering[70:] = 3

# Function to integrate temperature
def integrate_temperature(H, alpha, G, dt, rho, cp):
    C = rho * cp * H
    T = np.zeros(len(G) + 1)
    for x in range(len(G)):
        T[x + 1] = T[x] + (dt / C) * (G[x] - alpha * T[x])
    
    return T

# Case #1: Large C, small alpha (H=1000 m, alpha=0.5)
H1 = 1000
alpha1 = 0.5
T1_original = integrate_temperature(H1, alpha1, G_original, dt, rho, cp)
T1_geoengineering = integrate_temperature(H1, alpha1, G_geoengineering, dt, rho, cp)

# Case #2: Small C, large alpha (H=50 m, alpha=1.6)
H2 = 50
alpha2 = 1.6
T2_original = integrate_temperature(H2, alpha2, G_original, dt, rho, cp)
T2_geoengineering = integrate_temperature(H2, alpha2, G_geoengineering, dt, rho, cp)

# Case #3: Large C, large alpha (H=1000 m, alpha=1.6)
H3 = 1000
alpha3 = 1.6
T3_original = integrate_temperature(H3, alpha3, G_original, dt, rho, cp)
T3_geoengineering = integrate_temperature(H3, alpha3, G_geoengineering, dt, rho, cp)

# Calculate the transient climate response (TCR) at year 70 for each case with geoengineering intervention
TCR_case1_geoengineering = T1_geoengineering[70]
TCR_case2_geoengineering = T2_geoengineering[70]
TCR_case3_geoengineering = T3_geoengineering[70]

# Calculate the benefit of geoengineering intervention (difference in TCR)
benefit_case1 = T1_original[70] - TCR_case1_geoengineering
benefit_case2 = T2_original[70] - TCR_case2_geoengineering
benefit_case3 = T3_original[70] - TCR_case3_geoengineering
#% Calculate the equilibrium climate sensitivity (ECS) for each case with geoengineering intervention (assuming equilibrium at year 170)
ECS_case1_geoengineering = T1_geoengineering[end]
ECS_case2_geoengineering = T2_geoengineering[end]
ECS_case3_geoengineering = T3_geoengineering[end]

print('Transient Climate Response (TCR) at year 70 with geoengineering intervention:\n')
print(f'Case #1: {TCR_case1_geoengineering} K')
print(f'Case #2: {TCR_case2_geoengineering} K')
print(f'Case #3: {TCR_case3_geoengineering} K')

print('\nBenefit of geoengineering intervention (difference in TCR):\n')
print(f'Case #1: {benefit_case1} K')
print(f'Case #2: {benefit_case2} K')
print(f'Case #3: {benefit_case3} K')

print('\nEquilibrium Climate Sensitivity (ECS) at year 170 with geoengineering intervention:\n')
print(f'Case #1: {ECS_case1_geoengineering} K')
print(f'Case #2: {ECS_case2_geoengineering} K')
print(f'Case #3: {ECS_case3_geoengineering} K')

# Plot the temperature anomaly for each case under the new scenario and original scenario for comparison
plt.figure(figsize = (18, 9))
plt.plot(time, T1_geoengineering[:end], 'b', label = 'Case #1: Large C, small alpha (Geoengineering)')
plt.plot(time, T2_geoengineering[:end], 'g', label = 'Case #2: Small C, large alpha (Geoengineering)')
plt.plot(time, T3_geoengineering[:end], 'r', label = 'Case #3: Large C, large alpha (Geoengineering)')
plt.plot(time, T1_original[:end], 'b--', label = 'Case #1: Large C, small alpha (Original)')
plt.plot(time, T2_original[:end], 'g--', label = 'Case #2: Small C, large alpha (Original)')
plt.plot(time, T3_original[:end], 'r--', label = 'Case #3: Large C, large alpha (Original)')
plt.xlabel('Time (years)')
plt.ylabel('Temperature Anomaly (K)')
plt.title('Temperature Anomaly Over Time for Different Cases with Geoengineering Intervention')
plt.legend()
plt.grid()
plt.savefig(r"C:\Users\deela\Downloads\clementplot3.png", dpi = 400, bbox_inches = 'tight')
plt.show()