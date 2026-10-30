"""
Hợp đồng dữ liệu giữa web và solver
"""
from dataclasses import dataclass, field
from typing import Literal

PermitStatus = Literal["granted", "denied"] #Trạng thái Chấp nhận/Từ chối đăng ký


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
    # fairness_levels[j-1] = số sinh viên đạt mức j ở tầng công bằng
    fairness_levels: list[int] = field(default_factory=list)

###
def validate(inp: SolveInput) -> None:
    """Kiểm tra đầu vào, báo lỗi sớm thay vì để bộ giải trả kết quả sai."""
    if inp.capacity < 0:
        raise ValueError("capacity phải >= 0")
    ids = [b.block_id for b in inp.blocks]
    if len(ids) != len(set(ids)):
        raise ValueError("block_id bị trùng")