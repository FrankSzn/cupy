import unittest

import numpy
try:
    import scipy.sparse
    scipy_available = True
except ImportError:
    scipy_available = False

import cupy
import cupy.sparse
from cupy import testing


def _make(xp, sp, dtype):
    data = xp.array([0, 1, 3, 2], dtype)
    indices = xp.array([0, 0, 2, 1], 'i')
    indptr = xp.array([0, 1, 2, 3, 4], 'i')
    # 0, 1, 0, 0
    # 0, 0, 0, 2
    # 0, 0, 3, 0
    return sp.csc_matrix((data, indices, indptr), shape=(3, 4))


def _make2(xp, sp, dtype):
    data = xp.array([2, 1, 3, 4], dtype)
    indices = xp.array([1, 0, 1, 2], 'i')
    indptr = xp.array([0, 0, 1, 4, 4], 'i')
    # 0, 0, 1, 0
    # 0, 2, 3, 0
    # 0, 0, 4, 0
    return sp.csc_matrix((data, indices, indptr), shape=(3, 4))


def _make3(xp, sp, dtype):
    data = xp.array([1, 4, 3, 2, 5], dtype)
    indices = xp.array([0, 3, 1, 1, 3], 'i')
    indptr = xp.array([0, 2, 3, 5], 'i')
    # 1, 0, 0
    # 0, 3, 2
    # 0, 0, 0
    # 4, 0, 5
    return sp.csc_matrix((data, indices, indptr), shape=(4, 3))


def _make_unordered(xp, sp, dtype):
    data = xp.array([1, 2, 3, 4], dtype)
    indices = xp.array([1, 0, 1, 2], 'i')
    indptr = xp.array([0, 0, 0, 2, 4], 'i')
    return sp.csc_matrix((data, indices, indptr), shape=(3, 4))


@testing.parameterize(*testing.product({
    'dtype': [numpy.float32, numpy.float64],
}))
class TestCscMatrix(unittest.TestCase):

    def setUp(self):
        self.m = _make(cupy, cupy.sparse, self.dtype)

    def test_dtype(self):
        self.assertEqual(self.m.dtype, self.dtype)

    def test_data(self):
        self.assertEqual(self.m.data.dtype, self.dtype)
        testing.assert_array_equal(
            self.m.data, cupy.array([0, 1, 3, 2], self.dtype))

    def test_indices(self):
        self.assertEqual(self.m.indices.dtype, numpy.int32)
        testing.assert_array_equal(
            self.m.indices, cupy.array([0, 0, 2, 1], self.dtype))

    def test_indptr(self):
        self.assertEqual(self.m.indptr.dtype, numpy.int32)
        testing.assert_array_equal(
            self.m.indptr, cupy.array([0, 1, 2, 3, 4], self.dtype))

    def test_init_copy(self):
        n = cupy.sparse.csc_matrix(self.m)
        self.assertIsNot(n, self.m)
        cupy.testing.assert_array_equal(n.data, self.m.data)
        cupy.testing.assert_array_equal(n.indices, self.m.indices)
        cupy.testing.assert_array_equal(n.indptr, self.m.indptr)
        self.assertEqual(n.shape, self.m.shape)

    def test_init_copy_other_sparse(self):
        n = cupy.sparse.csc_matrix(self.m.tocsr())
        cupy.testing.assert_array_equal(n.data, self.m.data)
        cupy.testing.assert_array_equal(n.indices, self.m.indices)
        cupy.testing.assert_array_equal(n.indptr, self.m.indptr)
        self.assertEqual(n.shape, self.m.shape)

    @unittest.skipUnless(scipy_available, 'requires scipy')
    def test_init_copy_scipy_sparse(self):
        m = _make(numpy, scipy.sparse, self.dtype)
        n = cupy.sparse.csc_matrix(m)
        self.assertIsInstance(n.data, cupy.ndarray)
        self.assertIsInstance(n.indices, cupy.ndarray)
        self.assertIsInstance(n.indptr, cupy.ndarray)
        cupy.testing.assert_array_equal(n.data, m.data)
        cupy.testing.assert_array_equal(n.indices, m.indices)
        cupy.testing.assert_array_equal(n.indptr, m.indptr)
        self.assertEqual(n.shape, m.shape)

    @unittest.skipUnless(scipy_available, 'requires scipy')
    def test_init_copy_other_scipy_sparse(self):
        m = _make(numpy, scipy.sparse, self.dtype)
        n = cupy.sparse.csc_matrix(m.tocsr())
        self.assertIsInstance(n.data, cupy.ndarray)
        self.assertIsInstance(n.indices, cupy.ndarray)
        self.assertIsInstance(n.indptr, cupy.ndarray)
        cupy.testing.assert_array_equal(n.data, m.data)
        cupy.testing.assert_array_equal(n.indices, m.indices)
        cupy.testing.assert_array_equal(n.indptr, m.indptr)
        self.assertEqual(n.shape, m.shape)

    def test_copy(self):
        n = self.m.copy()
        self.assertIsInstance(n, cupy.sparse.csc_matrix)
        self.assertIsNot(n, self.m)
        self.assertIsNot(n.data, self.m.data)
        self.assertIsNot(n.indices, self.m.indices)
        self.assertIsNot(n.indptr, self.m.indptr)
        cupy.testing.assert_array_equal(n.data, self.m.data)
        cupy.testing.assert_array_equal(n.indices, self.m.indices)
        cupy.testing.assert_array_equal(n.indptr, self.m.indptr)
        self.assertEqual(n.shape, self.m.shape)

    def test_shape(self):
        self.assertEqual(self.m.shape, (3, 4))

    def test_ndim(self):
        self.assertEqual(self.m.ndim, 2)

    def test_nnz(self):
        self.assertEqual(self.m.nnz, 4)

    @unittest.skipUnless(scipy_available, 'requires scipy')
    def test_get(self):
        m = self.m.get()
        self.assertIsInstance(m, scipy.sparse.csc_matrix)
        expect = [
            [0, 1, 0, 0],
            [0, 0, 0, 2],
            [0, 0, 3, 0]
        ]
        numpy.testing.assert_allclose(m.toarray(), expect)

    @unittest.skipUnless(scipy_available, 'requires scipy')
    def test_str(self):
        self.assertEqual(str(self.m), '''  (0, 0)\t0.0
  (0, 1)\t1.0
  (2, 2)\t3.0
  (1, 3)\t2.0''')

    def test_toarray(self):
        m = self.m.toarray()
        expect = [
            [0, 1, 0, 0],
            [0, 0, 0, 2],
            [0, 0, 3, 0]
        ]
        self.assertTrue(m.flags.c_contiguous)
        cupy.testing.assert_allclose(m, expect)


