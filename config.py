
DATABASE = {
    'host': 'localhost',
    'port': '5432',
    'database': 'TeacherStudent',
    'user': 'postgres',
    'password': '123'
}

class Config:
    SQLALCHEMY_DATABASE_URI = f"postgresql+pg8000://{DATABASE['user']}:{DATABASE['password']}@{DATABASE['host']}:{DATABASE['port']}/{DATABASE['database']}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
