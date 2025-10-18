# EdgeOne SecTest - AI Agent Reference Guide

## 🤖 For AI Agents Continuing Development

This document provides essential context and guidelines for AI agents that will continue developing the EdgeOne SecTest application.

## 📋 Project Context

### What is EdgeOne SecTest?

A web security testing platform built with Streamlit that allows users to:

- Test web applications with various payload types (SQL injection, XSS, etc.)
- Generate Cloudflare Edge Functions for security
- Perform load testing and rate limiting
- Track testing history and results

### Current Architecture

```
Frontend: Streamlit (Python)
Backend: Python requests/httpx
Storage: CSV files (data/history.csv)
Deployment: Railway.app ready
Authentication: None (public access)
```

## 🏗️ Code Structure

### Main Files

- **`pentestweb.py`** - Main application (1042 lines)
- **`edge_templates.py`** - Edge function generators (921 lines)
- **`requirements.txt`** - Dependencies
- **`data/history.csv`** - Test results storage

### Key Functions in pentestweb.py

```python
# Core functions
def page_curl()                    # Main payload testing interface
def execute_single_request()       # Execute individual tests
def execute_multiple_requests()    # Execute batch tests
def display_results()             # Show test results
def page_rate()                   # Load testing
def page_history()                # Test history

# Payload execution functions
def execute_with_query_payload()  # SQL injection testing
def execute_with_xss_payload()    # XSS testing
def execute_with_cmd_payload()    # Command injection testing
# ... and 6 more payload types
```

### Key Functions in edge_templates.py

```python
# Edge function generators
def page_maintenance_hour()       # Maintenance mode
def page_simple_bot_detection()   # Bot blocking
def page_custom_header_injection() # Header injection
def page_remote_auth()           # Remote authentication
def page_rate_limiting()          # Rate limiting
def page_security_headers()      # Security headers
def page_ip_geolocation()        # Geographic blocking
def page_request_logging()        # Request logging
def page_ab_testing()            # A/B testing
```

## 🔧 Current Features

### Payload Testing System

- **9 Attack Types**: SQL Injection, XSS, Command Injection, Path Traversal, XXE, SSTI, NoSQL Injection, LDAP Injection, Custom Payload
- **Default Payloads**: Each attack type has 1 default payload
- **Custom Input**: Users can modify all payloads
- **Execution Modes**: Single, Sequential, Parallel
- **Results Display**: User-friendly with status indicators

### Edge Function Generators

- **9 Templates**: Maintenance, Bot Detection, Header Injection, Remote Auth, Rate Limiting, Security Headers, IP Geolocation, Request Logging, A/B Testing
- **Configurable**: Each template has multiple configuration options
- **Downloadable**: Generated code can be downloaded as .js files

### Current Limitations

- **No Authentication**: Public access only
- **CSV Storage**: Not suitable for large datasets
- **No User Management**: All users share same data
- **Limited Scalability**: Single instance deployment

## 🚀 Next Development Priorities

### Phase 1: Database Integration (CRITICAL)

```python
# Required changes
1. Add PostgreSQL database
2. Implement user authentication
3. Replace CSV storage with database
4. Add user-specific data isolation
```