@testing.parameterize(*testing.product({
    'dtype': [numpy.float32, numpy.float64],
}))
@unittest.skipUnless(scipy_available, 'requires scipy')
class TestCscMatrixInit(unittest.TestCase):

    def setUp(self):
        self.shape = (3, 4)

    def data(self, xp):
        return xp.array([1, 2, 3, 4], self.dtype)

    def indices(self, xp):
        return xp.array([0, 0, 2, 1], 'i')

    def indptr(self, xp):
        return xp.array([0, 1, 2, 3, 4], 'i')

    @testing.numpy_cupy_equal(sp_name='sp')
    def test_shape_none(self, xp, sp):
        x = sp.csc_matrix(
            (self.data(xp), self.indices(xp), self.indptr(xp)), shape=None)
        self.assertEqual(x.shape, (3, 4))

    @testing.numpy_cupy_equal(sp_name='sp')
    def test_dtype(self, xp, sp):
        data = self.data(xp).astype('i')
        x = sp.csc_matrix(
            (data, self.indices(xp), self.indptr(xp)), dtype=self.dtype)
        self.assertEqual(x.dtype, self.dtype)

    @testing.numpy_cupy_equal(sp_name='sp')
    def test_copy_true(self, xp, sp):
        data = self.data(xp)
        indices = self.indices(xp)
        indptr = self.indptr(xp)
        x = sp.csc_matrix((data, indices, indptr), copy=True)

        self.assertIsNot(data, x.data)
        self.assertIsNot(indices, x.indices)
        self.assertIsNot(indptr, x.indptr)

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_init_with_shape(self, xp, sp):
        s = sp.csc_matrix(self.shape)
        self.assertEqual(s.shape, self.shape)
        self.assertEqual(s.dtype, 'd')
        self.assertEqual(s.size, 0)
        return s.toarray()

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_init_with_shape_and_dtype(self, xp, sp):
        s = sp.csc_matrix(self.shape, dtype=self.dtype)
        self.assertEqual(s.shape, self.shape)
        self.assertEqual(s.dtype, self.dtype)
        self.assertEqual(s.size, 0)
        return s.toarray()

    @testing.numpy_cupy_raises(sp_name='sp')
    def test_shape_invalid(self, xp, sp):
        sp.csc_matrix(
            (self.data(xp), self.indices(xp), self.indptr(xp)), shape=(2,))

    @testing.numpy_cupy_raises(sp_name='sp')
    def test_data_invalid(self, xp, sp):
        sp.csc_matrix(
            ('invalid', self.indices(xp), self.indptr(xp)), shape=self.shape)

    @testing.numpy_cupy_raises(sp_name='sp')
    def test_data_invalid_ndim(self, xp, sp):
        sp.csc_matrix(
            (self.data(xp)[None], self.indices(xp), self.indptr(xp)),
            shape=self.shape)

    @testing.numpy_cupy_raises(sp_name='sp')
    def test_indices_invalid(self, xp, sp):
        sp.csc_matrix(
            (self.data(xp), 'invalid', self.indptr(xp)), shape=self.shape)

    @testing.numpy_cupy_raises(sp_name='sp')
    def test_indices_invalid_ndim(self, xp, sp):
        sp.csc_matrix(
            (self.data(xp), self.indices(xp)[None], self.indptr(xp)),
            shape=self.shape)

    @testing.numpy_cupy_raises(sp_name='sp')
    def test_indptr_invalid(self, xp, sp):
        sp.csc_matrix(
            (self.data(xp), self.indices(xp), 'invalid'), shape=self.shape)

    @testing.numpy_cupy_raises(sp_name='sp')
    def test_indptr_invalid_ndim(self, xp, sp):
        sp.csc_matrix(
            (self.data(xp), self.indices(xp), self.indptr(xp)[None]),
            shape=self.shape)

    @testing.numpy_cupy_raises(sp_name='sp')
    def test_data_indices_different_length(self, xp, sp):
        data = xp.arange(5, dtype=self.dtype)
        sp.csc_matrix(
            (data, self.indices(xp), self.indptr(xp)), shape=self.shape)

    @testing.numpy_cupy_raises(sp_name='sp')
    def test_indptr_invalid_length(self, xp, sp):
        indptr = xp.array([0, 1], 'i')
        sp.csc_matrix(
            (self.data(xp), self.indices(xp), indptr), shape=self.shape)

    def test_unsupported_dtype(self):
        with self.assertRaises(ValueError):
            cupy.sparse.csc_matrix(
                (self.data(cupy), self.indices(cupy), self.indptr(cupy)),
                shape=self.shape, dtype='i')


