"""
Hợp đồng dữ liệu giữa web và solver.
"""
from dataclasses import dataclass, field
from typing import Literal

PermitStatus = Literal["granted", "denied"]

@dataclass(frozen=True)
class Block:
    """Một Block bao gồm các Sessions liền nhau mà sinh viên muốn đi xe máy.

    `sessions` là các session_id liền nhau trong cùng một ngày.
    Block có phiếu "không đi xe máy" không được đưa vào solver.
    """

    block_id: str
    student_id: str
    sessions_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.sessions:
            raise ValueError(f"Block {self.block_id} không có session nào")

    @property
    def length(self) -> int:
        return len(self.sessions)


@dataclass(frozen=True)
class SolveInput:
    blocks: tuple[Block, ...]
    capacity: int  # C: một con số cho cả học kỳ
    seed: int = 0  # hạt giống cho tầng ngẫu nhiên
    # Số block đã được duyệt sẵn của mỗi sinh viên (dùng cho phần mở rộng đổi sức chứa)
    base_counts: dict[str, int] = field(default_factory=dict)


@dataclass
class SolveResult:
    status: dict[str, PermitStatus]  # block_id -> granted / denied
    granted_per_student: dict[str, int]  # student_id -> n_i
    occupancy: dict[str, int]  # session_id -> số xe trong bãi
    # fairness_levels[j-1] = số sinh viên đạt mức j ở tầng công bằng
    fairness_levels: list[int] = field(default_factory=list)


def validate(inp: SolveInput) -> None:
    """Kiểm tra đầu vào, báo lỗi sớm thay vì để bộ giải trả kết quả sai."""
    if inp.capacity < 0:
        raise ValueError("capacity phải >= 0")
    ids = [b.block_id for b in inp.blocks]
    if len(ids) != len(set(ids)):
        raise ValueError("block_id bị trùng")