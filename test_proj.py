import pytest
from pricing import OptionsPricer

def test_black():
    option = OptionsPricer(100, 105, 0.23, 0.05, 365, 100)
    assert option.black() == pytest.approx((9.210534, 9.089624))
    
    option = OptionsPricer(93, 105, 0.23, 0.05, 365, 100)
    assert option.black() == pytest.approx((5.809494, 12.688584))
    
def test_binomial():
    
    option = OptionsPricer(100, 105, 0.23, 0.05, 365, 100)
    assert option.binomial() == pytest.approx((9.195929, 9.075019))
    
    option = OptionsPricer(93, 105, 0.23, 0.05, 365, 100)
    assert option.binomial() == pytest.approx((5.822846, 12.701935))
    
def test_montecarlo():
    
    option = OptionsPricer(100, 105, 0.23, 0.05, 365, 100)
    assert option.montecarlo() == pytest.approx((8, 8), abs = 5)
    
    
