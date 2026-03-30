---
name: Web Server Manager
description: Web server management for nginx, Apache, and IIS. Use when configuring: (1) SSL/TLS certificates, (2) Load balancing, (3) Virtual hosts and subdomains, (4) Security hardening, (5) Performance optimization, (6) HTTPS redirects, (7) HTTP/2, (8) Backup/restore, (9) Troubleshooting server issues, or any web server administration tasks.
---

# Web Server Manager

Expert guidance for managing nginx, Apache, and IIS web servers with production-ready configurations.

## Supported Web Servers

| Web Server | Supported Actions |
|-------------|-------------------|
| nginx | ssl, loadbalancer, subdomain, security, optimize, https-redirect, http2, backup, restore, troubleshoot |
| Apache | ssl, loadbalancer, subdomain, security, optimize, https-redirect, http2, backup, restore, troubleshoot |
| IIS | ssl, loadbalancer, subdomain, security, optimize, https-redirect, http2, backup, restore, troubleshoot |

## Actions

### ssl
SSL certificate management:
- Certificate registration (Let's Encrypt, commercial)
- Certificate renewal and automation
- TLS configuration (1.2, 1.3)
- Certificate validation and troubleshooting

### loadbalancer
Load balancing and traffic distribution:
- Upstream/backend server configuration
- Load balancing algorithms (round-robin, least_conn, ip_hash)
- Health check setup
- Session persistence (sticky sessions)
- Failover handling

### subdomain
Subdomain management:
- Virtual host/server block configuration
- Wildcard subdomain handling
- SNI (Server Name Indication) setup
- DNS integration guidance

### security
Security hardening:
- Security headers (HSTS, X-Frame-Options, CSP)
- Rate limiting
- IP whitelisting/blacklisting
- DDoS mitigation
- SSL/TLS hardening

### optimize
Performance optimization:
- Worker/process tuning
- Keepalive optimization
- Caching strategies
- Compression (gzip, brotli, deflate)
- Connection limits and timeouts
- Buffer size tuning

### https-redirect
HTTP to HTTPS redirection:
- Permanent (301) redirects
- Redirect loop prevention
- Preserve query parameters
- HSTS configuration

### http2
HTTP/2 configuration:
- HTTP/2 module enablement
- Server push configuration
- Multiplexing setup
- ALPN negotiation
- HTTP/2 health checks

### backup
Backup operations:
- Configuration file backup
- Automatic backup scheduling
- Version control integration
- Certificate backup

### restore
Restore operations:
- Configuration restoration
- Versioned backup retrieval
- Rollback procedures
- Disaster recovery

## Usage Examples

Users can request web server management tasks in natural language:

**SSL Certificate Management:**
- "example.com에 Let's Encrypt SSL 인증서를 설정해줘"
- "nginx에 SSL 인증서를 갱신해줘"
- "Apache에서 TLS 1.3을 활성화하고 싶어"

**Load Balancing:**
- "nginx에 로드 밸런서를 설정해줘. 백엔드 서버는 backend1.example.com:8080과 backend2.example.com:8080이야"
- "Apache 로드 밸런서에 least_conn 알고리즘을 적용해줘"
- "IIS에서 세션 고정(sticky session)을 설정하고 싶어"

**Subdomain Configuration:**
- "api.example.com 서브도메인을 설정해줘"
- "nginx에서 와일드카드 서브도메인을 설정하고 싶어"
- "Apache에 새로운 가상 호스트를 추가해줘"

**Security Hardening:**
- "nginx 보안을 강화해줘"
- "Apache에 보안 헤더(HSTS, CSP)를 추가하고 싶어"
- "IIS에서 rate limiting을 설정해줘"

**Performance Optimization:**
- "Apache 성능을 최적화해줘"
- "nginx에서 gzip 압축을 활성화하고 싶어"
- "IIS 워커 프로세스를 튜닝해줘"

**HTTP/2 Configuration:**
- "nginx에서 HTTP/2를 활성화해줘"
- "IIS에 HTTP/2를 설정하고 싶어"

**Backup and Restore:**
- "nginx 설정 파일을 백업해줘"
- "Apache 백업에서 복원하고 싶어. 백업 파일은 /path/to/backup/apache-backup-2025-01-11.tar.gz야"

**Troubleshooting:**
- "nginx에서 502 bad gateway 에러가 발생해. 해결 방법을 알려줘"
- "Apache CPU 사용률이 너무 높아. 문제를 진단해줘"
- "IIS에서 SSL 핸드셰이크가 실패해. 트러블슈팅해줘"

## Context Information

Users can provide any relevant context in their natural language requests:

- **Domain names**: "example.com에 SSL을 설정해줘"
- **Backend server addresses**: "백엔드 서버는 10.0.1.1:8080, 10.0.1.2:8080, 10.0.1.3:8080이야"
- **Certificate authorities**: "DigiCert 인증서를 사용하고 싶어"
- **Configuration options**: "least_conn 알고리즘으로 로드 밸런싱해줘"
- **Document roots**: "api.example.com 서브도메인을 /var/www/api 경로로 설정해줘"
- **Environment names**: "staging 환경의 설정을 백업해줘"
- **Error messages**: "upstream timeout (110: Connection timed out) connecting to backend 에러가 발생해. 해결해줘"
- **File paths**: "/etc/nginx 설정을 백업해줘"

The skill automatically extracts relevant information from the user's natural language request and routes it to the appropriate web server expert.

## How to Use This Skill

When a user requests web server management tasks in natural language:

1. **Parse the user's natural language request**: Understand what the user wants to accomplish
2. **Identify the web server type**: Detect nginx, Apache, or IIS from the request (ask if unclear)
3. **Determine the action category**: Classify the request into one of the supported actions:
   - ssl, loadbalancer, subdomain, security, optimize, https-redirect, http2, backup, restore, or troubleshoot
4. **Extract context information**: Pull out relevant details from the user's message:
   - Domain names, backend servers, file paths, error messages, configuration options, etc.
5. **Route to specialized agent**: Use the Task tool to delegate to the appropriate expert:
   - nginx requests → nginx specialist agent
   - Apache requests → Apache specialist agent
   - IIS requests → IIS specialist agent
6. **Provide comprehensive input**: Pass the action type and all extracted context to the expert agent
7. **Present expert guidance**: Return production-ready configuration recommendations and step-by-step instructions

**Example workflow:**
- User says: "nginx에서 502 bad gateway 에러가 발생해. upstream timeout 메시지가 보여"
- Skill identifies: web server=nginx, action=troubleshoot, context="502 bad gateway, upstream timeout"
- Routes to nginx expert agent with troubleshooting request and error details
- Returns diagnostic steps and configuration fixes

Each expert agent provides tailored, production-ready guidance optimized for their respective web server.
