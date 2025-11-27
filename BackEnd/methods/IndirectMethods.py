from .BaseFunctions import *

class GaussSeidel(IterativeSolver):
    @override
    def iterate(self, A, b, x):
        x_old = x.copy()
        x_new = x.copy()
        relative_error = []

        for k in range(0, self.n):
            x_new[k] = (b[k] - (np.dot(A[k, :k], x_new[:k])) - np.dot(A[k, k + 1:], x_old[k + 1:])) / A[k][k]
            relative_error.append(self.calculate_individual_error(x_old[k], x_new[k]))
        self.steps.append((x_new.copy(), relative_error.copy()))
        return x_new


class JacobiIteration(IterativeSolver):
    @override
    def iterate(self, A, b, x):
        x_old = x.copy()
        x_new = np.zeros_like(x)
        relative_error = []

        for k in range(0, self.n):
            x_new[k] = (b[k] - (np.dot(A[k, :k], x_old[:k])) - np.dot(A[k, k + 1:], x_old[k + 1:])) / A[k][k]
            relative_error.append(self.calculate_individual_error(x_old[k], x_new[k]))
        self.steps.append((x_new.copy(), relative_error.copy()))

        return x_new