### Database Schema Needed

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Test results table
CREATE TABLE test_results (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    test_type VARCHAR(50) NOT NULL,
    target_url TEXT NOT NULL,
    payload TEXT,
    status_code INTEGER,
    response_time FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Payloads library table
CREATE TABLE payloads (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    payload TEXT NOT NULL,
    description TEXT,
    severity VARCHAR(20),
    is_public BOOLEAN DEFAULT TRUE,
    created_by INTEGER REFERENCES users(id)
);
```

### Authentication System Needed

```python
# Required functions to implement
def authenticate_user(username, password)
def create_user(username, email, password)
def get_current_user()
def require_login()
def logout_user()
```

## 🛠️ Development Guidelines

### Code Style

- **Python**: Follow PEP 8 standards
- **Streamlit**: Use proper session state management
- **Error Handling**: Always use try-catch blocks
- **User Experience**: Provide clear error messages

### Key Patterns

```python
# Session state management
st.session_state.setdefault("key", default_value)

# Error handling
try:
    result = execute_test()
except Exception as e:
    st.error(f"Error: {str(e)}")

# User-friendly results
if result.get("error"):
    st.error(result["error"])
else:
    st.success("Test completed successfully")
```

### Database Integration Pattern

```python
# Replace CSV functions with database functions
def append_history_db(user_id, test_data):
    # Database insert instead of CSV append
    pass

def load_history_db(user_id, limit=500):
    # Database query instead of CSV read
    pass
```

## 🔐 Security Considerations

### Current Security Issues

- **No Authentication**: Anyone can access
- **No Data Encryption**: Sensitive data in plain text
- **No Input Validation**: Potential injection attacks
- **No Rate Limiting**: Can be abused

### Required Security Enhancements

```python
# Authentication
- Implement secure login system
- Use password hashing (bcrypt)
- Session management with JWT tokens

# Data Protection
- Encrypt sensitive data
- Input validation and sanitization
- SQL injection prevention

# Access Control
- User-specific data access
- Role-based permissions
- Audit logging
```

## 📊 Performance Considerations

### Current Performance

- **Response Time**: < 2 seconds for single requests
- **Concurrent Users**: Up to 50 users
- **Memory Usage**: ~100MB per instance
- **Storage**: CSV-based, unlimited size

### Optimization Needed

```python
# Database optimization
- Connection pooling
- Query optimization
- Indexing strategy

# Caching
- Redis for session storage
- Result caching
- Static content caching

# Async processing
- Background tasks
- Queue system
- Worker processes
```

## 🧪 Testing Strategy

### Current Testing

- **Manual Testing**: Basic functionality
- **Error Handling**: Some edge cases covered
- **User Experience**: Basic UI testing

### Required Testing

```python
# Unit Tests
- Test individual functions
- Mock external dependencies
- Edge case testing

# Integration Tests
- Database integration
- Authentication flow
- End-to-end testing

# Security Tests
- Authentication bypass
- SQL injection prevention
- XSS prevention
```

## 🚀 Deployment Considerations

### Railway.app Deployment

```yaml
# Current deployment
- Single Streamlit app
- No database required
- Environment variables: None
- Dependencies: requirements.txt

# Future deployment needs
- PostgreSQL addon
- Redis addon (optional)
- Environment variables for database
- SSL certificates
```

### Environment Configuration

```python
# Required environment variables
DATABASE_URL = "postgresql://..."
SECRET_KEY = "your-secret-key"
JWT_SECRET = "jwt-secret-key"
REDIS_URL = "redis://..." # Optional
```

## 🔄 Migration Strategy

### CSV to Database Migration

```python
# Migration steps
1. Setup PostgreSQL database
2. Create database schema
3. Import existing CSV data
4. Update code to use database
5. Test migration
6. Remove CSV dependencies
```

### Code Changes Required

```python
# Replace these functions
def load_history() -> pd.DataFrame:
    # Replace with database query
    pass

def append_history_db(ts, url, method, status, reqid):
    # Replace with database insert
    pass

# Add these functions
def authenticate_user(username, password):
    # Implement authentication
    pass

def get_user_tests(user_id):
    # Get user-specific tests
    pass
```

## 📈 Success Metrics

### Phase 1 Success Criteria

- [ ] Database integration complete
- [ ] User authentication working
- [ ] Data migration successful
- [ ] Performance maintained

### Quality Assurance

- [ ] All tests passing
- [ ] No security vulnerabilities
- [ ] User experience improved
- [ ] Documentation updated

## 🆘 Common Issues & Solutions

### Known Issues

1. **CSV Storage Limitations**: Not suitable for large datasets
2. **No User Isolation**: All users share same data
3. **Performance Issues**: Can be slow with many users
4. **Security Concerns**: No authentication or data protection

### Solutions

1. **Database Integration**: Replace CSV with PostgreSQL
2. **User Management**: Implement authentication system
3. **Caching**: Add Redis for performance
4. **Security**: Implement comprehensive security measures

## 📞 Support Information

### Development Resources

- **Repository**: [GitHub URL]
- **Documentation**: HANDOVER.md, DEVELOPMENT_ROADMAP.md
- **Dependencies**: requirements.txt
- **Deployment**: Railway.app

### Key Contacts

- **Lead Developer**: [Your Name]
- **Email**: [Your Email]
- **Repository**: [GitHub URL]

---

**Reference Version**: 1.0  
**Last Updated**: [Current Date]  
**For AI Agents**: Use this as your primary reference for continuing development
