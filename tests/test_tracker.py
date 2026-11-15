import time
import pytest
from models.tracker import TimeTracker


@pytest.fixture
def tracker(tmp_path):
    test_file = tmp_path / "test_stats.json"
    return TimeTracker(str(test_file))


def test_start_and_stop(tracker):
    tracker.start(guild_id=100, user_id=1)
    time.sleep(1.1)
    elapsed = tracker.stop(guild_id=100, user_id=1)
    assert elapsed >= 1, f"Ожидалась минимум 1 сек, получено {elapsed}"


def test_channel_switch_does_not_reset_timer(tracker):
    tracker.start(guild_id=100, user_id=2)
    time.sleep(1.1)
    tracker.start(guild_id=100, user_id=2)
    time.sleep(1.1)
    elapsed = tracker.stop(guild_id=100, user_id=2)
    assert elapsed >= 2, f"Таймер сбросился! Получено {elapsed} сек вместо >= 2"


def test_stop_inactive_user(tracker):
    assert tracker.stop(guild_id=100, user_id=999) == 0


def test_json_persistence_live_stats_and_top(tmp_path):
    test_file = tmp_path / "test_stats.json"
    tracker = TimeTracker(str(test_file))

    tracker.start(guild_id=100, user_id=1)
    time.sleep(1.1)
    tracker.stop(guild_id=100, user_id=1)

    tracker.start(guild_id=100, user_id=2)
    time.sleep(2.1)
    tracker.stop(guild_id=100, user_id=2)

    reloaded_tracker = TimeTracker(str(test_file))
    user1_stats = reloaded_tracker.data["100"]["1"]
    assert user1_stats["total_seconds"] >= 1
    assert user1_stats["sessions"] == 1

    reloaded_tracker.start(guild_id=100, user_id=1)
    time.sleep(1.1)
    assert reloaded_tracker.get_user_seconds(guild_id=100, user_id=1) >= 2

    time.sleep(1.1)
    top_list = reloaded_tracker.get_top(guild_id=100, limit=10)
    assert top_list[0][0] == 1
    assert top_list[1][0] == 2
