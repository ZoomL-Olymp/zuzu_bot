import pytest
import pandas as pd
from io import BytesIO
import os
import sqlite3
from unittest.mock import AsyncMock

from bot.handlers.basic import handle_document
from db.database import save_website_data, get_all_websites, init_db, DATABASE_NAME

# Fixture for the database
@pytest.fixture
def test_db():
    """Creates an in-memory database for testing."""
    conn = sqlite3.connect(DATABASE_NAME)  # Use the actual name for consistency
    init_db(conn)  # Initialize the schema

    # --- Pre-populate with some data for other tests ---
    data = [
        {'title': 'Test Site 1', 'url': 'https://example.com/1', 'xpath': '//div[@class="price1"]'},
        {'title': 'Test Site 2', 'url': 'https://example.com/2', 'xpath': '//span[@class="price2"]'}
    ]
    save_website_data(data, conn)

    yield conn  # Provide the connection to the tests

    conn.close()
    if os.path.exists(DATABASE_NAME): # added cleanup
        os.remove(DATABASE_NAME)


@pytest.fixture
def mock_message():
    """Creates a mock message object."""
    mock = AsyncMock()
    mock.document = AsyncMock()  # Ensure document is also a mock
    return mock

@pytest.fixture
def mock_bot():
    """Creates a mock bot object."""
    return AsyncMock()

@pytest.mark.asyncio
async def test_handle_document_success(mock_message, mock_bot, test_db):
    """Test successful document handling."""
    # Clear the database before this specific test
    cursor = test_db.cursor()
    cursor.execute("DELETE FROM websites")
    test_db.commit()


    data = {
        'title': ['Test Site 3', 'Test Site 4'],
        'url': ['https://example.com/3', 'https://example.com/4'],
        'xpath': ['//div[@class="price3"]', '//span[@class="price4"]']
    }
    df = pd.DataFrame(data)
    excel_file = BytesIO()
    df.to_excel(excel_file, index=False)
    excel_file.seek(0)  # Important: Reset the stream's position

    mock_message.document.file_name = "test_file.xlsx"
    mock_message.document.file_id = "test_file_id"
    mock_bot.get_file.return_value.file_path = "test_file_path"

    async def download_side_effect(file_path, destination):
        with open(destination, 'wb') as f:
            f.write(excel_file.read())  # Read from the BytesIO object

    mock_bot.download_file.side_effect = download_side_effect

    await handle_document(mock_message, mock_bot, test_db)

    mock_bot.download_file.assert_called_once()
    mock_message.answer.assert_called()  # Check that *some* answer was sent

    websites = get_all_websites(test_db)
    assert len(websites) == 2
    assert websites[0]['title'] == 'Test Site 3'
    assert websites[1]['url'] == 'https://example.com/4'

@pytest.mark.asyncio
async def test_handle_document_missing_column(mock_message, mock_bot, test_db):
    """Test handling a file with a missing column."""
    # --- Correct Data Setup ---
    data = {
        'title': ['Test Site 1'],
        'url': ['https://example.com/1']
    }
    df = pd.DataFrame(data)
    excel_file = BytesIO()
    df.to_excel(excel_file, index=False)
    excel_file.seek(0)

    mock_message.document.file_name = "test_file.xlsx"
    mock_message.document.file_id = "test_file_id"
    mock_bot.get_file.return_value.file_path = "test_file_path"

    async def download_side_effect(file_path, destination):
        with open(destination, 'wb') as f:
            f.write(excel_file.read())
    mock_bot.download_file.side_effect = download_side_effect

     # Clear the database before this specific test
    cursor = test_db.cursor()
    cursor.execute("DELETE FROM websites")
    test_db.commit()

    await handle_document(mock_message, mock_bot, test_db)

    mock_message.answer.assert_called_with("Ошибка: В файле отсутствуют колонки: xpath.")
    assert not os.path.exists("data/temp_file.xlsx")
    assert len(get_all_websites(test_db)) == 0

@pytest.mark.asyncio
async def test_handle_document_invalid_file(mock_message, mock_bot, test_db):
    """Test handling a non-Excel file."""
    mock_message.document.file_name = "invalid_file.txt"
    mock_message.document.file_id = "invalid_file_id"

    await handle_document(mock_message, mock_bot, test_db)

    mock_message.answer.assert_called_with("Пожалуйста, отправьте файл в формате Excel (.xls, .xlsx).")


@pytest.mark.asyncio
async def test_handle_document_exception(mock_message, mock_bot, test_db):
    """Test exception handling during file processing."""
    mock_message.document.file_name = "test_file.xlsx"
    mock_message.document.file_id = "test_file_id"
    mock_bot.get_file.side_effect = Exception("Simulated error")

    await handle_document(mock_message, mock_bot, test_db)
    mock_message.answer.assert_called()
    assert "Произошла ошибка при обработке файла" in mock_message.answer.call_args[0][0]
    assert not os.path.exists("data/temp_file.xlsx")


@pytest.mark.asyncio
async def test_handle_document_empty_excel(mock_message, mock_bot, test_db):
    """Test handling an empty Excel file (headers only)."""
    df = pd.DataFrame(columns=['title', 'url', 'xpath'])  # Empty DataFrame
    excel_file = BytesIO()
    df.to_excel(excel_file, index=False)
    excel_file.seek(0)

    mock_message.document.file_name = "empty_file.xlsx"
    mock_message.document.file_id = "empty_file_id"
    mock_bot.get_file.return_value.file_path = "empty_file_path"

    async def download_side_effect(file_path, destination):
        with open(destination, 'wb') as f:
            f.write(excel_file.read())
    mock_bot.download_file.side_effect = download_side_effect

    # Clear the database before this specific test
    cursor = test_db.cursor()
    cursor.execute("DELETE FROM websites")
    test_db.commit()

    await handle_document(mock_message, mock_bot, test_db)

    mock_bot.download_file.assert_called_once()
    mock_message.answer.assert_called()
    assert not os.path.exists("data/temp_file.xlsx")

    websites = get_all_websites(test_db)
    assert len(websites) == 0, "Database should be empty for an empty Excel file."