"""Tests for the Gradio app module."""

from unittest.mock import Mock, patch

import pytest

from tapio.app import TapioAssistantApp, main


@pytest.fixture
def test_app(mock_rag_orchestrator):
    """Create TapioAssistantApp with mocked RAG orchestrator."""
    return TapioAssistantApp(rag_orchestrator=mock_rag_orchestrator)


class TestGradioApp:
    """Tests for the Gradio app module."""

    def test_generate_rag_response(self, test_app):
        """Test generating a RAG response."""
        test_app.rag_orchestrator.query.return_value = (
            "Test response",
            ["doc1", "doc2"],
        )
        test_app.rag_orchestrator.format_documents_for_display.return_value = "Formatted docs"

        # Call the method
        response, formatted_docs = test_app.generate_rag_response("test query")

        # Assertions
        test_app.rag_orchestrator.query.assert_called_once_with(
            query_text="test query",
            history=None,
        )
        test_app.rag_orchestrator.format_documents_for_display.assert_called_once_with(
            [
                "doc1",
                "doc2",
            ],
        )
        assert response == "Test response"
        assert formatted_docs == "Formatted docs"

    def test_generate_rag_response_with_error(self, test_app):
        """Test error handling in generate_rag_response."""
        # Setup
        test_app.rag_orchestrator.query.side_effect = Exception("Test error")

        # Call the method
        response, formatted_docs = test_app.generate_rag_response("test query")

        # Assertions
        assert "error" in response.lower()
        assert "Error retrieving" in formatted_docs

    @patch("tapio.app.TapioAssistantApp")
    def test_main_function(self, mock_app_class, mock_rag_orchestrator):
        """Test the main function that launches the Gradio app."""
        # Setup
        mock_app_instance = Mock()
        mock_app_class.return_value = mock_app_instance
        mock_app_instance.check_model_availability.return_value = True

        # Call the function
        main(rag_orchestrator=mock_rag_orchestrator, share=True)

        # Assertions
        mock_app_class.assert_called_once_with(rag_orchestrator=mock_rag_orchestrator)
        mock_app_instance.check_model_availability.assert_called_once()
        mock_app_instance.launch.assert_called_once_with(share=True)

    @patch("tapio.app.TapioAssistantApp")
    def test_main_function_model_unavailable(self, mock_app_class, mock_rag_orchestrator):
        """Test the main function when the model is unavailable."""
        # Setup
        mock_app_instance = Mock()
        mock_app_class.return_value = mock_app_instance
        mock_app_instance.check_model_availability.return_value = False

        # Call the function
        main(rag_orchestrator=mock_rag_orchestrator)

        # Assertions
        mock_app_instance.check_model_availability.assert_called_once()
        # Even with model unavailable, the app should launch
        mock_app_instance.launch.assert_called_once()

