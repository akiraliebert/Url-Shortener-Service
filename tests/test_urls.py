import pytest

@pytest.mark.asyncio
async def test_create_short_url_success(client):
    response = await client.post("/api/shorten", json={"original_url": "https://example.com"})
    assert response.status_code == 200
    data = response.json()

    assert "short_code" in data
    assert data["original_url"].rstrip("/") == "https://example.com".rstrip("/")


@pytest.mark.asyncio
async def test_create_short_url_invalid(client):
    response = await client.post("/api/shorten", json={"original_url": "not-a-url"})
    # Проверяем, что вернулась ошибка
    assert response.status_code in [400, 422]
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_create_short_url_duplicate(client):
    url = "https://repeat.com"
    # Первый вызов
    response1 = await client.post("/api/shorten", json={"original_url": url})
    assert response1.status_code == 200
    short1 = response1.json()["short_code"]

    # Второй вызов с тем же URL
    response2 = await client.post("/api/shorten", json={"original_url": url})
    assert response2.status_code == 200
    short2 = response2.json()["short_code"]

    # Проверяем, что short_code одинаковый — ссылка не дублируется
    assert short1 == short2

@pytest.mark.asyncio
async def test_redirect_short_url(client):
    # Сначала создаём ссылку
    response = await client.post("/api/shorten", json={"original_url": "https://redirect.me"})
    data = response.json()
    short_code = data["short_code"]

    # Теперь пробуем перейти по short_code
    response = await client.get(f"/api/{short_code}", allow_redirects=False)

    # Проверяем, что возвращает redirect (обычно 307 или 302)
    assert response.status_code in [302, 307]
    assert "https://redirect.me" in response.headers["location"]

@pytest.mark.asyncio
async def test_get_url_stats(client):
    response = await client.post("/api/shorten", json={"original_url": "https://stats.test"})
    data = response.json()
    short_code = data["short_code"]

    response = await client.get(f"/api/stats/{short_code}")
    assert response.status_code == 200

    stats = response.json()
    assert "clicks" in stats
    assert "last_accessed" in stats

@pytest.mark.asyncio
async def test_delete_short_url_authorized(client, test_token):
    # Создаём ссылку
    response = await client.post("/api/shorten", json={"original_url": "https://delete.me"})
    data = response.json()
    short_code = data["short_code"]

    # Удаляем с авторизацией
    response = await client.delete(
        f"/api/{short_code}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200

    # Проверяем, что теперь ссылка больше не доступна
    response2 = await client.get(f"/{short_code}")
    assert response2.status_code == 404
