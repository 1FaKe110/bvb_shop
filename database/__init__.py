import dataclasses
import sqlite3
import platform

from loguru import logger

match platform.system():
    case 'Ubuntu':
        cwd = '/home/ifake/BVB_SHOP_SITE'
    case 'Windows':
        cwd = r'C:\Users\iFaKe\Desktop\BVB_SHOP_SITE'
    case _:
        raise SystemExit(f"Unsupported os: {platform.system()}")


class Database:
    def __init__(self):
        self.__conn = sqlite3.connect(f'{cwd}/database.db', check_same_thread=False)
        self.__conn.row_factory = dict_factory
        self.cur = self.__conn.cursor()

    @logger.catch
    def __commit__(self):
        logger.trace('committed!')
        self.__conn.commit()

    @logger.catch
    def close(self) -> None:
        self.cur.close()
        self.__conn.close()
        return

    @logger.catch
    def exec(self, query: str, func: str | None = None):
        """
        :param query: str repr of sql syntax 
        :param func: fetchall | fetchone | None
        :return: None | Dict | List
        """
        logger.debug(f"Query: [{query}] | asserted to {func}")
        self.cur.execute(query)
        if not query.lower().startswith('select'):
            logger.trace("Query must be committed!")
            self.__commit__()
            return self.close()

        match func:
            case 'fetchall':
                reply = self.cur.fetchall()
                if reply is not None:
                    [logger.trace(row) for row in reply]
                else:
                    logger.debug(reply)
            case 'fetchone':
                reply = self.cur.fetchone()
                if reply is not None:
                    [logger.trace(row) for row in reply]
                else:
                    logger.debug(reply)
            case _:
                self.close()
                raise TypeError()

        self.close()
        return reply


@logger.catch
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@dataclasses.dataclass
class Queries:
    ...
