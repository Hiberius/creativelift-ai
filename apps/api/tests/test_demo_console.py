def test_demo_console_serves_one_click_product_surface(client):
    response = client.get("/demo")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "CreativeLift AI Measurement Lab" in response.text
    assert "/v1/demo/analyze" in response.text
    assert "/v1/demo/reports" in response.text
    assert "/v1/demo/reports/export?format=csv" in response.text
    assert "/v1/demo/reports/import" in response.text
    assert "/v1/demo/reports/summary" in response.text
    assert "/v1/demo/scenario" in response.text
    assert "Analyze numbers" in response.text
    assert "CSV Import" in response.text
    assert "Import CSV" in response.text
    assert "Save report" in response.text
    assert "Decision Log" in response.text
    assert "Avg lift" in response.text
    assert "Clear" in response.text
    assert "Run full scenario" in response.text
