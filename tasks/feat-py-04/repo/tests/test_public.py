import unittest

from src.clock import ManualClock
from src.limiter import TokenLimiter
from src.models import RateLimitPolicy


class TestPublic(unittest.TestCase):
    def test_policy_and_clock_validation(self):
        clock = ManualClock(10.0)
        self.assertEqual(clock.now(), 10.0)
        self.assertEqual(clock.advance(2.5), 12.5)
        with self.assertRaises(ValueError):
            clock.advance(-1.0)
        with self.assertRaises(ValueError):
            RateLimitPolicy(rate=-1.0, capacity=5.0)
        with self.assertRaises(ValueError):
            RateLimitPolicy(rate=1.0, capacity=0.0)

    def test_single_thread_basic_try_acquire(self):
        clock = ManualClock(0.0)
        limiter = TokenLimiter(RateLimitPolicy(rate=2.0, capacity=3.0), clock=clock)
        self.assertTrue(limiter.try_acquire("api-a", 2))
        self.assertTrue(limiter.try_acquire("api-a", 1))
        self.assertFalse(limiter.try_acquire("api-a", 1))
        clock.advance(1.0)
        self.assertTrue(limiter.try_acquire("api-a", 2))
        st = limiter.stats("api-a")
        self.assertIsNotNone(st)
        self.assertEqual(st.allowed_requests, 3)
        self.assertEqual(st.allowed_tokens, 5)
        self.assertEqual(st.rejected_requests, 1)


if __name__ == "__main__":
    unittest.main()
