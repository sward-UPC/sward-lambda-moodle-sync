from unittest.mock import MagicMock, patch
import pytest
from handler import handle_schedule


@patch("handler.urllib.request.urlopen")
def test_sync_exitoso(mock_urlopen):
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"registros_procesados": 42, "cursos": 3}'
    mock_response.__enter__ = lambda s: s
    mock_response.__exit__ = MagicMock(return_value=False)
    mock_urlopen.return_value = mock_response

    result = handle_schedule({}, None)
    assert result["statusCode"] == 200
    assert result["body"]["registros_procesados"] == 42


@patch("handler.urllib.request.urlopen")
def test_sync_error_http(mock_urlopen):
    import urllib.error

    mock_urlopen.side_effect = urllib.error.HTTPError(
        url="http://test",
        code=500,
        msg="Internal Server Error",
        hdrs=None,
        fp=MagicMock(read=lambda: b"error"),
    )
    with pytest.raises(RuntimeError, match="Sync falló"):
        handle_schedule({}, None)


@patch("handler.urllib.request.urlopen")
def test_sync_error_conexion(mock_urlopen):
    import urllib.error

    mock_urlopen.side_effect = urllib.error.URLError(reason="Connection refused")
    with pytest.raises(RuntimeError, match="No se pudo conectar"):
        handle_schedule({}, None)
