from sqlmodel import SQLModel


class UserCreate(SQLModel):
	username: str
	email: str
	password: str
	confirm_password: str


class UserResetPassword(SQLModel):
	id: int
	email: str
	password: str


class UserChangePassword(SQLModel):
	email: str
	current_password: str
	new_password: str
	confirm_new_password: str
