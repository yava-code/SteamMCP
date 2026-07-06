"""
MCP Smoke Tests for SteamMCP

These tests verify that the MCP server can be imported, initialized,
and that all tools are properly registered without requiring live Steam API calls.
"""

import asyncio
import importlib
import pytest
from unittest.mock import patch, Mock


class TestMCPServerImport:
    """Test that the MCP server module can be imported successfully."""

    def test_server_module_import(self, monkeypatch):
        """Test that server.py can be imported without errors."""
        # Set up environment to avoid import errors
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        
        # Mock requests to avoid network calls during import
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"ok": True}
            mock_get.return_value = mock_response
            
            # This should not raise any exceptions
            server = importlib.import_module("server")
            assert server is not None
            assert hasattr(server, 'mcp')

    def test_mcp_instance_exists(self, monkeypatch):
        """Test that the mcp instance is created."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"ok": True}
            mock_get.return_value = mock_response
            
            server = importlib.import_module("server")
            assert server.mcp is not None
            assert hasattr(server.mcp, 'name')


class TestMCPToolsRegistration:
    """Test that all MCP tools are properly registered."""

    def test_tools_are_registered(self, monkeypatch):
        """Test that all tool functions are registered with the MCP server."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"ok": True}
            mock_get.return_value = mock_response
            
            server = importlib.import_module("server")
            
            # Get all functions from the server module that are tools
            tool_functions = [
                'get_profile_info',
                'get_friends',
                'resolve_vanity_url_name',
                'get_player_achievements',
                'get_user_stats',
                'get_owned_games',
                'get_recently_played_games',
                'get_game_news',
                'get_game_schema',
                'get_app_details',
                'get_top_market_items',
                'search_market_items',
                'get_item_price_history',
                'get_item_price_overview',
                'get_popular_market_items',
                'get_recent_market_activity',
            ]
            
            # Verify each tool function exists in the server module
            for tool_name in tool_functions:
                assert hasattr(server, tool_name), f"Tool {tool_name} not found in server module"
                tool_func = getattr(server, tool_name)
                assert callable(tool_func), f"{tool_name} is not callable"

    def test_tools_have_docstrings(self, monkeypatch):
        """Test that all tools have proper docstrings."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"ok": True}
            mock_get.return_value = mock_response
            
            server = importlib.import_module("server")
            
            tool_functions = [
                'get_profile_info',
                'get_friends',
                'resolve_vanity_url_name',
                'get_player_achievements',
                'get_user_stats',
                'get_owned_games',
                'get_recently_played_games',
                'get_game_news',
                'get_game_schema',
                'get_app_details',
                'get_top_market_items',
                'search_market_items',
                'get_item_price_history',
                'get_item_price_overview',
                'get_popular_market_items',
                'get_recent_market_activity',
            ]
            
            for tool_name in tool_functions:
                tool_func = getattr(server, tool_name)
                assert tool_func.__doc__ is not None, f"{tool_name} has no docstring"
                assert len(tool_func.__doc__) > 0, f"{tool_name} has empty docstring"


class TestMCPServerInitialization:
    """Test that the MCP server can be initialized without live API calls."""

    def test_server_initialization_no_api_calls(self, monkeypatch):
        """Test that server initialization doesn't make live API calls."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        
        with patch('requests.get') as mock_get:
            # Import server - should not make any API calls
            server = importlib.import_module("server")
            
            # Verify no requests were made
            assert mock_get.call_count == 0, "Server initialization made unexpected API calls"

    def test_tools_can_be_called_with_mocks(self, monkeypatch):
        """Test that tools can be called with mocked dependencies."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "response": {
                    "players": [{"steamid": "76561198006409530", "personaname": "TestUser"}]
                }
            }
            mock_get.return_value = mock_response
            
            server = importlib.import_module("server")
            
            # Test a simple tool call
            result = server.get_profile_info("76561198006409530")
            assert result is not None
            # New API returns normalized response with 'ok' field
            assert "ok" in result or "data" in result


class TestMCPFastMCPIntegration:
    """Test integration with FastMCP framework."""

    def test_fastmcp_import(self):
        """Test that fastmcp can be imported."""
        try:
            import fastmcp
            assert fastmcp is not None
        except ImportError:
            pytest.skip("fastmcp not installed")

    def test_fastmcp_fastmcp_class(self):
        """Test that FastMCP class exists."""
        try:
            from fastmcp import FastMCP
            assert FastMCP is not None
        except ImportError:
            pytest.skip("fastmcp not installed")

    def test_mcp_server_is_fastmcp_instance(self, monkeypatch):
        """Test that the mcp server is a FastMCP instance."""
        try:
            from fastmcp import FastMCP
        except ImportError:
            pytest.skip("fastmcp not installed")
        
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"ok": True}
            mock_get.return_value = mock_response
            
            server = importlib.import_module("server")
            assert isinstance(server.mcp, FastMCP)


class TestMCPToolsListed:
    """Test that all tools are properly listed by the MCP server."""

    @pytest.mark.asyncio
    async def test_all_tools_listed(self, monkeypatch):
        """Test that all expected tools are listed by the MCP server."""
        try:
            from fastmcp import FastMCP
        except ImportError:
            pytest.skip("fastmcp not installed")
        
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"ok": True}
            mock_get.return_value = mock_response
            
            server = importlib.import_module("server")
            
            # Get the list of registered tools
            tools = await server.mcp.list_tools()
            
            # Expected tool names
            expected_tools = {
                'get_profile_info',
                'get_friends',
                'resolve_vanity_url_name',
                'get_player_achievements',
                'get_user_stats',
                'get_owned_games',
                'get_recently_played_games',
                'get_game_news',
                'get_game_schema',
                'get_app_details',
                'get_top_market_items',
                'search_market_items',
                'get_item_price_history',
                'get_item_price_overview',
                'get_popular_market_items',
                'get_recent_market_activity',
            }
            
            # Check that all expected tools are registered
            registered_tool_names = {tool.name for tool in tools}
            assert expected_tools.issubset(registered_tool_names), \
                f"Missing tools: {expected_tools - registered_tool_names}"
            
            # Check that we have exactly the expected number of tools
            assert len(tools) >= len(expected_tools), \
                f"Expected at least {len(expected_tools)} tools, got {len(tools)}"

    @pytest.mark.asyncio
    async def test_tools_have_descriptions(self, monkeypatch):
        """Test that all tools have descriptions."""
        try:
            from fastmcp import FastMCP
        except ImportError:
            pytest.skip("fastmcp not installed")
        
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"ok": True}
            mock_get.return_value = mock_response
            
            server = importlib.import_module("server")
            tools = await server.mcp.list_tools()
            
            for tool in tools:
                assert tool.description is not None, f"Tool {tool.name} has no description"
                assert len(tool.description) > 0, f"Tool {tool.name} has empty description"

    @pytest.mark.asyncio
    async def test_tools_have_parameters(self, monkeypatch):
        """Test that tools have proper parameter schemas."""
        try:
            from fastmcp import FastMCP
        except ImportError:
            pytest.skip("fastmcp not installed")
        
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"ok": True}
            mock_get.return_value = mock_response
            
            server = importlib.import_module("server")
            tools = await server.mcp.list_tools()
            
            for tool in tools:
                assert tool.parameters is not None, f"Tool {tool.name} has no parameters"
                assert isinstance(tool.parameters, dict), f"Tool {tool.name} parameters is not a dict"
