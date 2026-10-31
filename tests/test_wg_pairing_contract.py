import base64, json, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parents[1]

def test_shared_wireguard_contract():
    c = json.loads((ROOT/'shared/routepou-wg-contract.json').read_text())
    assert c['protocolVersion'] == 1
    assert c['phoneTunnelAddress'] == '10.13.37.1/32'
    assert c['windowsTunnelAddress'] == '10.13.37.2/32'
    assert c['windowsAllowedIps'] == '0.0.0.0/0'
    assert c['mtu'] == 1420 and c['listenPort'] == 51820

def test_kotlin_pairing_contract_matches_shared_values():
    src = (ROOT/'android/app/src/main/java/com/pou/routepou/pairing/RoutePouWgConfig.kt').read_text()
    for value in ['10.13.37.1','10.13.37.2','1420','51820','0.0.0.0/0']:
        assert value in src

def test_qr_payload_is_versioned_and_secret_marked():
    src = (ROOT/'android/app/src/main/java/com/pou/routepou/pairing/RoutePouPairingPayload.kt').read_text()
    assert 'routepou://p/' in src
    assert 'clientPrivateKey' in src
    assert 'root.optInt("v") == 1' in src
    assert 'port in 1..65535' in src
