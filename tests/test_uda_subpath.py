"""UDA-prefix and LAN regression using the isolated test database."""
def test_uda_mount_and_lan(client):
    local = client.get("/model-manual")
    assert local.status_code == 200
    assert '<base href="/">' in local.get_data(as_text=True)
    headers = {
        "X-Forwarded-Prefix": "/apps/lucky-lab",
        "X-Forwarded-Host": "tanyaanne.ddns.net",
        "X-Forwarded-Proto": "https",
    }
    prefixed = client.get("/", headers=headers)
    assert prefixed.status_code == 200
    html = prefixed.get_data(as_text=True)
    assert '<base href="/apps/lucky-lab/">' in html
    assert '/apps/lucky-lab/static/js/app.js' in html
