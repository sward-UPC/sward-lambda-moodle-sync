"""Tests unitarios para sward-lambda-moodle-sync.

Trigger: EventBridge schedule → POST /lms/sync
"""
import json
from unittest.mock import MagicMock, patch

import pytest

from handler import handle_schedule


class TestMoodleSyncHandler:
    """Tests para el handler de sincronización Moodle."""

    @patch("handler.urllib.request.urlopen")
    def test_sync_exitoso(self, mock_urlopen):
        """Test happy path: EventBridge schedule válido, POST /lms/sync exitoso."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"registros_procesados": 42, "cursos": 3}'
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = handle_schedule({}, None)
        assert result["statusCode"] == 200
        assert result["body"]["registros_procesados"] == 42
        mock_urlopen.assert_called_once()

    @patch("handler.urllib.request.urlopen")
    def test_sync_error_http(self, mock_urlopen):
        """Test edge case: HTTP error desde /lms/sync (500, 400, etc.)."""
        import urllib.error

        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="http://test",
            code=500,
            msg="Internal Server Error",
            hdrs=None,
            fp=MagicMock(read=lambda: b'{"error": "server error"}'),
        )
        with pytest.raises(RuntimeError, match="Sync falló"):
            handle_schedule({}, None)

    @patch("handler.urllib.request.urlopen")
    def test_sync_error_conexion(self, mock_urlopen):
        """Test edge case: Error de conexión al ms-integracion-lms (URLError)."""
        import urllib.error

        mock_urlopen.side_effect = urllib.error.URLError(reason="Connection refused")
        with pytest.raises(RuntimeError, match="No se pudo conectar"):
            handle_schedule({}, None)

    @patch("handler.urllib.request.urlopen")
    def test_sync_malformed_response(self, mock_urlopen):
        """Test edge case: respuesta no es JSON válido."""
        mock_response = MagicMock()
        mock_response.read.return_value = b"not valid json at all"
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        with pytest.raises(json.JSONDecodeError):
            handle_schedule({}, None)
