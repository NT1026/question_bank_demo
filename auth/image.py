from itsdangerous import URLSafeTimedSerializer

from settings.configs import Settings

settings = Settings()
serializer = URLSafeTimedSerializer(
    settings.IMAGE_SECRET_KEY,
    salt="image-salt",
)


def generate_image_token(user_id: str, question_id: str):
    return serializer.dumps({"user_id": user_id, "question_id": question_id})
