# 🚀 AI Hybrid Analysis Platform

A powerful AI-driven analysis platform that integrates with ThoughtSpot and Claude AI to generate automated insights and reports.

## ✨ Features

- 🔄 **Dynamic Scenario Management** - Load and configure analysis scenarios from JSON
- 🤖 **AI-Powered Analysis** - Integration with Claude AI for intelligent insights  
- 📊 **ThoughtSpot Integration** - Direct API connection to ThoughtSpot liveboards
- 🌐 **Web-Based UI** - Modern, futuristic interface for easy interaction
- 📈 **Report Generation** - Automated report creation and version management
- ⚙️ **Configurable** - Environment-based configuration for different setups

## 🛠️ Quick Start

### Prerequisites
- Python 3.9+ 
- Virtual environment (recommended)
- ThoughtSpot account with API access
- Claude API key from Anthropic

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YourUsername/AI-Highlights-2.0.git
   cd AI-Highlights-2.0
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment configuration**
   ```bash
   cp .env.example backend/.env
   ```

5. **Configure your API keys** (Edit `backend/.env`):
   ```bash
   THOUGHTSPOT_BASE_URL=https://your-instance.thoughtspotstaging.cloud
   THOUGHTSPOT_AUTH_TOKEN=your_base64_encoded_token
   CLAUDE_API_KEY=sk-ant-api03-your_claude_api_key
   PORT=5005
   ```

6. **Start the application**
   ```bash
   ./start_servers.sh
   ```

7. **Open your browser** and go to: `http://localhost:5005`

## 📁 Project Structure

```
AI-Highlights-2.0/
├── backend/               # Backend API server
│   ├── .env              # Environment configuration 
│   ├── api_server.py     # Main Flask server
│   ├── inputs.json       # Scenario configurations
│   └── ...
├── frontend/             # Web interface
│   ├── index.html        # Main UI
│   ├── script.js         # Frontend logic
│   └── styles.css        # Futuristic styling
├── start_servers.sh      # Easy startup script
├── requirements.txt      # Python dependencies
└── .env.example         # Configuration template
```

## 🎯 Usage

### 1. Configure Settings
- Open the **Settings tab** in the web interface
- Enter your ThoughtSpot URL and authentication token
- Add your Claude API key
- Test the connections

### 2. Create/Select Scenarios  
- Use the **Input Configuration tab**
- Select an existing scenario or create a new one
- Configure worksheet IDs and analysis parameters

### 3. Run Analysis
- Go to the **Analysis tab**
- Select your configured scenario
- Click **Start Analysis** and wait for results

### 4. View Reports
- Use **View Analysis** to see generated reports
- Browse different versions and historical results
- Download reports for sharing

## 🔧 Configuration

### Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `THOUGHTSPOT_BASE_URL` | Your ThoughtSpot instance URL | ✅ Yes |
| `THOUGHTSPOT_AUTH_TOKEN` | Base64 encoded auth token | ✅ Yes |
| `CLAUDE_API_KEY` | Anthropic Claude API key | ✅ Yes |
| `PORT` | Server port (default: 5005) | ⚪ Optional |

### Getting API Keys

#### ThoughtSpot Token
1. Log into your ThoughtSpot instance
2. Go to **Develop > REST API > REST API Playground**
3. Generate a token or use your existing credentials
4. Base64 encode: `username:password`

#### Claude API Key
1. Sign up at [Anthropic Console](https://console.anthropic.com)
2. Create a new API key
3. Copy the key starting with `sk-ant-api03-...`

## 🐛 Troubleshooting

### Common Issues

**Server won't start:**
- Check if virtual environment is activated
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check port availability: `lsof -i :5005`

**API connection failures:**
- Verify API keys in Settings tab
- Check ThoughtSpot URL format (https://...)
- Test connection using the built-in test feature

**Analysis fails:**
- Ensure worksheet IDs are correct
- Check Claude API quota/limits
- Review browser console for errors

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For questions or issues, please:
1. Check the troubleshooting section above
2. Review existing GitHub issues  
3. Create a new issue with detailed description

---

**Made with ❤️ for data-driven insights**
