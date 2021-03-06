from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from loguru import logger

from sqlalchemy_views import CreateView
import config

# DB接続するためのEngineインスタンス
engine = create_engine(config.database_host, echo=True)

# DBに対してORM操作するときに利用
# Sessionを通じて操作を行う
session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

# 各modelで利用
# classとDBをMapping
Base = declarative_base()

# ログ
logger.remove()
logger.add(config.log, rotation="1 day", retention=30, compression="zip")

# View追加 TODO: View作成は別ファイルに分離したい。
insp = inspect(engine)
if not insp.has_table("members_date_total_enter_seconds"):
    view = Table('members_date_total_enter_seconds', MetaData())
    definition = text(
        "SELECT "
        "member_id, "
        "date, "
        "sum(channel_enter_seconds) as total_second "
        "from time_records "
        "group by member_id, date"
    )
    create_view = CreateView(view, definition)
    print(str(create_view.compile()).strip())
    engine.execute(create_view)

if not insp.has_table("members_week_total_enter_seconds"):
    view = Table('members_week_total_enter_seconds', MetaData())
    definition = text(
        "SELECT "
        "member_id, "
        "strftime('%Y-%W weeks', date) as week, "
        "sum(total_second) as total_second "
        "FROM members_date_total_enter_seconds "
        "GROUP BY member_id, week"
    )
    create_view = CreateView(view, definition)
    print(str(create_view.compile()).strip())
    engine.execute(create_view)
