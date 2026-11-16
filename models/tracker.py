import json
import time
from pathlib import Path


class TimeTracker:
    def __init__(self, filepath: str = "data/stats.json"):
        self.filepath = Path(filepath)
        self.active_sessions: dict[tuple[int, int], tuple[float, int]] = {}
        self.data: dict = self.load()

    def load(self) -> dict:
        if not self.filepath.exists():
            return {}
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def save(self) -> None:
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def ensure_user(self, g_id: str, u_id: str) -> None:
        self.data.setdefault(g_id, {})
        self.data[g_id].setdefault(u_id, {"total_seconds": 0, "sessions": 0, "duos": {}})
        self.data[g_id][u_id].setdefault("duos", {})

    def start(self, guild_id: int, user_id: int, channel_id: int = 0) -> None:
        key = (guild_id, user_id)
        if key not in self.active_sessions:
            self.active_sessions[key] = (time.time(), channel_id)
        else:
            start_time, _ = self.active_sessions[key]
            self.active_sessions[key] = (start_time, channel_id)

    def stop(self, guild_id: int, user_id: int) -> int:
        key = (guild_id, user_id)
        session = self.active_sessions.pop(key, None)

        if session is None:
            return 0

        start_time, channel_id = session
        now = time.time()
        elapsed = int(now - start_time)
        if elapsed <= 0:
            return 0

        g_id, u_id = str(guild_id), str(user_id)
        self.ensure_user(g_id, u_id)

        self.data[g_id][u_id]["total_seconds"] += elapsed
        self.data[g_id][u_id]["sessions"] += 1

        if channel_id != 0:
            for (active_g_id, other_u_id), (other_start, other_ch_id) in self.active_sessions.items():
                if active_g_id == guild_id and other_ch_id == channel_id:
                    overlap_start = max(start_time, other_start)
                    overlap = int(now - overlap_start)
                    if overlap > 0:
                        other_id_str = str(other_u_id)
                        self.ensure_user(g_id, other_id_str)
                        self.data[g_id][u_id]["duos"][other_id_str] = (
                            self.data[g_id][u_id]["duos"].get(other_id_str, 0) + overlap
                        )
                        self.data[g_id][other_id_str]["duos"][u_id] = (
                            self.data[g_id][other_id_str]["duos"].get(u_id, 0) + overlap
                        )

        self.save()
        return elapsed

    def get_user_seconds(self, guild_id: int, user_id: int) -> int:
        g_id, u_id = str(guild_id), str(user_id)
        saved = self.data.get(g_id, {}).get(u_id, {}).get("total_seconds", 0)

        session = self.active_sessions.get((guild_id, user_id))
        active = int(time.time() - session[0]) if session else 0

        return saved + active

    def get_duo_seconds(self, guild_id: int, user1_id: int, user2_id: int) -> int:
        if user1_id == user2_id:
            return 0

        g_id = str(guild_id)
        u1_id, u2_id = str(user1_id), str(user2_id)
        saved = self.data.get(g_id, {}).get(u1_id, {}).get("duos", {}).get(u2_id, 0)

        s1 = self.active_sessions.get((guild_id, user1_id))
        s2 = self.active_sessions.get((guild_id, user2_id))
        active = 0
        if s1 and s2 and s1[1] != 0 and s1[1] == s2[1]:
            overlap_start = max(s1[0], s2[0])
            active = max(0, int(time.time() - overlap_start))

        return saved + active

    def get_top(self, guild_id: int, limit: int = 10) -> list[tuple[int, int]]:
        g_id = str(guild_id)
        users_time: dict[int, int] = {}

        for u_id_str, info in self.data.get(g_id, {}).items():
            users_time[int(u_id_str)] = info.get("total_seconds", 0)

        now = time.time()
        for (active_g_id, active_u_id), (start_time, _) in self.active_sessions.items():
            if active_g_id == guild_id:
                users_time[active_u_id] = users_time.get(active_u_id, 0) + int(now - start_time)

        sorted_users = sorted(users_time.items(), key=lambda x: x[1], reverse=True)
        return sorted_users[:limit]
