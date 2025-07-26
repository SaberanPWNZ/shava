from decimal import Decimal

REVIEW_SCORE_CHOICES = [
    (Decimal("1.0"), "1 - Very Poor"),
    (Decimal("2.0"), "2 - Poor"),
    (Decimal("3.0"), "3 - Below Average"),
    (Decimal("4.0"), "4 - Fair"),
    (Decimal("5.0"), "5 - Average"),
    (Decimal("6.0"), "6 - Above Average"),
    (Decimal("7.0"), "7 - Good"),
    (Decimal("8.0"), "8 - Very Good"),
    (Decimal("9.0"), "9 - Excellent"),
    (Decimal("10.0"), "10 - Outstanding"),
]
