import json
import time
from pathlib import Path


class TimeTracker:
    def __init__(self, filepath: str = "data/stats.json"):
        self.filepath = Path(filepath)
        self.active_sessions: dict[tuple[int, int], float] = {}
        self.data: dict = self._load()

    def _load(self) -> dict:
        if not self.filepath.exists():
            return {}
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def _save(self) -> None:
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def start(self, guild_id: int, user_id: int) -> None:
        key = (guild_id, user_id)
        if key not in self.active_sessions:
            self.active_sessions[key] = time.time()

    def stop(self, guild_id: int, user_id: int) -> int:
        key = (guild_id, user_id)
        start_time = self.active_sessions.pop(key, None)

        if start_time is None:
            return 0

        elapsed = int(time.time() - start_time)
        if elapsed <= 0:
            return 0

        g_id, u_id = str(guild_id), str(user_id)
        self.data.setdefault(g_id, {})
        self.data[g_id].setdefault(u_id, {"total_seconds": 0, "sessions": 0})

        self.data[g_id][u_id]["total_seconds"] += elapsed
        self.data[g_id][u_id]["sessions"] += 1
        self._save()

        return elapsed

    def get_user_seconds(self, guild_id: int, user_id: int) -> int:
        g_id, u_id = str(guild_id), str(user_id)
        saved = self.data.get(g_id, {}).get(u_id, {}).get("total_seconds", 0)

        current_start = self.active_sessions.get((guild_id, user_id))
        active = int(time.time() - current_start) if current_start else 0

        return saved + active

    def get_top(self, guild_id: int, limit: int = 10) -> list[tuple[int, int]]:
        g_id = str(guild_id)
        users_time: dict[int, int] = {}

        for u_id_str, info in self.data.get(g_id, {}).items():
            users_time[int(u_id_str)] = info.get("total_seconds", 0)

        now = time.time()
        for (active_g_id, active_u_id), start_time in self.active_sessions.items():
            if active_g_id == guild_id:
                users_time[active_u_id] = users_time.get(active_u_id, 0) + int(now - start_time)

        sorted_users = sorted(users_time.items(), key=lambda x: x[1], reverse=True)
        return sorted_users[:limit]
