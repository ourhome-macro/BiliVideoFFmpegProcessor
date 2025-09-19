from typing import Any, List, Optional
class Result:
    success: bool
    message: Optional[str]=None
    data: Any 
    total: Optional[int]=None

    def __init__(self,success:bool,message:Optional[str]=None,data:Any=None,total:Optional[int]=None):
        self.success=success
        self.message=message
        self.data=data
        self.total=total

    @classmethod
    def ok():
        return Result(True)
    
    @classmethod
    def ok(data: Any):
        return Result(True,data=data)

    @classmethod
    def ok(data: List[Any], total: int):
        return Result(True, data=data, total=total)
    
    @classmethod
    def error(msg: str):
        return Result(False, message=msg)

    def to_dict(self) -> dict:
        return {
            'success': self.success,
            'message': self.message,
            'data': self.data,
            'total': self.total
        }