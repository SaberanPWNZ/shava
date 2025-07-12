import logging
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

logger = logging.getLogger("news")

# Create your views here.


class NewsViewSet(viewsets.ViewSet):
    """
    Приклад ViewSet з логуванням для новин
    """

    def list(self, request):
        """Отримати список новин"""
        logger.info("User %s requested news list", request.user)
        try:
            logger.debug("Fetching news from database")
            return Response({"message": "News list"}, status=status.HTTP_200_OK)
        except ValueError as e:
            logger.error("Validation error fetching news: %s", str(e), exc_info=True)
            return Response(
                {"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error("Unexpected error fetching news: %s", str(e), exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def create(self, request):
        """Створити нову новину"""
        logger.info("User %s creating new news item", request.user)
        try:
            logger.debug("Creating news with data: %s", request.data)
            logger.info("News item created successfully")
            return Response({"message": "News created"}, status=status.HTTP_201_CREATED)
        except ValueError as e:
            logger.error("Validation error creating news: %s", str(e), exc_info=True)
            return Response(
                {"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error("Unexpected error creating news: %s", str(e), exc_info=True)
            return Response(
                {"error": "Failed to create news"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def featured(self, request):
        """Отримати рекомендовані новини"""
        logger.info("User %s fetching featured news", request.user)
        try:
            # Логіка для рекомендованих новин
            logger.debug("Processing featured news request")
            return Response({"message": "Featured news"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Error fetching featured news: %s", str(e), exc_info=True)
            return Response(
                {"error": "Failed to fetch featured news"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
