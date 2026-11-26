import unittest

import numpy as np
from numpy.testing import assert_allclose
from scipy.signal import csd

from transient_welch import finite_sums, corrections
from linear_welch import expected_spectra
from finite_covariance import lag_covariances, centered_moments


class TransientWelchChecks(unittest.TestCase):
    def test_binary_sums_match_direct_nonnormal_and_unit_root(self):
        f=np.array([[1.,.23],[0,.7]])
        k=np.array([[1.,-.3],[-.3,-2.]])
        for n in [0,1,2,3,17,128,257]:
            power=np.eye(2); total=np.zeros((2,2)); gram=np.zeros((2,2))
            for _ in range(n):
                total+=power;gram+=power@k@power.T;power=power@f
            actual=finite_sums(f,k,n)
            for a,b in zip(actual,[power,total,gram]):
                assert_allclose(a,b,rtol=2e-13,atol=2e-12)

    def fixture(self):
        f=np.array([[.78,.22],[0,.49]])
        p=np.array([[1.2,.1],[.1,.7]])
        initial=np.array([[.3,.08],[.08,.2]])
        mean=np.array([.7,-.5])
        observation=np.array([[1.,.2],[-.1,1.]])
        return f,p,initial,mean,observation

    def dense(self,f,p,k,observation,count,burn):
        powers=[np.linalg.matrix_power(f,t) for t in range(burn+count)]
        # Independent direct time-by-time raw second moments.
        blocks=[]
        for t in range(count):
            row=[]
            for u in range(count):
                stationary=(np.linalg.matrix_power(f,t-u)@p if t>=u
                            else p@np.linalg.matrix_power(f,u-t).T)
                row.append(observation@(stationary+powers[burn+t]@k@powers[burn+u].T)@observation.T)
            blocks.append(row)
        return np.asarray(blocks)

    def test_dense_time_moments_match_welch_and_centering(self):
        f,p,initial,mean,o=self.fixture()
        k=initial-p+np.outer(mean,mean)
        for segment in [5,6]:
            count=23;burn=3;hop=2
            raw=self.dense(f,p,k,o,count,burn)
            lags=lag_covariances(f,p,count,observed=2)
            observed=np.einsum('ai,tij,bj->tab',o,lags,o)
            stationary=expected_spectra(observed,segment)
            covariance=centered_moments(observed)[0]
            correction,cov_correction,segments=corrections(f,k,o,count,burn,segment,hop)
            from scipy.signal import get_window
            window=get_window('hann',segment,fftbins=True)
            vector=np.exp(-2j*np.pi*np.arange(segment//2+1)[:,None]*np.arange(segment)[None,:]/segment)*window
            vector-=vector.mean(axis=1,keepdims=True)
            expected=np.zeros_like(correction)
            for start in range(0,count-segment+1,hop):
                block=raw[start:start+segment,start:start+segment]
                expected+=np.einsum('ft,fu,tuij->fij',vector.conj(),vector,block)/sum(window**2)
            expected/=segments
            expected[1:-1 if segment%2==0 else None]*=2
            assert_allclose(stationary+correction,expected,rtol=1e-12,atol=1e-14)
            centered=np.einsum('ttij->ij',raw)/count-raw.sum(axis=(0,1))/count**2
            assert_allclose(covariance+cov_correction,centered,rtol=1e-12,atol=1e-14)

    def test_stationary_initial_law_has_zero_correction(self):
        f,p,_,_,o=self.fixture()
        s,c,m=corrections(f,np.zeros_like(p),o,101,7,7,3)
        assert_allclose(s,0,atol=0);assert_allclose(c,0,atol=0)
        self.assertEqual(m,32)

    def test_deterministic_transient_matches_scipy_exactly(self):
        f,_,_,mean,o=self.fixture()
        count=41;burn=4
        states=np.array([o@np.linalg.matrix_power(f,t)@mean for t in range(burn,burn+count)])
        for segment in [5,6]:
            s,c,_=corrections(f,np.outer(mean,mean),o,count,burn,segment,2)
            for i in range(2):
                for j in range(2):
                    _,actual=csd(states[:,i],states[:,j],fs=1,nperseg=segment,
                                 noverlap=segment-2,detrend='constant',window='hann')
                    assert_allclose(s[:,i,j],actual,rtol=2e-12,atol=1e-16)
            assert_allclose(c,np.cov(states.T,bias=True),rtol=2e-12,atol=1e-16)

    def test_independent_gaussian_draws_match_noncentral_means(self):
        f,p,initial,mean,o=self.fixture()
        count=17;burn=2;segment=6;hop=3
        # Assemble covariance directly, then draw the entire record at once.
        cov=self.dense(f,p,initial-p,o,count,burn)
        matrix=cov.transpose(0,2,1,3).reshape(2*count,2*count)
        means=np.array([o@np.linalg.matrix_power(f,burn+t)@mean for t in range(count)])
        rng=np.random.default_rng(718103)
        draws=(rng.normal(size=(60000,2*count))@np.linalg.cholesky(matrix).T).reshape(-1,count,2)+means
        lags=lag_covariances(f,p,count,observed=2)
        observed=np.einsum('ai,tij,bj->tab',o,lags,o)
        s,c,_=corrections(f,initial-p+np.outer(mean,mean),o,count,burn,segment,hop)
        expected=expected_spectra(observed,segment)+s
        for i in range(2):
            for j in range(2):
                _,actual=csd(draws[:,:,i],draws[:,:,j],fs=1,nperseg=segment,
                             noverlap=segment-hop,axis=1)
                assert_allclose(actual.mean(axis=0),expected[:,i,j],rtol=.025,atol=.002)
        centered=draws-draws.mean(axis=1,keepdims=True)
        empirical=np.einsum('nti,ntj->ij',centered,centered)/(len(draws)*count)
        assert_allclose(empirical,centered_moments(observed)[0]+c,rtol=.02,atol=.002)

    def test_invalid_inputs_fail(self):
        with self.assertRaises(ValueError):
            finite_sums(np.eye(2),np.array([[1.,1.],[0.,1.]]),3)
        for n in [-1,2.5,True]:
            with self.assertRaises(ValueError):finite_sums(np.eye(2),np.eye(2),n)
        for kwargs in [dict(count=3),dict(count=40,burn=-1),dict(count=40,hop=0),dict(count=40,hop=31)]:
            with self.assertRaises(ValueError):corrections(np.eye(2),np.eye(2),np.eye(2),**kwargs)


if __name__=='__main__':
    unittest.main()
