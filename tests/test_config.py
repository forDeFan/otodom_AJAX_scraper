from unittest.mock import patch

import pytest

from config.config_handler import ParametersHandler


class TestConfig:
    @patch("yaml.safe_load")
    def test_if_exception_when_no_param_file_present(
        self, mock_safe_load
    ):
        mock_safe_load.return_value = None

        with pytest.raises(ValueError):
            ParametersHandler()
            assert True

    @patch("yaml.safe_load")
    def test_if_params_returned(self, mock_safe_load):
        mock_safe_load.return_value = "value"

        assert "value" in ParametersHandler().get_params()
