## Запуск MCP - сервера ##

1. перейти в директорию mcp_agent\healthcare-mcp-public
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (optional):
   ```bash
   # Create .env file from example
   cp .env.example .env
   ```

5. Run the server:
   ```bash
   python run.py --http --port 8000
   ```

## Тестирование диалога с моделью ##

Запустить скрипт mcp_agent\agent.py
Много раз не запускать, у меня там лимит!!! Я платить денежка.