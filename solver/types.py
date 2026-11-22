"""
Hợp đồng dữ liệu giữa web và solver
"""
from dataclasses import dataclass, field
from typing import Literal

PermitStatus = Literal["granted", "denied"] #Trạng thái Chấp nhận/Từ chối đăng ký

@dataclass
class StageSummary:
    name: str
    status: str
    value: int
    bound: int
    seconds: int


@dataclass
class SolveConfig:
    total_time_limit: float = 600.0
    fairness_share: float = 0.5
    length_share: float = 0.5
    base: int = 64
    random_max_weight: int = 1000
    num_workers: int = 0

    def __post_init__(self):
        if self.total_time_limit <= 0:
            raise ValueError("total_time_limit must be > 0")
        for name in ("fairness_share", "length_share"):
            if not 0.0 < getattr(self, name) <= 1.0:
                raise ValueError(f"{name} must be in (0, 1]")
        if self.base < 2:
            raise ValueError("base must be >= 2")
        if self.random_max_weight < 1:
            raise ValueError("random_max_weight must be >= 1")
        if self.num_workers < 0:
            raise ValueError("num_workers must be >= 0")

@dataclass(frozen=True)
class Block:
    """
    Một Block bao gồm các Sessions liền nhau mà sinh viên muốn đi xe máy
    `sessions` là các session_id liền nhau trong cùng một ngày
    Block không được đăng ký sẽ đi xe máy không được đưa vào solver
    """

    block_id: str
    student_id: str
    sessions: tuple[str, ...]

    def __post_init__(self) -> None:
        """ Đảm bảo loại trường hợp block chứa 0 session nào """
        if not self.sessions:
            raise ValueError(f"Block {self.block_id} has no sessions")

    @property
    def length(self) -> int:
        return len(self.sessions)

@dataclass(frozen=True)
class SolveInput:
    blocks: tuple[Block, ...]
    capacity: int  # sức chứa bãi đỗ
    seed: int = 0
    
    def __post_init__(self):
        if self.capacity < 0:
            raise ValueError("Capacity must be >= 0")
        block_ids = [block.block_id for block in self.blocks]
        if len(block_ids) != len(set(block_ids)):
            raise ValueError("There are duplicate blocks") 

@dataclass
class SolveResult:
    status: dict[str, PermitStatus]  # Gán cho từng block_id là granted / denied
    granted_per_student: dict[str, int]  # Số lượng block đã granted cho mỗi SV
    occupancy: dict[str, int]  # Với mỗi session_id, lấy số xe hiện có trong bãi
    fairness_levels: list[int] = field(default_factory=list) # fairness_levels[j-1] = số sinh viên đạt mức j ở tầng công bằng
    stages: list[StageSummary] = field(default_factory=list)
    proven_prefix: int = 0
    levels_total: int = 0
    deviation: tuple[int, int] | None = None
    all_optimal: bool = False
    total_seconds: float = 0.0

###
def validate(inp: SolveInput) -> None:
    """Kiểm tra đầu vào, báo lỗi sớm thay vì để solver trả kết quả sai."""
    if inp.capacity < 0:
        raise ValueError("capacity phải >= 0")
    ids = [b.block_id for b in inp.blocks]
    if len(ids) != len(set(ids)):
        raise ValueError("block_id bị trùng")