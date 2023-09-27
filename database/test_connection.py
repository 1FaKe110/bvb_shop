import psycopg2

conn = psycopg2.connect("""
    host=rc1b-n347sd0msta4wqdq.mdb.yandexcloud.net
    port=6432
    sslmode=verify-full
    dbname=bvb_shop
    user=admin_bvb
    password=admin_bvb
    target_session_attrs=read-write
""")

q = conn.cursor()
q.execute('SELECT * from products')

print(q.fetchone())

conn.close()