import numpy as np 

P = np.array([[-1, 0, 0], [-1, 0, 1], [1, 1, 0]])
Pneg = np.linalg.inv(P)

A = np.array([[1, 0, 0], [-1, 2, 0], [1, 0, 2]])

eigVals = np.linalg.eigvals(A)
print("Eigenvalues: ", eigVals)

print("\nP\n", P)
print("\nA\n", A)
print("\nP^-1\n", Pneg)

prod1 = np.matmul(Pneg, A)

print("\nP^-1A\n", prod1)

prod2 = np.matmul(prod1, P)

print("\nP^-1AP\n", prod2)


# import numpy as np 

# P = np.array([[0, 0, 1, 0], [0, 0, 0, 1], [0, 0, 0, 0], [0, 0, 0, 0]])
# prod3 = np.matmul(P, P)
# print("\nP\n", P)
# print("\nPP\n", prod3)