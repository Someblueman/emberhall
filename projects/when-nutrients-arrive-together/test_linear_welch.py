import unittest
import numpy as np
from numpy.testing import assert_allclose
from scipy.signal import welch
from linear_welch import expected_spectra, predictions


class ExpectedWelchChecks(unittest.TestCase):
    def test_white_noise_exact_window_detrend_normalization(self):
        for segment in (16,30,60):
            lags=np.zeros((segment,2,2)); lags[0]=[[1,.4],[.4,1]]
            s=expected_spectra(lags,segment)
            expected=np.full(segment//2+1,2.); expected[0]=1/3; expected[1]=5/3; expected[-1]=1
            assert_allclose(s[:,0,0].real,expected,atol=1e-13)
            assert_allclose(np.abs(s[:,0,1])**2/(s[:,0,0]*s[:,1,1]),.16,atol=1e-13)

    def test_expected_periodogram_against_independent_sampling(self):
        rng=np.random.default_rng(781)
        # Independent 30-sample records; average SciPy's actual periodograms.
        x=rng.normal(size=(40000,30))
        _,observed=welch(x, nperseg=30,noverlap=0,axis=1,window='hann',detrend='constant')
        lags=np.zeros((30,1,1)); lags[0]=1
        assert_allclose(observed.mean(0),expected_spectra(lags,30)[:,0,0].real,rtol=.02)

    def test_source_reconstruction_prediction_remains_bounded(self):
        for metric,scores in predictions(4)['scores'].items():
            for target,value in scores.items():
                self.assertTrue(np.isfinite(value))
                self.assertLessEqual(value,1)
                self.assertGreaterEqual(value,-1 if target=='overlap_spearman' else 0)


class ColoredExpectedWelchChecks(unittest.TestCase):
    def test_delayed_colored_filter_matches_complex_expected_cross_spectrum(self):
        from scipy.linalg import solve_discrete_lyapunov
        from scipy.signal import lfilter, csd
        rng=np.random.default_rng(1952)
        innovations=rng.normal(size=(501000,2))
        first=lfilter([1],[1,-.8],innovations[:,0])
        other=lfilter([1],[1,-.4],innovations[:,1])
        second=.5*np.roll(first,2)+other
        first=first[1000:]; second=second[1000:]
        # Independently derived delay-line state (x_t,x_(t-1),x_(t-2),z_t).
        transition=np.array([[.8,0,0,0],[1,0,0,0],[0,1,0,0],[0,0,0,.4]])
        p=solve_discrete_lyapunov(transition,np.diag([1,0,0,1]))
        observation=np.array([[1,0,0,0],[0,0,.5,1]])
        lags=np.array([observation@np.linalg.matrix_power(transition,lag)@p@observation.T
                       for lag in range(30)])
        expected=expected_spectra(lags,30)
        _,cross=csd(first,second,nperseg=30,noverlap=15,window='hann',detrend='constant')
        _,auto0=welch(first,nperseg=30,noverlap=15,window='hann',detrend='constant')
        _,auto1=welch(second,nperseg=30,noverlap=15,window='hann',detrend='constant')
        scale=np.sqrt(expected[:,0,0].real*expected[:,1,1].real)
        self.assertLess(np.max(np.abs(cross-expected[:,0,1])/scale),.035)
        assert_allclose(auto0,expected[:,0,0].real,rtol=.035)
        assert_allclose(auto1,expected[:,1,1].real,rtol=.035)
