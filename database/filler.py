from loguru import logger
import database


class DbFiller(database.Database):
    def __init__(self):
        super().__init__()

    @logger.catch
    def create(self):
        logger.debug('Creating table: categories')
        # Создание таблицы категорий товаров, если она не существует
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_id TEXT DEFAULT ('Сантехника'),
                name TEXT,
                image_path TEXT DEFAULT ('../static/images/categories/categories-blank.png')
        )''')
        self.__commit__()
        logger.debug('Creating table: dollar')
        # Создание таблицы категорий товаров, если она не существует
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS dollar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                price float DEFAULT (80)
        )''')
        self.__commit__()
        logger.debug('Creating table: products')
        self.cur.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    by_price FLOAT DEFAULT (10),
                    price FLOAT DEFAULT (NULL),
                    amount INT NOT NULL DEFAULT (10),
                    brand TEXT NOT NULL,
                    price_dependency BOOL DEFAULT (false), 
                    category_id INTEGER NOT NULL,
                    image_id INTEGER,
                    description TEXT NOT NULL DEFAULT ('тут какое-то описание'),
                    image_path TEXT NOT NULL DEFAULT ('../static/images/products/products-blank.png')
                )
            ''')
        self.__commit__()
        self.cur.execute('''
                CREATE TRIGGER set_price_value
                AFTER INSERT ON products
                FOR EACH ROW
                WHEN NEW.price IS NULL
                BEGIN
                  UPDATE products
                  SET price = (NEW.by_price * (select price from dollar) * 0.5)
                  WHERE NEW.id = NEW.rowid;
                END;
            ''')
        self.__commit__()
        logger.debug('Creating table: images')
        self.cur.execute('''
                CREATE TABLE IF NOT EXISTS images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price FLOAT NOT NULL,
                    category_id INTEGER NOT NULL,
                    tags TEXT,
                    description TEXT NOT NULL DEFAULT "тут какое-то описание",
                    image_path TEXT NOT NULL DEFAULT "../static/images/products/"
                )
            ''')
        self.__commit__()
        logger.debug('Creating table: brands')
        self.cur.execute('''
                CREATE TABLE IF NOT EXISTS brands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    tags TEXT,
                    description TEXT NOT NULL DEFAULT "тут какое-то описание",
                    image_path TEXT NOT NULL DEFAULT "../static/images/products/"
                )
            ''')
        self.__commit__()
        logger.debug('Creating table: orders')
        self.cur.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    status_id INTEGER NOT NULL,
                    position_id INTEGER NOT NULL,
                    amount INTEGER NOT NULL,
                    address TEXT NOT NULL,
                    datetime DATETIME NOT NULL
                )
            ''')
        self.__commit__()
        logger.debug('Creating table: users')
        self.cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    email TEXT,
                    password TEXT,
                    is_admin BOOL DEFAULT False,
                    is_registered BOOL DEFAULT False
                )
            ''')
        self.__commit__()

    @logger.catch
    def fill(self):
        logger.debug('Filling table: categories')
        # Добавление примера данных категорий (можно заменить на вашу базу данных)
        self.cur.execute(
            "INSERT INTO categories (name, parent_id, image_path) VALUES ('Сантехника', NULL, '../static/images/categories/plumbing.jpg');")
        self.cur.execute(
            "INSERT INTO categories (name, parent_id, image_path) VALUES ('Электрика', NULL, '../static/images/categories/Electrics.jpg');")
        self.cur.execute(
            "INSERT INTO categories (name, parent_id, image_path) values ('Краны', 1, 'https://png.pngtree.com/png-clipart/20200701/original/pngtree-water-pipe-switch-faucet-png-image_5410968.jpg');")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Насосы', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Аквасторож', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Американки', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Баки', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Клапаны', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Вентиляторы', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Защита от протечек', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Гофры', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Шланги', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Гильзы', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Заглушки', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Картриджи', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Манжеты', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Манометры', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Насадки', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Ниппеля', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Каналы', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Переходники', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Подводка', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Муфты', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Мультифлексы', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Утеплители', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Удлинители', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Колени', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Коллектора', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Шкафы для коллекторов', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Гайки', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Резьбы', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Редукторы', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Шумоизоляция', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Цанги', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Хомута', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Футорки', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Фильтры', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Трубы', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Трапы', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Углы', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Эксцентрик', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Смесители', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Решетки', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Радиаторы', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Груши', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Арматуры', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Гребенки', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Пена паста смазка', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Обвязки', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Крепежи', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Крестовины', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Люки', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Штуцера', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Терморегуляторы', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Термометры', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Термоголовки', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Теплоносители', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Счетчики', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Держатели', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Диэлектрики', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Колбы', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Скотч и клей', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Тросы', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Соль', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Фланец', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Ленты', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Шины', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Компенсаторы', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Клипсы', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Инсталяции для унитаза', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Наклейки', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Шпильки', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Сливы', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Силикон', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Планки', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Теплый пол', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Нити', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Втулки', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Врезки', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Коллекторная группа', 1);")
        self.cur.execute("INSERT INTO categories (name, parent_id) values ('Остальные', 1);")
        self.__commit__()

        parent_id = self.cur.execute("SELECT id from categories where name = 'Краны'").fetchone()['id']
        self.cur.execute(f"INSERT INTO categories (name, parent_id) values ('C носиком', '{parent_id}');")
        self.cur.execute(f"INSERT INTO categories (name, parent_id) values ('Угловой', '{parent_id}');")
        self.cur.execute(f"INSERT INTO categories (name, parent_id) values ('Краны Ф', '{parent_id}');")
        self.cur.execute(f"INSERT INTO categories (name, parent_id) values ('Букса', '{parent_id}');")
        self.cur.execute(f"INSERT INTO categories (name, parent_id) values ('Мини', '{parent_id}');")
        self.cur.execute(f"INSERT INTO categories (name, parent_id) values ('Радиаторный', '{parent_id}');")
        self.__commit__()

        category_id = self.cur.execute(
            f"SELECT id FROM categories WHERE parent_id='{parent_id}' and name='C носиком'").fetchone()['id']

        logger.debug(f'Filling table: products with cat_id = {category_id}')

        self.cur.execute(f"INSERT INTO products (name, price, price_dependency, brand, category_id, image_path) "
                         f"VALUES ('Кран с носиком 1\\2', 300.0, true, 'sololift', {category_id},"
                         f" 'https://santexkom.ru/upload/iblock/ac8/ac88967bf614c62b5afc9ecebd6b727b.jpg')")
        self.__commit__()
        self.cur.execute(f"INSERT INTO products (name, price, brand, category_id) "
                         f"VALUES ('Кран с носиком 3\\4', 300.0, 'sololift', {category_id})")
        self.__commit__()

        self.__commit__()
        category_id = self.cur.execute(
            f"SELECT id FROM categories WHERE parent_id='{parent_id}' and name='Угловой'").fetchone()['id']
        self.cur.execute(
            f"INSERT INTO products (name, price, price_dependency, brand, category_id) VALUES "
            f"('Кран угловой 1\\2х1\\2', 16.0, true, 'tim', {category_id})")
        self.cur.execute(
            f"INSERT INTO products (name, price, brand, category_id) VALUES ('Кран угловой 1\\2х3\\4', 3500.0, 'tim', {category_id})")
        self.cur.execute(
            f"INSERT INTO products (name, price, brand, category_id) VALUES ('Кран угловой 1\\2х3\\8', 3500.0, 'tim', {category_id})")
        self.cur.execute(
            f"INSERT INTO products (name, price, brand, category_id) VALUES ('Кран угловой 1\\2х3\\4', 3500.0, 'гг', {category_id})")
        self.__commit__()


    @logger.catch
    def drop(self):
        logger.debug('Drop all tables')
        self.cur.execute("DROP TABLE IF EXISTS brands;")
        self.cur.execute("DROP TABLE IF EXISTS categories;")
        self.cur.execute("DROP TABLE IF EXISTS category_matrix;")
        self.cur.execute("DROP TABLE IF EXISTS images;")
        self.cur.execute("DROP TABLE IF EXISTS orders;")
        self.cur.execute("DROP TABLE IF EXISTS products;")
        self.cur.execute("DROP TABLE IF EXISTS users;")
        self.__commit__()


@logger.catch
def reset_database():
    DbFiller().drop()
    DbFiller().create()
    DbFiller().fill()


if __name__ == '__main__':
    reset_database()
