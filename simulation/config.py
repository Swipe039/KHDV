"""
Các tham số mặc định cho việc sinh dataset giả lập
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class SimulationConfig:
    days: tuple[str, ...] = ("T2", "T3", "T4", "T5", "T6", "T7")
    sessions_per_day: int = 4
    motorbike_usage_rate: float = 0.8 #Tỉ lệ số SV sử dụng xe máy trên tổng số SV
    register_rate: float = 0.95 #Tỉ lệ SV sẽ đăng ký đi xe máy vào 1 block
    days_weights_distribution: tuple[int, ...] = (2, 5, 25, 32, 28, 8) #Trọng số số ngày học của SV trong tuần
    sparse_rate: float = 0.15 #Tỉ lệ SV dky học các ca rời nhau trong 1 ngày

    def __post_init__(self):
        for name in ("motorbike_usage_rate", "register_rate", "sparse_rate"):
            value = getattr(self, name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be in [0, 1]")
        if len(self.days_weights_distribution) != len(self.days):
            raise ValueError("days_weights_distribution needs one weight per day")
        if any(weight < 0 for weight in self.days_weights_distribution):
            raise ValueError("days_weights_distribution must be >= 0")
        if sum(self.days_weights_distribution) <= 0:
            raise ValueError("days_weights_distribution must have a positive sum")
        if self.sessions_per_day < 1:
            raise ValueError("sessions_per_day must be >= 1")
        if self.sparse_rate > 0 and self.sessions_per_day < 3:
            raise ValueError("sparse_rate > 0 requires sessions_per_day >= 3")