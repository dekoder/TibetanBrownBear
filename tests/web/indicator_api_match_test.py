"""Tests for the Indicator matching API."""

import json

import pytest

@pytest.mark.usefixtures('clean_db', 'populate_all')
def test_yara_rule_match(authenticated_client):
    json_data = [{'encoding': 'b64', 'data': 'TVoAAAA='}]
    rv = authenticated_client.post('/api/indicators/match/',
                                   data=json.dumps(json_data),
                                   content_type='application/json')
    response = json.loads(rv.data)
    assert rv.status_code == 200
    assert len(response) == 1
    assert response[0]['name'] == 'MZ'

@pytest.mark.usefixtures('clean_db', 'populate_all')
def test_regex_match(authenticated_client):
    json_data = [{
        'encoding': 'utf-8',
        'data': 'http://malicious.com/gate.php'
    }]
    rv = authenticated_client.post('/api/indicators/match/',
                                   data=json.dumps(json_data),
                                   content_type='application/json')
    response = json.loads(rv.data)
    assert rv.status_code == 200
    assert len(response) == 1
    assert response[0]['name'] == 'Zeus C2'
