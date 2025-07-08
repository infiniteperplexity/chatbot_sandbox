"""
Chatbot utilities for managing Chainlit server processes and development tasks.

This module provides utilities for:
- Managing Chainlit server processes (start/stop/status)
- Testing LLM connections
- Configuration management
- Development helpers
"""

import subprocess
import os
import signal
import time
import json
from pathlib import Path

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

try:
    from config_loader import config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False


class ChainlitManager:
    """Manage Chainlit server processes."""
    
    def __init__(self):
        self.process = None
        self.app_file = "app.py"
        
    def start_server(self, host="localhost", port=8000, background=True):
        """Start the Chainlit server."""
        try:
            if self.is_running():
                print("⚠️  Server is already running!")
                return False
            
            # Activate virtual environment and run chainlit
            cmd = [
                "bash", "-c",
                f"source chainlit-env/bin/activate && chainlit run {self.app_file} --host {host} --port {port}"
            ]
            
            if background:
                # Start in background
                self.process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    preexec_fn=os.setsid  # Create new process group
                )
                time.sleep(2)  # Give it time to start
                
                if self.process.poll() is None:  # Still running
                    print(f"🚀 Chainlit server started!")
                    print(f"🌐 URL: http://{host}:{port}")
                    return True
                else:
                    print("❌ Failed to start server")
                    return False
            else:
                # Run in foreground (blocking)
                result = subprocess.run(cmd)
                return result.returncode == 0
                
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            return False
    
    def stop_server(self):
        """Stop the Chainlit server."""
        try:
            # Method 1: Kill our tracked process
            if self.process and self.process.poll() is None:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                self.process = None
                print("🛑 Server stopped (tracked process)")
                return True
            
            # Method 2: Kill all chainlit processes
            result = subprocess.run(
                ["pkill", "-f", "chainlit run"], 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                print("🛑 Server stopped (pkill)")
                return True
            else:
                print("ℹ️  No running Chainlit processes found")
                return False
                
        except Exception as e:
            print(f"❌ Error stopping server: {e}")
            return False
    
    def is_running(self):
        """Check if Chainlit server is running."""
        try:
            result = subprocess.run(
                ["pgrep", "-f", "chainlit run"], 
                capture_output=True, 
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def status(self):
        """Get server status."""
        if self.is_running():
            print("✅ Chainlit server is running")
            # Try to get process info
            try:
                result = subprocess.run(
                    ["pgrep", "-f", "chainlit run"], 
                    capture_output=True, 
                    text=True
                )
                if result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    print(f"📊 Process IDs: {', '.join(pids)}")
            except:
                pass
        else:
            print("❌ Chainlit server is not running")


def create_chatbot_app():
    """Create and return the chatbot application components."""
    if not CONFIG_AVAILABLE:
        raise ImportError("Configuration loader not available")
    if not LANGCHAIN_AVAILABLE:
        raise ImportError("LangChain libraries not available")
    
    # Load OpenAI configuration
    openai_config = config.get_openai_config()
    
    # Initialize the OpenAI chat model
    llm = ChatOpenAI(
        api_key=openai_config.get('api_key'),
        model=openai_config.get('model', 'gpt-4.1'),
        temperature=openai_config.get('temperature', 0.7),
        max_tokens=openai_config.get('max_tokens', 1000)
    )
    
    # System message to set the AI's behavior
    system_message = SystemMessage(content="""
    You are a helpful AI assistant built with Chainlit and LangChain. 
    You should be friendly, informative, and concise in your responses.
    """)
    
    return llm, system_message


def test_llm_connection():
    """Test the LLM connection without Chainlit."""
    try:
        llm, system_message = create_chatbot_app()
        
        # Test with a simple message
        test_messages = [
            system_message,
            HumanMessage(content="Hello! Can you respond with a short greeting?")
        ]
        
        print("🔍 Testing LLM connection...")
        response = llm.invoke(test_messages)
        
        print("✅ LLM connection successful!")
        print(f"📝 Test Response: {response.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM connection failed: {e}")
        return False


def check_server_status(manager):
    """Quick status check."""
    manager.status()


def open_browser():
    """Open the chatbot in system default browser."""
    try:
        import webbrowser
        url = "http://localhost:8000"
        print(f"🌐 Opening {url} in system browser...")
        webbrowser.open(url)
    except Exception as e:
        print(f"❌ Error opening browser: {e}")
        print("💡 Manually open: http://localhost:8000")


def open_vscode_browser():
    """Open the chatbot in VS Code Simple Browser."""
    try:
        # This uses VS Code's command API to open the Simple Browser
        import subprocess
        url = "http://localhost:8000"
        print(f"🌐 Opening {url} in VS Code Simple Browser...")
        
        # Try to use VS Code command to open Simple Browser
        # This works when running from within VS Code
        result = subprocess.run([
            "code", "--command", "simpleBrowser.show", url
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Opened in VS Code Simple Browser")
        else:
            # Fallback to system browser
            print("⚠️  VS Code Simple Browser not available, using system browser...")
            open_browser()
            
    except Exception as e:
        print(f"❌ Error opening VS Code browser: {e}")
        print("💡 Fallback: Opening in system browser...")
        try:
            open_browser()
        except:
            print("💡 Manually open: http://localhost:8000")


def restart_server(manager):
    """Restart the chatbot server."""
    print("🔄 Restarting server...")
    manager.stop_server()
    time.sleep(2)
    success = manager.start_server()
    
    if success:
        print("✅ Server restarted successfully!")
    else:
        print("❌ Failed to restart server")


def show_config():
    """Display current configuration."""
    if not CONFIG_AVAILABLE:
        print("❌ Configuration loader not available")
        return
    
    try:
        openai_config = config.get_openai_config()
        chainlit_config = config.get_chainlit_config()
        
        print("📋 Current Configuration:")
        print("=" * 40)
        print(f"OpenAI Model: {openai_config.get('model')}")
        print(f"Temperature: {openai_config.get('temperature')}")
        print(f"Max Tokens: {openai_config.get('max_tokens')}")
        print(f"Host: {chainlit_config.get('host')}")
        print(f"Port: {chainlit_config.get('port')}")
        print(f"Debug: {chainlit_config.get('debug')}")
        print("=" * 40)
    except Exception as e:
        print(f"❌ Error reading config: {e}")


def test_configuration():
    """Test and display the current configuration settings."""
    if not CONFIG_AVAILABLE:
        print("❌ Configuration loader not available")
        return
    
    try:
        # Load and display OpenAI configuration
        openai_config = config.get_openai_config()
        
        print("🔧 Current Configuration:")
        print(f"  Model: {openai_config.get('model', 'Not set')}")
        print(f"  Temperature: {openai_config.get('temperature', 'Not set')}")
        print(f"  Max Tokens: {openai_config.get('max_tokens', 'Not set')}")
        
        # Check if API key is configured (without showing it)
        api_key = openai_config.get('api_key', '')
        if api_key and api_key != "your-openai-api-key-here":
            print(f"  API Key: ✅ Configured (ends with ...{api_key[-4:]})")
        else:
            print("  API Key: ❌ Not configured or using placeholder")
        
        # Display Chainlit configuration
        chainlit_config = config.get_chainlit_config()
        print(f"\n🌐 Chainlit Configuration:")
        print(f"  Host: {chainlit_config.get('host', 'localhost')}")
        print(f"  Port: {chainlit_config.get('port', 8000)}")
        print(f"  Debug: {chainlit_config.get('debug', False)}")
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        print("Make sure config.json exists and is properly formatted!")


# Global manager instance for convenience
chainlit_manager = ChainlitManager()


def get_manager():
    """Get the global ChainlitManager instance."""
    return chainlit_manager


def print_available_functions():
    """Print all available utility functions."""
    print("🛠️  Chatbot utility functions available:")
    print("  • ChainlitManager() - Class for managing server processes")
    print("  • chainlit_manager - Global manager instance")
    print("  • test_configuration() - Test configuration settings")
    print("  • create_chatbot_app() - Create chatbot components")
    print("  • test_llm_connection() - Test LLM connection")
    print("  • check_server_status(manager) - Check server status")
    print("  • open_browser() - Open chatbot in browser")
    print("  • open_vscode_browser() - Open chatbot in VS Code Simple Browser")
    print("  • restart_server(manager) - Restart the server")
    print("  • show_config() - Display current configuration")
