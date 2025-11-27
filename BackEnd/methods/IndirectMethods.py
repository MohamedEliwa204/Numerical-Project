from .BaseFunctions import *

class GaussSeidel(IterativeSolver):
    @override
    def iterate(self, A, b, x):
        x_old = x.copy()
        x_new = x.copy()
        relative_error = []

        for k in range(0, self.n):
            newSum = self.round_significant(np.dot(A[k, :k], x_new[:k]))
            oldSum = self.round_significant(np.dot(A[k, k + 1:], x_old[k + 1:]))
            sum = self.round_significant(newSum + oldSum)
            numerator = self.round_significant(b[k] - sum)
            x_new[k] = self.round_significant(numerator / A[k][k])
            relative_error.append(self.calculate_error(x_old, x_new))
        self.steps.append((x_new.copy(), relative_error.copy()))
        return x_new


class JacobiIteration(IterativeSolver):
    @override
    def iterate(self, A, b, x):
        x_old = x.copy()
        x_new = np.zeros_like(x)
        relative_error = []

        for k in range(0, self.n):
            oldSum1 = self.round_significant(np.dot(A[k, :k], x_old[:k]))
            oldSum2 = self.round_significant(np.dot(A[k, k + 1:], x_old[k + 1:]))
            sum = self.round_significant(oldSum1 + oldSum2)
            numerator = self.round_significant(b[k] - sum)
            x_new[k] = self.round_significant(numerator / A[k][k])
            relative_error.append(self.calculate_error(x_old, x_new))
        self.steps.append((x_new.copy(), relative_error.copy()))

        return x_new