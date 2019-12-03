"""Test high-level mutual information functions."""
import numpy as np

from frites.core import permute_mi_vector, get_core_mi_fun

rnd = np.random.RandomState(0)

mi_methods = ['gc', 'bin']
mi_types = ['cc', 'cd', 'ccd']
inferences = ['ffx', 'rfx']
n_perm = 15

n_times, n_epochs, n_suj, n_conds = 100, 100, 2, 3
x = rnd.rand(n_times, 1, n_epochs)
y = rnd.rand(n_epochs).reshape(-1, 1)
z = np.round(np.linspace(0, n_conds, n_epochs)).astype(int).reshape(-1, 1)
suj = np.round(np.linspace(0, n_suj, n_epochs)).astype(int)


class TestMiFun(object):  # noqa

    def test_mi_fun(self):
        """Test mi functions."""
        for mi_meth in mi_methods:
            mi_funs = get_core_mi_fun(mi_meth)
            for mi in mi_types:
                fun = mi_funs[mi]
                for inf in inferences:
                    y_c = z if mi is 'cd' else y
                    fun(x, y_c, z, suj, inf)

    def test_permute_mi_vector(self):
        """Test function permute_mi_vector."""
        for mi in mi_types:
            for inf in inferences:
                y_p = permute_mi_vector(y, suj, mi_type=mi, inference=inf,
                                        n_perm=n_perm)
                assert len(y_p) == n_perm