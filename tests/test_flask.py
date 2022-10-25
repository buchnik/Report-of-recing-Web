import pytest
from githab.report_flask import *


class TestReportFlask:

    def setup(self):
        app.testing = True
        self.client = app.test_client()

    @pytest.mark.parametrize('args, expected_result', [
        ('/', 200),
        ('/report/', 200),
        ('/report/drivers/', 200),
        ('/report/?order=desc', 200),
        ('/report/?order=asc', 200),
        ('/report/?order=', 400),
        ('/report/?order=sd', 404),
        ('/report/drivers/?driver_id=SVF', 200),
        ('/report/drivers/?driver_id=dfg', 404),
        ('/report/drivers/?driver_id=', 400)
    ])
    def test_report_flask(self, args, expected_result):
        response = self.client.get(args)
        assert response.status_code == expected_result

    @pytest.mark.parametrize('args, expected_result', [
        ({'order': 'desc'}, True),
        ({'sadg': ''}, False)
    ])
    def test_validate_request(self, args, expected_result):
        result = validate_request(args)
        assert result == expected_result

    def test_report(self):
        res = self.client.get('/report/drivers/')
        assert 'SVF' in res.data.decode()
