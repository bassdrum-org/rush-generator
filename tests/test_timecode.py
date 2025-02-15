import unittest
from src.timecode import format_seconds, TimeConstants

class TestTimecode(unittest.TestCase):
    def test_format_seconds_zero(self):
        """0秒のフォーマットテスト"""
        self.assertEqual(format_seconds(0), "00:00:00")

    def test_format_seconds_single_digits(self):
        """1桁の数値のフォーマットテスト"""
        self.assertEqual(format_seconds(5), "00:00:05")
        self.assertEqual(format_seconds(45), "00:00:45")

    def test_format_seconds_minutes(self):
        """分を含む時間のフォーマットテスト"""
        self.assertEqual(format_seconds(60), "00:01:00")
        self.assertEqual(format_seconds(75), "00:01:15")
        self.assertEqual(format_seconds(3599), "00:59:59")

    def test_format_seconds_hours(self):
        """時間を含む時間のフォーマットテスト"""
        self.assertEqual(format_seconds(3600), "01:00:00")
        self.assertEqual(format_seconds(3661), "01:01:01")
        self.assertEqual(format_seconds(7200), "02:00:00")

    def test_format_seconds_large_values(self):
        """大きな値のフォーマットテスト"""
        # 10時間
        self.assertEqual(format_seconds(36000), "10:00:00")
        # 23時間59分59秒
        self.assertEqual(format_seconds(86399), "23:59:59")
        # 24時間
        self.assertEqual(format_seconds(86400), "24:00:00")

    def test_format_seconds_with_constants(self):
        """TimeConstantsを使用した値のフォーマットテスト"""
        one_hour = TimeConstants.SECONDS_PER_HOUR
        one_minute = TimeConstants.SECONDS_PER_MINUTE
        
        self.assertEqual(format_seconds(one_hour), "01:00:00")
        self.assertEqual(format_seconds(one_minute), "00:01:00")
        self.assertEqual(
            format_seconds(2 * one_hour + 30 * one_minute + 15),
            "02:30:15"
        )

if __name__ == '__main__':
    unittest.main()