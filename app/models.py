from app import db
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from app import login
from sqlalchemy.sql import func
class User(UserMixin,db.Model):
    id:so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64),unique=True)
    email: so.Mapped[str] =so.mapped_column(sa.String(128))
    pwd: so.Mapped[str] =so.mapped_column(sa.String(256))
    admin: so.Mapped[str] = so.mapped_column(sa.String(64),default='user')
    datejoined = db.Column(sa.DateTime(timezone=True), server_default=func.now())
    cart_items: so.WriteOnlyMapped['Cart_Items'] = so.relationship(back_populates='author',primaryjoin="User.id == Cart_Items.user_id",passive_deletes=True)
    @login.user_loader
    def load_user(id):
        return db.session.get(User,int(id))
    def __repr__(self) -> str:
        return '<User {}>'.format(self.username)
class Cart_Items(db.Model):
    id:so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str]=so.mapped_column(sa.String(128))
    quantity: so.Mapped[int] = so.mapped_column()
    price:so.Mapped[int]=so.mapped_column()
    description: so.Mapped[str] = so.mapped_column(sa.String(256))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author:so.Mapped[User] = so.relationship(back_populates='cart_items')
    def __repr__(self) -> str:
        return '<Cart_Items {}>'.format(self.name)
class Products(db.Model):
    id:so.Mapped[int] = so.mapped_column(primary_key=True)
    name:so.Mapped[str] = so.mapped_column(sa.String(100))
    category:so.Mapped[str] = so.mapped_column(sa.String(256))
    description:so.Mapped[str] = so.mapped_column(sa.String(256))
    price: so.Mapped[int] = so.mapped_column()
    def __repr__(self) -> str:
        return '<Products {}>'.format(self.name)
class Liked(db.Model):
    id:so.Mapped[int] = so.mapped_column(primary_key=True)
    username:so.Mapped[str] = so.mapped_column(sa.String(100))
    liked_pname:so.Mapped[str] = so.mapped_column(sa.String(100))
    def _repr_(self) -> str:
        return '<Liked {}>'.format(self.name)
class Carted(db.Model):
    id:so.Mapped[int] = so.mapped_column(primary_key=True)
    username:so.Mapped[str] = so.mapped_column(sa.String(100))
    carted_pname:so.Mapped[str] = so.mapped_column(sa.String(100))
    def _repr_(self) -> str:
        return '<Recom {}>'.format(self.name)