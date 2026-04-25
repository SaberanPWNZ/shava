"""Smoke tests for the OpenAPI schema (drf-spectacular)."""

from __future__ import annotations

from django.test import TestCase
from django.urls import reverse


class OpenAPISchemaTests(TestCase):
    """Verify the schema and UI endpoints are reachable."""

    def test_schema_endpoint_returns_openapi_yaml(self):
        url = reverse("schema")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        body = response.content.decode("utf-8", errors="replace")
        self.assertIn("openapi:", body)
        self.assertIn("Shava API", body)

    def test_swagger_ui_endpoint(self):
        url = reverse("swagger-ui")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_redoc_endpoint(self):
        url = reverse("redoc")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
