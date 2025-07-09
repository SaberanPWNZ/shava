"""
Модуль для тестування логування в Django проекті Shava.

Цей файл демонструє правильне використання логування
в різних ситуаціях та з різними рівнями логування.
"""

import logging

# Отримуємо логер для цього модуля
logger = logging.getLogger("shava_project")


def test_logging():
    """Тестування різних рівнів логування"""

    # DEBUG - детальна інформація для діагностики
    logger.debug("Це DEBUG повідомлення - детальна інформація для розробки")

    # INFO - загальна інформація про роботу програми
    logger.info("Це INFO повідомлення - нормальна робота додатку")

    # WARNING - попередження про потенційні проблеми
    logger.warning("Це WARNING повідомлення - щось може працювати не оптимально")

    # ERROR - помилки, які не зупиняють роботу програми
    logger.error("Це ERROR повідомлення - сталася помилка")

    # CRITICAL - критичні помилки, які можуть зупинити програму
    logger.critical("Це CRITICAL повідомлення - критична помилка")


def test_logging_with_params():
    """Тестування логування з параметрами"""

    user_id = 123
    username = "test_user"
    operation = "create_shawarma"

    # Правильний спосіб логування з параметрами (lazy formatting)
    logger.info(
        "User %s (ID: %d) performed operation: %s", username, user_id, operation
    )

    # Логування з додатковою інформацією
    logger.debug("Operation details - user_id: %d, operation: %s", user_id, operation)


def test_exception_logging():
    """Тестування логування виключень"""

    try:
        # Симулюємо помилку
        result = 10 / 0
    except ZeroDivisionError as e:
        # Логування виключення з повною інформацією про стек
        logger.error("Division by zero error occurred: %s", str(e), exc_info=True)
    except Exception as e:
        # Загальне виключення (не рекомендується в реальному коді)
        logger.error("Unexpected error: %s", str(e), exc_info=True)


def test_structured_logging():
    """Тестування структурованого логування"""

    # Логування з додатковими атрибутами
    extra_data = {
        "user_id": 123,
        "request_id": "req-456",
        "action": "order_shawarma",
        "ip_address": "192.168.1.1",
    }

    logger.info("Order placed successfully", extra=extra_data)


class ShawarmaLogger:
    """Приклад класу з логуванням для шаурми"""

    def __init__(self):
        self.logger = logging.getLogger("shwarma")

    def create_shawarma(self, ingredients, customer_id):
        """Створення шаурми з логуванням"""
        self.logger.info("Creating shawarma for customer %d", customer_id)

        try:
            # Логування початку процесу
            self.logger.debug(
                "Starting shawarma preparation with ingredients: %s", ingredients
            )

            # Симулюємо процес створення
            if not ingredients:
                raise ValueError("No ingredients provided")

            # Логування успішного створення
            self.logger.info(
                "Shawarma created successfully for customer %d", customer_id
            )
            return {"status": "success", "shawarma_id": 789}

        except ValueError as e:
            self.logger.error("Validation error creating shawarma: %s", str(e))
            raise
        except Exception as e:
            self.logger.error(
                "Unexpected error creating shawarma: %s", str(e), exc_info=True
            )
            raise


# Функція для демонстрації роботи логування
if __name__ == "__main__":
    print("Тестування системи логування Shava Project")

    test_logging()
    print("\n" + "=" * 50 + "\n")

    test_logging_with_params()
    print("\n" + "=" * 50 + "\n")

    test_exception_logging()
    print("\n" + "=" * 50 + "\n")

    test_structured_logging()
    print("\n" + "=" * 50 + "\n")

    # Тест класу
    shawarma_logger = ShawarmaLogger()
    try:
        shawarma_logger.create_shawarma(["chicken", "vegetables", "sauce"], 123)
    except Exception:
        pass

    try:
        shawarma_logger.create_shawarma([], 456)  # Спричинить помилку
    except Exception:
        pass
