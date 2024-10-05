from common import get_logger

from sqlalchemy import create_engine
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Session
from sqlalchemy import select, delete

import os


class Base(DeclarativeBase):
    pass

class GlobalSettings(Base):
    __tablename__ = "global_settings"
    id: Mapped[int] = mapped_column(primary_key=True)
    current_handler: Mapped[str] = mapped_column(String(256))

    def __repr__(self) -> str:
        return f"GlobalSettings(id={self.id!r}, current_handler={self.current_handler!r}"

class HandlerReferences(Base):
    __tablename__ = "handler_references"
    id: Mapped[int] = mapped_column(primary_key=True)
    handler: Mapped[str] = mapped_column(String(256))
    ref: Mapped[str] = mapped_column(String(256))
    value: Mapped[str] = mapped_column(String(4096))

    def __repr__(self) -> str:
        return f"HandlerReferences(id={self.id!r}, handler={self.handler!r}, ref={self.ref!r}, value={self.value!r})"


class HandlerFixes(Base):
    __tablename__ = "handler_fixes"
    id: Mapped[int] = mapped_column(primary_key=True)
    handler: Mapped[str] = mapped_column(String(256))
    type: Mapped[str] = mapped_column(String(256))
    value: Mapped[str] = mapped_column(String(4096))

    def __repr__(self) -> str:
        return f"HandlerFixes(id={self.id!r}, handler={self.handler!r}, type={self.type!r}, value={self.value!r})"


class BotDB(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._setup()
        return cls._instance

    def _setup(self):
        DB_PATH = "db"
        self._logger = get_logger("BOT-DB")
        if not os.path.exists(DB_PATH):
            os.makedirs(DB_PATH)
            self._logger.info(f"Folder '{DB_PATH}' created successfully.")
        self._engine = create_engine("sqlite:///{}/bot.db".format(DB_PATH), echo=False)
        Base.metadata.create_all(self._engine)
        self._logger.info("Database setup complete.")

    def create_or_update_global_handler(self, handler_key):
        with Session(self._engine) as session:
            stmt = (select(GlobalSettings)
                    .where(GlobalSettings.id.is_(1))
                    )
            target = None
            for handlerRefs in session.scalars(stmt):
                target = handlerRefs
            if target is None:
                target = GlobalSettings(id=1, current_handler=handler_key)
            target.current_handler = handler_key
            session.add_all([target])
            session.commit()
    def get_global_handle(self):
        result = []
        with Session(self._engine) as session:
            stmt = (select(GlobalSettings)
                    .where(GlobalSettings.id.is_(1))
                    )
            for handlerRefs in session.scalars(stmt):
                result.append(handlerRefs)
        if len(result) == 0:
            return "Txt2Img"
        return result[0].current_handler

    def create_or_update_handler_reference(self, handler_key, ref, value):
        with Session(self._engine) as session:
            stmt = (select(HandlerReferences)
                    .where(HandlerReferences.handler.is_(handler_key))
                    .where(HandlerReferences.ref.is_(ref))
                    )
            target = None
            for handlerRefs in session.scalars(stmt):
                target = handlerRefs
            if target is None:
                target = HandlerReferences(handler=handler_key, ref=ref, value=value)
            target.value = value
            session.add_all([target])
            session.commit()

    def get_all_handler_reference(self, handler_key):
        result = []
        with Session(self._engine) as session:
            stmt = (select(HandlerReferences)
                    .where(HandlerReferences.handler.is_(handler_key))
                    )
            for handlerRefs in session.scalars(stmt):
                result.append(handlerRefs)
        return result

    def remove_handler_reference(self, handler_key, ref):
        with Session(self._engine) as session:
            stmt = (delete(HandlerReferences)
                    .where(HandlerReferences.handler.is_(handler_key))
                    .where(HandlerReferences.ref.is_(ref))
                    )
            session.execute(stmt)
            session.commit()

    def remove_all_handler_reference(self, handler_key):
        with Session(self._engine) as session:
            stmt = (delete(HandlerReferences)
                    .where(HandlerReferences.handler.is_(handler_key))
                    )
            session.execute(stmt)
            session.commit()

    def create_or_update_handler_fixes(self, handler_key, type, value):
        with Session(self._engine) as session:
            stmt = (select(HandlerFixes)
                    .where(HandlerFixes.handler.is_(handler_key))
                    .where(HandlerFixes.type.is_(type))
                    )
            target = None
            for handlerFixes in session.scalars(stmt):
                target = handlerFixes
            if target is None:
                target = HandlerFixes(handler=handler_key, type=type, value=value)
            target.value = value
            session.add_all([target])
            session.commit()

    def get_all_handler_fixes(self, handler_key):
        result = []
        with Session(self._engine) as session:
            stmt = (select(HandlerFixes)
                    .where(HandlerFixes.handler.is_(handler_key))
                    )
            for handlerFixes in session.scalars(stmt):
                result.append(handlerFixes)
        return result

    def remove_handler_fixes_by_type(self, handler_key, type):
        with Session(self._engine) as session:
            stmt = (delete(HandlerFixes)
                    .where(HandlerFixes.handler.is_(handler_key))
                    .where(HandlerFixes.type.is_(type))
                    )
            session.execute(stmt)
            session.commit()

    def remove_all_handler_fixes(self, handler_key):
        with Session(self._engine) as session:
            stmt = (delete(HandlerFixes)
                    .where(HandlerFixes.handler.is_(handler_key))
                    )
            session.execute(stmt)
            session.commit()
