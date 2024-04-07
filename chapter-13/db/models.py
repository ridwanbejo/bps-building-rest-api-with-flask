import bcrypt

from sqlmodel import Field, Session, SQLModel, create_engine, select


sqlite_file_name = "database.db"  
sqlite_url = f"sqlite:///{sqlite_file_name}"  

engine = create_engine(sqlite_url, echo=True)
salt = b'$2b$12$D9r4ccjlTutS2DK5i074Be'


class Users(SQLModel, table=True):
	id: int | None = Field(default=None, primary_key=True)
	username: str
	email: str
	password: str
	is_active: bool = Field(default=True)


def hash_password(password, salt):
	plain_text_bytes = password.encode('utf-8')
	hashed_password = bcrypt.hashpw(plain_text_bytes, salt)

	return hashed_password.decode('utf-8')


def create_db_and_tables():  
    SQLModel.metadata.create_all(engine)  


def create_sample_users():
	user_1 = Users(username="john.doe", email="john.doe123@gmail.com", password=hash_password("secret12345", salt))
	user_2 = Users(username="charlie.frank", email="charlie.frank345@gmail.com", password=hash_password("secret12345", salt))

	with Session(engine) as session:
		existing_user_1 = get_user_by_username(session, user_1.username)
		if existing_user_1 is None:
			session.add(user_1)

		existing_user_2 = get_user_by_username(session, user_2.username)
		if existing_user_2 is None:
			session.add(user_2)

		session.commit()


def get_user_by_username(session, username):
	statement = select(Users).where(Users.username == username)
	results = session.exec(statement)
	temp_user = results.one()

	return temp_user


def get_user_by_id(session, id):
	statement = select(Users).where(Users.id == id)
	results = session.exec(statement)
	temp_user = results.one()

	return temp_user


def get_user_by_credential(session, username, password):
	statement = select(Users).where(Users.username == username).where(Users.password == hash_password(password, salt))
	results = session.exec(statement)
	temp_user = results.one()

	return temp_user


def get_user_by_email_and_password(session, email, password):
	statement = select(Users).where(Users.email == email).where(Users.password == hash_password(password, salt))
	results = session.exec(statement)
	temp_user = results.one()

	return temp_user


def create_user(session, username, email, password):
	user = Users(username=username, email=email, password=hash_password(password, salt))
	existing_user = get_user_by_username(session, user.username) 
	if existing_user is None:
		session.add(user)
		session.commit()

		return user
	else:
		return None


def change_password(session, id, email, password):
	user = get_user_by_id(session, id)

	if user is None:
		return None
	else:
		user.password = hash_password(password, salt)
		session.add(user)
		session.commit()
		session.refresh(user)

		return user


if __name__ == "__main__":
    create_db_and_tables()
    create_sample_users()
