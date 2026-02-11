
from sqlalchemy.orm import Session
from app.models.user import User as UserModel
from app.schemas.user import User as UserSchema

class UserService:
    @staticmethod
    def get_user_by_id(db: Session, user_id: str):
        return db.query(UserModel).filter(UserModel.id == user_id).first()

    @staticmethod
    def update_user_profile(db: Session, user_id: str, email: str, full_name: str, institution: str, role: str = "authenticated"):
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            user = UserModel(id=user_id, email=email, full_name=full_name, institution=institution, role=role)
            db.add(user)
        else:
            user.email = email
            user.full_name = full_name
            user.institution = institution
            user.role = role
        db.commit()
        db.refresh(user)
        return user
