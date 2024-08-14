from typing import Any
from fastapi import APIRouter
from fastapi import BackgroundTasks
from app.services.transfer import Transfer
from redis import Redis

router = APIRouter()


def restore(source, destination):
    t = Transfer(source, destination, 'redis')
    t.download()
    t.upload()


@router.post("/")
def create_restore(
    source: str, destination: str, bg_tasks: BackgroundTasks
) -> Any:
    """
    Create new Restore.
    """
    bg_tasks.add_task(restore, source, destination)

    return 'restore_id: 1frqFtyhjt'


@router.get("/")
def get_restore(restore_id: str):
    r = Redis('redis', 6379, encoding='utf-8')

    data = {
        'restore_id': restore_id,
        'direction': str(r.get('direction')),
        'transferred_bytes': str(r.get('transferred_bytes')),
        'percent': str(r.get('percent')) + '%',
        'transfer_speed': str(r.get('transfer_speed')),
        'transfer_speed_unit': str(r.get('transfer_speed_unit')),
        'time': str(r.get('time')),
        'is_completed_stats': str(r.get('is_completed_stats'))
    }

    return data
