# HiOllama

> **A Paradigm Shift in AI Communication**  
> *Create multiple AI personalities that can talk to each other*

HiOllama revolutionizes how we interact with AI by enabling **multiple distinct AI personalities** to coexist and communicate within a single application. Unlike traditional single-context chat interfaces, HiOllama creates isolated AI personalities through unique system prompts and conversation histories, while allowing them to seamlessly communicate with each other.

## 🌟 The Paradigm Shift

**Traditional AI Chat**: One conversation, one context, one personality.

**HiOllama**: Multiple AI personalities, each with their own:
- **System prompt** (defining their role, knowledge, and behavior)
- **Conversation history** (their unique memory and context)
- **Ability to communicate** with other AI personalities via the `/twist` command

Think of it as hosting a **multi-dimensional AI conference** where different AI experts, assistants, or personas can collaborate, debate, and share insights - all powered by a single Ollama model.

## ✨ Key Features

### 🎭 Multi-Personality Architecture
- **Unlimited Chat Sessions**: Create as many AI personalities as needed
- **Unique System Prompts**: Each session can have a completely different AI persona
- **Isolated Contexts**: Conversations remain separate unless explicitly bridged
- **Persistent Memory**: Each personality maintains its own conversation history

### 🔄 Inter-Personality Communication
- **`/twist` Command**: Send messages between AI personalities
- **Cross-Context Collaboration**: Let different AI experts work together
- **Knowledge Sharing**: Bridge insights between specialized AI personas

### ⚡ Powerful Command System
**23+ Commands across 6 categories:**

- **🎯 Core Chat**: `/new`, `/switch`, `/list`, `/rename`, `/delete`
- **🔄 Communication**: `/twist`, `/copy` (send messages between AI personalities)
- **💾 Session Management**: `/save`, `/load`, `/export` (backup AI personalities)  
- **⚙️ Model Config**: `/model`, `/system`, `/config` (manage global settings)
- **🔍 Info & Control**: `/status`, `/clear`, `/help` (monitor and control)
- **🛠️ Advanced**: `/debug`, `/history`, `/search` (power user features)

**➡️ See [COMMANDS.md](COMMANDS.md) for complete command reference with examples and usage patterns**

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**
- **Ollama** installed and running locally
- At least one Ollama model downloaded (e.g., `llama2`, `mistral`, `codellama`)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/hiollama.git
cd hiollama

# Install dependencies
pip install -r requirements.txt

# Ensure Ollama is running
ollama serve

# Start HiOllama
python -m hiollama
```

### Your First Multi-Personality Setup

```bash
# Start with default AI personality
> Hello! How can I help you today?

# Create a coding expert personality
/new
/system You are a senior software engineer specializing in Python and system architecture.
> I'm ready to help with coding challenges and architectural decisions.

# Create a creative writing personality  
/new
/system You are a creative writing coach who helps with storytelling, character development, and narrative structure.
> I'm here to help bring your stories to life!

# Let the coding expert and writing coach collaborate
/twist 1 "Can you help me create a compelling narrative for a software project README?"

# Switch between personalities
/switch 0  # Back to general assistant
/switch 1  # Coding expert
/switch 2  # Writing coach
```

## 🎯 Use Cases

### 🔬 **Multi-Expert Collaboration**
Create specialized AI personalities for different domains:
- **Technical Expert**: System architecture, debugging, code review
- **Creative Director**: UI/UX design, user experience, branding
- **Project Manager**: Planning, coordination, stakeholder communication
- **Quality Assurance**: Testing strategies, edge cases, validation

### 📚 **Educational Scenarios**
- **Teacher + Student**: Create learning dialogues between AI personas
- **Debate Partners**: Have AI personalities argue different perspectives
- **Study Groups**: Multiple AI tutors with different teaching styles

### 🎨 **Creative Projects**
- **Character Development**: Create AI personalities matching story characters
- **Worldbuilding**: Different AI perspectives for various aspects of fictional worlds
- **Content Creation**: Collaborate between AI writers, editors, and critics

### 🔧 **Development Workflows**
- **Code Reviewer**: Specialized AI for code quality and security
- **Documentation Writer**: AI focused on clear technical communication
- **Testing Specialist**: AI personality dedicated to comprehensive testing strategies

## 🏗️ Architecture Highlights

### Single Model, Multiple Personalities
HiOllama uses **one Ollama model** to power all AI personalities. The magic happens through:
- **Isolated System Prompts**: Each session gets unique context and role definition
- **Separate Conversation Histories**: Personalities maintain independent memories
- **Dynamic Context Switching**: Seamlessly move between different AI personas

### Event-Driven Design
- **Session Manager**: Orchestrates multiple AI personalities
- **Command Registry**: Extensible system for adding new capabilities
- **Configuration Management**: Global and per-session settings

### Extensible Command System
Adding new commands is straightforward:
```python
@register_command
class YourCustomCommand(Command):
    aliases = ["custom", "cc"]
    description = "Your custom functionality"
    category = CommandCategory.ADVANCED
    
    def execute(self, args: str, session_manager: ChatSessionManager) -> CommandResult:
        # Your implementation
        return CommandResult.success("Custom command executed!")
```

## 📖 Documentation

- **[COMMANDS.md](COMMANDS.md)** - Complete command reference with examples and usage patterns
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed technical architecture and design patterns
- **[API Reference](docs/api.md)** - Complete command and configuration reference
- **[Examples](docs/examples.md)** - Real-world multi-personality scenarios

## 🤝 Contributing

We welcome contributions to expand HiOllama's multi-personality capabilities!

### Areas for Contribution
- **New Commands**: Expand the command system
- **Personality Templates**: Pre-configured AI personality setups
- **Integration Features**: Connect with external tools and APIs
- **UI Improvements**: Enhance the chat interface
- **Documentation**: Examples, tutorials, and guides

### Getting Started
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes and add tests
4. Submit a pull request with detailed description

## 📋 Requirements

```
ollama>=0.1.0
requests>=2.28.0
prompt-toolkit>=3.0.0
rich>=12.0.0
pyyaml>=6.0
```

## 🔮 Future Vision

HiOllama is evolving towards an **AI Personality Ecosystem** where:
- **Personality Marketplaces**: Share and discover AI personality configurations
- **Cross-Model Support**: Use different models for different personalities
- **Advanced Communication**: Rich media exchange between AI personalities
- **Persistent Relationships**: AI personalities that remember each other across sessions
- **Collaborative Workspaces**: Multiple users interacting with shared AI personalities

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- **Ollama Team** - For providing the excellent local LLM infrastructure
- **AI Community** - For inspiration and feedback on multi-context AI interactions
- **Contributors** - Everyone helping to expand the boundaries of AI communication

---

**HiOllama**: *Where AI personalities come alive and collaborate* 🎭✨