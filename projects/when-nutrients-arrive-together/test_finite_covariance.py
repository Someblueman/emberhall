import unittest
import numpy as np
from numpy.testing import assert_allclose
from finite_covariance import (lag_covariances, centered_moments,
    correlation_envelope, absolute_envelope, auc_envelope, score_envelopes,
    quadratic_operator_bounds, spearman_envelope)


class FiniteCovarianceChecks(unittest.TestCase):
    def test_iid_matches_wishart_with_estimated_mean(self):
        p=np.array([[2.,.4],[.4,1.]])
        n=17
        lags=np.zeros((n,2,2));lags[0]=p
        mean,var=centered_moments(lags)
        assert_allclose(mean,(n-1)*p/n,atol=1e-15)
        assert_allclose(var,(n-1)*(np.outer(np.diag(p),np.diag(p))+p*p)/n**2,atol=1e-15)

    def test_nonreversible_control_matches_dense_quadratic_forms(self):
        f=np.array([[.7,.3],[0,.4]])
        p=np.array([[1.,.2],[.2,2.]])
        n=11
        lags=lag_covariances(f,p,n,observed=2)
        mean,var=centered_moments(lags)
        blocks=[[np.array([[lags[a-b,i,j] if a>=b else lags[b-a,j,i]
                           for b in range(n)] for a in range(n)])
                 for j in range(2)] for i in range(2)]
        h=np.eye(n)-np.ones((n,n))/n
        for i in range(2):
            for j in range(2):
                assert_allclose(mean[i,j],np.trace(h@blocks[i][j])/n,atol=1e-14)
                expected=(np.trace(h@blocks[i][i]@h@blocks[j][j])+
                          np.trace(h@blocks[i][j]@h@blocks[i][j]))/n**2
                assert_allclose(var[i,j],expected,atol=1e-14)
        # A transpose error at positive lags must be detectable by this control.
        self.assertGreater(abs(lags[1,0,1]-lags[1,1,0]),.1)

    def test_independent_gaussian_monte_carlo_moments(self):
        f=np.array([[.7,.3],[0,.4]])
        p=np.array([[1.,.2],[.2,2.]])
        n=9
        lags=lag_covariances(f,p,n,observed=2)
        mean,var=centered_moments(lags)
        # Dense joint Gaussian draws, independent of the state-space sampler.
        cov=np.block([[lags[a-b] if a>=b else lags[b-a].T
                       for b in range(n)] for a in range(n)])
        rng=np.random.default_rng(70913)
        x=(rng.normal(size=(80000,2*n))@np.linalg.cholesky(cov).T).reshape(-1,n,2)
        x-=x.mean(axis=1,keepdims=True)
        sample=np.einsum('nti,ntj->nij',x,x)/n
        assert_allclose(sample.mean(axis=0),mean,atol=.008)
        assert_allclose(sample.var(axis=0),var,rtol=.025,atol=.001)

    def test_operator_bound_dominates_dense_gaussian_quadratic_spectrum(self):
        f=np.array([[.7,.3],[0,.4]])
        p=np.array([[1.,.2],[.2,2.]])
        n=11
        lags=lag_covariances(f,p,n,observed=2)
        cov=np.block([[lags[a-b] if a>=b else lags[b-a].T
                       for b in range(n)] for a in range(n)])
        factor=np.linalg.cholesky(cov)
        h=np.eye(n)-np.ones((n,n))/n
        bound=quadratic_operator_bounds(lags)
        mean,var=centered_moments(lags)
        for i in range(2):
            for j in range(2):
                weight=np.zeros((2,2))
                weight[i,j]+=.5;weight[j,i]+=.5
                a=np.kron(h,weight)/n
                eigenvalues=np.linalg.eigvalsh(factor.T@a@factor)
                self.assertLessEqual(max(abs(eigenvalues)),bound[i,j]+1e-14)
                assert_allclose(2*np.sum(eigenvalues**2),var[i,j],atol=1e-14)
                assert_allclose(eigenvalues.sum(),mean[i,j],atol=1e-14)
        lo,hi,_=correlation_envelope(p,mean,var,operator_bounds=bound)
        self.assertTrue(np.all(lo<=hi))

    def test_envelopes_cover_extreme_covariances_and_monotone_closure(self):
        population=np.eye(6);population[0,1]=population[1,0]=.3
        mean=population.copy();var=np.full((6,6),1e-7)
        lower,upper,radius=correlation_envelope(population,mean,var)
        rng=np.random.default_rng(132)
        for _ in range(100):
            delta=rng.uniform(-1,1,(6,6))*radius
            sample=population+(delta+delta.T)/2
            rho=sample/np.sqrt(np.outer(np.diag(sample),np.diag(sample)))
            values=rho[np.triu_indices(6,1)]
            self.assertTrue(np.all(values>=lower))
            self.assertTrue(np.all(values<=upper))
        lo,hi=absolute_envelope(np.array([-.2,.1,-.9]),np.array([.3,.5,-.4]))
        assert_allclose(lo,[0,.1,.4]);assert_allclose(hi,[.3,.5,.9])
        labels=np.repeat([0,1],3)
        from reference import auc,single_linkage_scores,PAIRS
        same=(labels[:,None]==labels)[PAIRS]
        result=score_envelopes(labels,lower,upper)
        for _ in range(100):
            values=rng.uniform(lower,upper)
            for target,score in [('same_diet_pair_auc',values),
                                 ('single_linkage_guild_auc',single_linkage_scores(values))]:
                a,b=result[target]
                self.assertLessEqual(a,auc(same,score))
                self.assertGreaterEqual(b,auc(same,score))

    def test_vacuous_and_exact_tie_bounds(self):
        p=np.eye(2)
        lo,hi,_=correlation_envelope(p,p,np.ones((2,2)))
        assert_allclose(lo,[-1]);assert_allclose(hi,[1])
        self.assertEqual(auc_envelope([True,False],np.zeros(2),np.zeros(2)),[.5,.5])
        with self.assertRaises(ValueError):
            correlation_envelope(p,p,p,alpha=0)

    def test_rank_assignment_contains_all_small_permutations(self):
        from itertools import permutations
        from scipy.stats import spearmanr
        target=np.array([1,1,2,4,3])  # overlap ties are permitted
        lower=np.array([0.,.1,.4,.3,.7])
        upper=np.array([.2,.5,.8,.6,1.])
        bound=spearman_envelope(target,lower,upper)
        checked=0
        for ordering in permutations(range(5)):
            # Construct an ordered set of distinct values inside the intervals.
            values=np.empty(5);previous=-np.inf
            for index in ordering:
                values[index]=max(lower[index],previous+1e-5)
                previous=values[index]
            if np.any(values>upper):continue
            checked+=1
            rho=spearmanr(values,target).statistic
            self.assertLessEqual(bound[0]-1e-14,rho)
            self.assertGreaterEqual(bound[1]+1e-14,rho)
        self.assertGreater(checked,1)
        exact=spearman_envelope(target,np.arange(5.),np.arange(5.))
        assert_allclose(exact,[spearmanr(np.arange(5),target).statistic]*2,atol=1e-14)