@testing.parameterize(*testing.product({
    'dtype': [numpy.float32, numpy.float64],
}))
@unittest.skipUnless(scipy_available, 'requires scipy')
class TestCscMatrixScipyComparison(unittest.TestCase):

    @testing.numpy_cupy_raises(sp_name='sp', accept_error=TypeError)
    def test_len(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        len(m)

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_toarray(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        a = m.toarray()
        self.assertTrue(a.flags.c_contiguous)
        return a

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_toarray_c_order(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        a = m.toarray(order='C')
        self.assertTrue(a.flags.c_contiguous)
        return a

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_toarray_f_order(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        a = m.toarray(order='F')
        self.assertTrue(a.flags.f_contiguous)
        return a

    @testing.numpy_cupy_raises(sp_name='sp', accept_error=TypeError)
    def test_toarray_unknown_order(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        m.toarray(order='unknown')

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_tocoo(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        return m.tocoo().toarray()

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_tocsc(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        return m.tocsc().toarray()

    # dot
    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_dot_scalar(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        return m.dot(2.0).toarray()

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_dot_numpy_scalar(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        return m.dot(numpy.dtype(self.dtype).type(2.0)).toarray()

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_dot_csr(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        x = _make3(xp, sp, self.dtype)
        return m.dot(x).toarray()

    @testing.numpy_cupy_raises(sp_name='sp', accept_error=ValueError)
    def test_dot_csr_invalid_shape(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        x = sp.csr_matrix((5, 3), dtype=self.dtype)
        m.dot(x)

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_dot_csc(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        x = _make3(xp, sp, self.dtype).tocsc()
        return m.dot(x).toarray()

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_dot_sparse(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        x = _make3(xp, sp, self.dtype).tocoo()
        return m.dot(x).toarray()

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_dot_zero_dim(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        x = xp.array(2, dtype=self.dtype)
        return m.dot(x).toarray()

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_dot_dense_vector(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        x = xp.arange(4).astype(self.dtype)
        return m.dot(x)

    @testing.numpy_cupy_raises(sp_name='sp', accept_error=ValueError)
    def test_dot_dense_vector_invalid_shape(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        x = xp.arange(5).astype(self.dtype)
        m.dot(x)

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_dot_dense_matrix(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        x = xp.arange(8).reshape(4, 2).astype(self.dtype)
        return m.dot(x)

    @testing.numpy_cupy_raises(sp_name='sp', accept_error=ValueError)
    def test_dot_dense_matrix_invalid_shape(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        x = xp.arange(10).reshape(5, 2).astype(self.dtype)
        m.dot(x)

    @testing.numpy_cupy_raises(sp_name='sp', accept_error=ValueError)
    def test_dot_dense_ndim3(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        x = xp.arange(24).reshape(4, 2, 3).astype(self.dtype)
        m.dot(x)

    @testing.numpy_cupy_raises(sp_name='sp')
    def test_dot_unsupported(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        m.dot(None)

    # __add__
    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_add_zero(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        return (m + 0).toarray()

    @testing.numpy_cupy_raises(sp_name='sp')
    def test_add_scalar(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        m + 1

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_add_csr(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        n = _make2(xp, sp, self.dtype)
        return (m + n).toarray()

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_add_coo(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        n = _make2(xp, sp, self.dtype).tocoo()
        return (m + n).toarray()

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_add_dense(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        n = xp.arange(12).reshape(3, 4)
        return m + n

    # __radd__
    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_radd_zero(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        return (0 + m).toarray()

    @testing.numpy_cupy_raises(sp_name='sp')
    def test_radd_scalar(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        1 + m

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_radd_dense(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        n = xp.arange(12).reshape(3, 4)
        return n + m

    # __sub__
    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_sub_zero(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        return (m - 0).toarray()

    @testing.numpy_cupy_raises(sp_name='sp')
    def test_sub_scalar(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        m - 1

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_sub_csr(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        n = _make2(xp, sp, self.dtype)
        return (m - n).toarray()

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_sub_coo(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        n = _make2(xp, sp, self.dtype).tocoo()
        return (m - n).toarray()

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_sub_dense(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        n = xp.arange(12).reshape(3, 4)
        return m - n

    # __rsub__
    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_rsub_zero(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        return (0 - m).toarray()

    @testing.numpy_cupy_raises(sp_name='sp')
    def test_rsub_scalar(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        1 - m

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_rsub_dense(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        n = xp.arange(12).reshape(3, 4)
        return n - m

    # __mul__
    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_mul_scalar(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        return (m * 2.0).toarray()

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_mul_numpy_scalar(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        return (m * numpy.dtype(self.dtype).type(2.0)).toarray()

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_mul_csr(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        x = _make3(xp, sp, self.dtype)
        return (m * x).toarray()

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_mul_csc(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        x = _make3(xp, sp, self.dtype).tocsc()
        return (m * x).toarray()

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_mul_sparse(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        x = _make3(xp, sp, self.dtype).tocoo()
        return (m * x).toarray()

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_mul_zero_dim(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        x = xp.array(2, dtype=self.dtype)
        return (m * x).toarray()

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_mul_dense_vector(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        x = xp.arange(4).astype(self.dtype)
        return m * x

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_mul_dense_matrix(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        x = xp.arange(8).reshape(4, 2).astype(self.dtype)
        return (m * x)

    @testing.numpy_cupy_raises(sp_name='sp')
    def test_mul_dense_ndim3(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        x = xp.arange(24).reshape(4, 2, 3).astype(self.dtype)
        m * x

    @testing.numpy_cupy_raises(sp_name='sp')
    def test_mul_unsupported(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        m * None

    # __rmul__
    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_rmul_scalar(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        return (2.0 * m).toarray()

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_rmul_numpy_scalar(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        return (numpy.dtype(self.dtype).type(2.0) * m).toarray()

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_rmul_csr(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        x = _make3(xp, sp, self.dtype)
        return (x * m).toarray()

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_rmul_csc(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        x = _make3(xp, sp, self.dtype).tocsc()
        return (x * m).toarray()

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_rmul_sparse(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        x = _make3(xp, sp, self.dtype).tocoo()
        return (x * m).toarray()

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_rmul_zero_dim(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        x = xp.array(2, dtype=self.dtype)
        return (x * m).toarray()

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_rmul_dense_matrix(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        x = xp.arange(12).reshape(4, 3).astype(self.dtype)
        return x * m

    @testing.numpy_cupy_raises(sp_name='sp')
    def test_rmul_dense_ndim3(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        x = xp.arange(24).reshape(4, 2, 3).astype(self.dtype)
        x * m

    @testing.numpy_cupy_raises(sp_name='sp')
    def test_rmul_unsupported(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        None * m

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_tocsr(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        return m.tocsr().toarray()

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_sort_indices(self, xp, sp):
        m = _make_unordered(xp, sp, self.dtype)
        m.sort_indices()
        return m.toarray()

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_transpose(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        return m.transpose().toarray()


@testing.parameterize(*testing.product({
    'dtype': [numpy.float32, numpy.float64],
}))
@unittest.skipUnless(scipy_available, 'requires scipy')
class TestCscMatrixScipyCompressed(unittest.TestCase):

    @testing.numpy_cupy_equal(sp_name='sp')
    def test_get_shape(self, xp, sp):
        return _make(xp, sp, self.dtype).get_shape()

    @testing.numpy_cupy_equal(sp_name='sp')
    def test_getnnz(self, xp, sp):
        return _make(xp, sp, self.dtype).getnnz()


@testing.parameterize(*testing.product({
    'dtype': [numpy.float32, numpy.float64],
}))
@unittest.skipUnless(scipy_available, 'requires scipy')
class TestCscMatrixData(unittest.TestCase):

    @testing.numpy_cupy_equal(sp_name='sp')
    def test_dtype(self, xp, sp):
        return _make(xp, sp, self.dtype).dtype

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_abs(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        return abs(m).toarray()

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_neg(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        return (-m).toarray()

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_astype(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        return m.astype('d').toarray()

    @testing.numpy_cupy_equal(sp_name='sp')
    def test_count_nonzero(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        return m.count_nonzero()

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_power(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        return m.power(2).toarray()

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_power_with_dtype(self, xp, sp):
        m = _make(xp, sp, self.dtype)
        return m.power(2, 'd').toarray()


@testing.parameterize(*testing.product({
    'dtype': [numpy.float32, numpy.float64],
    'ufunc': [
        'arcsin', 'arcsinh', 'arctan', 'arctanh', 'ceil', 'deg2rad', 'expm1',
        'floor', 'log1p', 'rad2deg', 'rint', 'sign', 'sin', 'sinh', 'sqrt',
        'tan', 'tanh', 'trunc',
    ],
}))
@unittest.skipUnless(scipy_available, 'requires scipy')
class TestUfunc(unittest.TestCase):

    @testing.numpy_cupy_allclose(sp_name='sp', atol=1e-5)
    def test_ufun(self, xp, sp):
        x = _make(xp, sp, self.dtype)
        x.data *= 0.1
        return getattr(x, self.ufunc)().toarray()


class TestIsspmatrixCsc(unittest.TestCase):

    def test_csr(self):
        x = cupy.sparse.csr_matrix(
            (cupy.array([], 'f'),
             cupy.array([], 'i'),
             cupy.array([0], 'i')),
            shape=(0, 0), dtype='f')
        self.assertFalse(cupy.sparse.isspmatrix_csc(x))

    def test_csc(self):
        x = cupy.sparse.csc_matrix(
            (cupy.array([], 'f'),
             cupy.array([], 'i'),
             cupy.array([0], 'i')),
            shape=(0, 0), dtype='f')
        self.assertTrue(cupy.sparse.isspmatrix_csc(x))


@testing.parameterize(*testing.product({
    'dtype': [numpy.float32, numpy.float64],
}))
@unittest.skipUnless(scipy_available, 'requires scipy')
class TestCsrMatrixGetitem(unittest.TestCase):

    @testing.numpy_cupy_equal(sp_name='sp')
    def test_getitem_int_int(self, xp, sp):
        self.assertEqual(_make(xp, sp, self.dtype)[0, 1], 1)

    @testing.numpy_cupy_equal(sp_name='sp')
    def test_getitem_int_int_not_found(self, xp, sp):
        self.assertEqual(_make(xp, sp, self.dtype)[1, 1], 0)

    @testing.numpy_cupy_equal(sp_name='sp')
    def test_getitem_int_int_negative(self, xp, sp):
        self.assertEqual(_make(xp, sp, self.dtype)[-1, -2], 3)

    @testing.numpy_cupy_raises(sp_name='sp', accept_error=IndexError)
    def test_getitem_int_int_too_small_row(self, xp, sp):
        _make(xp, sp, self.dtype)[-4, 0]

    @testing.numpy_cupy_raises(sp_name='sp', accept_error=IndexError)
    def test_getitem_int_int_too_large_row(self, xp, sp):
        _make(xp, sp, self.dtype)[3, 0]

    @testing.numpy_cupy_raises(sp_name='sp', accept_error=IndexError)
    def test_getitem_int_int_too_small_col(self, xp, sp):
        _make(xp, sp, self.dtype)[0, -5]

    @testing.numpy_cupy_raises(sp_name='sp', accept_error=IndexError)
    def test_getitem_int_int_too_large_col(self, xp, sp):
        _make(xp, sp, self.dtype)[0, 4]
