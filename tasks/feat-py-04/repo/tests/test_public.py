"""潮汐令牌桶的可见测试。"""

import unittest

from src.clock import ManualClock
from src.limiter import TokenLimiter
from src.models import RateLimitPolicy


class TestPublic(unittest.TestCase):
    def test_manual_clock(self):
        clock = ManualClock(2)
        self.assertEqual(clock.now(), 2.0)
        clock.advance(1.5)
        self.assertEqual(clock.now(), 3.5)
        clock.set(0)
        self.assertEqual(clock.now(), 0.0)
        with self.assertRaises(ValueError):
            clock.advance(-1)
        with self.assertRaises(ValueError):
            clock.advance(True)

    def test_policy_rejects_bool_and_rate(self):
        with self.assertRaises(ValueError):
            RateLimitPolicy(True, 1)
        with self.assertRaises(ValueError):
            RateLimitPolicy(1, -0.1)
        with self.assertRaises(ValueError):
            RateLimitPolicy(1, True)
        with self.assertRaises(ValueError):
            RateLimitPolicy(1, 1, freeze_after=False)

    def test_policy_burst_mismatch(self):
        policy = RateLimitPolicy(4, 1, burst=4)
        self.assertEqual(policy.capacity, 4)
        with self.assertRaises(ValueError):
            RateLimitPolicy(4, 1, burst=3)

    def test_empty_stats(self):
        limiter = TokenLimiter(RateLimitPolicy(2, 0), ManualClock())
        self.assertIsNone(limiter.stats("missing"))
        self.assertEqual(limiter.all_stats(), {})

    def test_bad_key(self):
        limiter = TokenLimiter(RateLimitPolicy(2, 0), ManualClock())
        with self.assertRaises(ValueError):
            limiter.try_acquire("", 1)
        with self.assertRaises(ValueError):
            limiter.try_acquire(1, 1)

    def test_bad_tokens(self):
        limiter = TokenLimiter(RateLimitPolicy(2, 0), ManualClock())
        with self.assertRaises(ValueError):
            limiter.try_acquire("gate", True)
        with self.assertRaises(ValueError):
            limiter.try_acquire("gate", 0)
        with self.assertRaises(ValueError):
            limiter.try_acquire("gate", 3)
        self.assertIsNone(limiter.stats("gate"))

    def test_timeout_type(self):
        limiter = TokenLimiter(RateLimitPolicy(2, 0), ManualClock())
        with self.assertRaises(ValueError):
            limiter.acquire("gate", 1, timeout=True)
        with self.assertRaises(ValueError):
            limiter.acquire("gate", 1, timeout=-0.1)

    def test_basic_consume(self):
        limiter = TokenLimiter(RateLimitPolicy(2, 0), ManualClock())
        self.assertTrue(limiter.try_acquire("gate", 1))
        self.assertTrue(limiter.try_acquire("gate", 1))
        self.assertFalse(limiter.try_acquire("gate", 1))
        snap = limiter.stats("gate")
        self.assertEqual(snap.allowed_requests, 2)
        self.assertEqual(snap.rejected_requests, 1)


if __name__ == "__main__":
    unittest.main()
