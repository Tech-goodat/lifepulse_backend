import random
from app import app
from models import db, UserModel, UserLog

# Quote pool 
QUOTES = [
    "Small steps every day lead to big results.",
    "Consistency beats motivation.",
    "Take care of your body. It’s the only place you have to live.",
    "Progress, not perfection.",
    "Discipline is self-respect in action.",
    "You survived 100% of your hardest days.",
    "A healthy mind lives in a healthy body.",
    "Focus on improvement, not comparison.",
    "Wellness is built daily, not occasionally.",
    "Your future depends on what you do today."
]

def get_random_quote():
    return random.choice(QUOTES)

def seed_logs():
    print("Seeding logs with quotes...")

 
    user = UserModel.query.first()

    if not user:
        user = UserModel(
            username="demo_user",
            email="demo@mail.com",
            password="1234"
        )
        db.session.add(user)
        db.session.commit()
        print(" Demo user created")

 
    for i in range(5):
        log = UserLog(
            hashtag=f"#day{i+1}",
            average_sleep=random.randint(5, 9),
            total_water_taken=random.randint(1, 4),
            total_exercise_time=random.randint(0, 2),
            total_meditation_time=random.randint(5, 30),
            low_moments="Felt tired but pushed through",
            cope_up="Went for a walk",
            quote_of_the_day=get_random_quote(),
            user=user
        )
        db.session.add(log)

    db.session.commit()
    print(" Logs seeded successfully")

if __name__ == "__main__":
    with app.app_context():
        seed_logs()