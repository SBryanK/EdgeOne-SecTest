# EdgeOne SecTest - Web Security Testing Platform

## 🛡️ Overview

EdgeOne SecTest is a comprehensive web security testing platform built with Streamlit, designed for security professionals, developers, and organizations to test web applications for vulnerabilities and generate security-focused edge functions.

## ✨ Features

### 🔴 Security Testing

- **9 Attack Types**: SQL Injection, XSS, Command Injection, Path Traversal, XXE, SSTI, NoSQL Injection, LDAP Injection, Custom Payload
- **Default Payloads**: Pre-configured payloads for each attack type
- **Custom Payloads**: Full customization for advanced testing
- **Multiple Execution Modes**: Single, Sequential, and Parallel testing
- **Real-time Results**: Live status updates and detailed analysis

### 🔵 Edge Function Generators

- **Maintenance Hour**: Scheduled downtime management
- **Simple Bot Detection**: Header-based bot blocking
- **Custom Header Injection**: Response header modification
- **Remote Authentication**: External auth service integration
- **Rate Limiting**: KV-based rate limiting with burst protection
- **Security Headers**: Comprehensive security headers (CSP, HSTS, etc.)
- **IP Geolocation**: Geographic access control
- **Request Logging**: Security monitoring and analytics
- **A/B Testing**: Traffic splitting for testing

### 📊 Analytics & Reporting

- **Test History**: Comprehensive test result tracking
- **Export Options**: CSV, JSON, and clipboard export
- **Vulnerability Detection**: Automatic detection of common vulnerabilities
- **Performance Metrics**: Response times and success rates
- **Detailed Analysis**: In-depth result analysis with recommendations

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/tencentsec-test.git
cd tencentsec-test

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run pentestweb.py
```

### Railway.app Deployment

1. Connect your GitHub repository to Railway
2. Railway will automatically detect Python and install dependencies
3. Deploy with one click
4. Access your application via Railway URL

## 🏗️ Architecture

### Current Stack

```
Frontend: Streamlit
Backend: Python (requests, httpx, aiohttp)
Storage: CSV files
Deployment: Railway.app ready
```

### File Structure

```
├── pentestweb.py          # Main application
├── edge_templates.py       # Edge function generators
├── requirements.txt       # Dependencies
├── data/
│   └── history.csv        # Test results storage
├── pictures/
│   └── logotencenttengah.jpg
├── HANDOVER.md            # Project handover documentation
├── DEVELOPMENT_ROADMAP.md # Development roadmap
└── AI_AGENT_REFERENCE.md  # AI agent reference guide
```

## 🔧 Usage

### Security Testing

1. **Select Attack Type**: Choose from 9 different attack types
2. **Configure Payloads**: Use default payloads or create custom ones
3. **Set Target URL**: Enter the target application URL
4. **Execute Tests**: Run single or multiple tests
5. **Analyze Results**: Review detailed results and recommendations

### Edge Function Generation

1. **Choose Template**: Select from 9 edge function templates
2. **Configure Settings**: Customize parameters for your needs
3. **Generate Code**: Download ready-to-deploy JavaScript code
4. **Deploy**: Use generated code in Cloudflare Workers

### Rate Testing

1. **Set Parameters**: Configure request count, concurrency, and timeout
2. **Run Load Test**: Execute performance testing
3. **Analyze Results**: Review performance metrics and bottlenecks

## 📈 Development Roadmap

### Phase 1: Database Integration (Current Priority)

- PostgreSQL database integration
- User authentication system
- Data migration from CSV to database
- User-specific test results

### Phase 2: Advanced Features

- Enhanced payload management
- Team collaboration features
- API development
- Advanced analytics

### Phase 3: Enterprise Features

- Multi-tenancy support
- Advanced security features
- Compliance reporting
- Professional services

## 🔐 Security Considerations

### Current Security

- Public access (no authentication)
- CSV-based storage
- No data encryption

### Planned Security Enhancements

- User authentication and authorization
- Data encryption and protection
- Input validation and sanitization
- Audit logging and monitoring

## 🛠️ Development

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Run linting
flake8 pentestweb.py edge_templates.py
```

## 📊 Performance

### Current Performance

- **Response Time**: < 2 seconds for single requests
- **Concurrent Users**: Up to 50 users
- **Memory Usage**: ~100MB per instance
- **Storage**: CSV-based, unlimited size

### Optimization Plans

- Database caching
- CDN integration
- Async processing
- Resource optimization

## 🚨 Known Limitations

### Current Limitations

- No user authentication
- CSV storage limitations
- No data encryption
- Limited scalability

### Planned Improvements

- Database integration
- User management system
- Data encryption
- Scalable architecture

## 📞 Support

### Documentation

- **Handover Guide**: [HANDOVER.md](HANDOVER.md)
- **Development Roadmap**: [DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md)
- **AI Agent Reference**: [AI_AGENT_REFERENCE.md](AI_AGENT_REFERENCE.md)

### Contact

- **Repository**: [GitHub URL]
- **Issues**: [GitHub Issues](https://github.com/yourusername/tencentsec-test/issues)
- **Email**: [Your Email]

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Streamlit team for the amazing framework
- Railway.app for easy deployment
- Security community for payload contributions
- Open source contributors

---

**Version**: 1.0  
**Last Updated**: [Current Date]  
**Status**: Active Development
