"""
Hợp đồng dữ liệu giữa web và solver
"""
from dataclasses import dataclass

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
            raise ValueError(f"Block {self.block_id} không có session nào")

    @property
    def length(self) -> int:
        return len(self.sessions)