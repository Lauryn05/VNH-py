import pytest
from manager import app as manager_app
from client import app as client_app

@pytest.fixture
def manager():
    manager_app.config['TESTING'] = True
    yield manager_app.test_client()

@pytest.fixture
def client():
    client_app.config['TESTING'] = True
    yield client_app.test_client()

def test_get_devices(manager):
    response = manager.get('/api/device')
    assert response.status_code == 200

def test_add_device(manager):
    response = manager.post('/api/device', json={'name': 'Device1', 'ip': '192.168.1.1', 'community': 'public', 'version': '2c'})
    assert response.status_code == 200

def test_receive_trap(client):
    response = client.post('/api/trap', json={'oid': '1.3.6.1.2.1.1.1', 'value': 'New device added'})
    assert response.status_code == 200
