from part2.app.models.basemodel import BaseModel


class Review(BaseModel):
    def __init__(self, text, rating, place, user):
        super().__init__()

        if not text:
            raise ValueError("Review text is required.")
        if not (1 <= rating <= 5):
            raise ValueError("Rating must be between 1 and 5.")

        self.text = text
        self.rating = rating
        self.place = place  # يجب أن يكون كائن من نوع Place
        self.user = user    # يجب أن يكون كائن من نوع User
