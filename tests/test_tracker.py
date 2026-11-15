import time
from pathlib import Path
from models.tracker import TimeTracker

BASE_DIR = Path(__file__).resolve().parent.parent
TEST_FILE = BASE_DIR / "data" / "test_stats.json"


def run_tests():
    TEST_FILE.unlink(missing_ok=True)

    tracker = TimeTracker(str(TEST_FILE))

    # имитация входа в ГС(start) ждёт 1.1 сек и выходит(stop)
    tracker.start(guild_id=100, user_id=1)
    time.sleep(1.1)
    elapsed = tracker.stop(guild_id=100, user_id=1)
    assert elapsed >= 1, f"Ожидалась минимум 1 сек, получено {elapsed}"

    # переключение между ГСами, тут проверка что start вызывается повторно при перезаходе
    tracker.start(guild_id=100, user_id=2)
    time.sleep(1.1)
    tracker.start(guild_id=100, user_id=2)
    time.sleep(1.1)
    elapsed_2 = tracker.stop(guild_id=100, user_id=2)
    assert elapsed_2 >= 2, f"Таймер сбросился! Получено {elapsed_2} сек вместо >= 2"

    # остановка таймера если человека нет в ГСах
    assert tracker.stop(guild_id=100, user_id=999) == 0

    # проверка сохранения в json
    reloaded_tracker = TimeTracker(str(TEST_FILE))
    user1_stats = reloaded_tracker.data["100"]["1"]
    assert user1_stats["total_seconds"] >= 1
    assert user1_stats["sessions"] == 1

    # проверка живой статы (сохраненное + то, что тикает прямо сейчас)
    reloaded_tracker.start(guild_id=100, user_id=1)
    time.sleep(1.1)
    assert reloaded_tracker.get_user_seconds(guild_id=100, user_id=1) >= 2

    # проверка топа (юзер 1 сидит дольше юзера 2, должен быть на 1 месте)
    time.sleep(1.1)
    top_list = reloaded_tracker.get_top(guild_id=100, limit=10)
    assert top_list[0][0] == 1
    assert top_list[1][0] == 2

    TEST_FILE.unlink(missing_ok=True)
    print("тесты models/tracker.py пройдены")


if __name__ == "__main__":
    run_tests()
