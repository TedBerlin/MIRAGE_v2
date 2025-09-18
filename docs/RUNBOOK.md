# MIRAGE v2 - Operational Runbook

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Deployment Procedures](#deployment-procedures)
4. [Monitoring & Alerting](#monitoring--alerting)
5. [Troubleshooting](#troubleshooting)
6. [Maintenance Procedures](#maintenance-procedures)
7. [Security Procedures](#security-procedures)
8. [Backup & Recovery](#backup--recovery)
9. [Performance Tuning](#performance-tuning)
10. [Emergency Procedures](#emergency-procedures)

## Overview

This runbook provides comprehensive operational procedures for MIRAGE v2, including deployment, monitoring, troubleshooting, and maintenance procedures.

### System Components
- **MIRAGE v2 Application**: Main AI system
- **ChromaDB**: Vector database for embeddings
- **Redis**: Caching and session storage
- **Prometheus**: Metrics collection
- **Grafana**: Monitoring dashboards
- **Nginx**: Reverse proxy and load balancer

### Service Ports
- **8000**: MIRAGE API
- **8080**: MIRAGE Dashboard
- **8001**: ChromaDB
- **6379**: Redis
- **9090**: Prometheus
- **3000**: Grafana
- **80/443**: Nginx

## System Architecture

### Production Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Load Balancer (Nginx)                   │
│                         Port 80/443                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                    MIRAGE v2 Services                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   MIRAGE    │  │  ChromaDB   │  │    Redis    │        │
│  │ Application │  │   Vector    │  │    Cache    │        │
│  │  Port 8000  │  │  Port 8001  │  │  Port 6379  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Prometheus  │  │   Grafana   │  │   MIRAGE    │        │
│  │  Metrics    │  │  Dashboard  │  │  Dashboard  │        │
│  │  Port 9090  │  │  Port 3000  │  │  Port 8080  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow
1. **User Request** → Nginx → MIRAGE API
2. **Query Processing** → RAG Engine → ChromaDB
3. **Agent Processing** → Gemini API → Response Generation
4. **Caching** → Redis → Performance Optimization
5. **Monitoring** → Prometheus → Grafana

## Deployment Procedures

### Initial Deployment

#### Prerequisites
- Docker and Docker Compose installed
- GEMINI_API_KEY configured
- Minimum 4GB RAM, 10GB disk space
- Network access to Gemini API

#### Deployment Steps
```bash
# 1. Clone repository
git clone <repository-url>
cd MIRAGE_v2

# 2. Configure environment
cp .env.template .env
# Edit .env with your configuration

# 3. Deploy application
./scripts/deploy.sh production

# 4. Verify deployment
./scripts/deploy.sh status
```

#### Verification Checklist
- [ ] All containers running
- [ ] API health check passing
- [ ] Dashboard accessible
- [ ] ChromaDB responding
- [ ] Redis connected
- [ ] Prometheus collecting metrics
- [ ] Grafana dashboards loaded

### Updates and Upgrades

#### Rolling Update Procedure
```bash
# 1. Create backup
./scripts/deploy.sh backup

# 2. Pull latest changes
git pull origin main

# 3. Rebuild and deploy
./scripts/deploy.sh production

# 4. Verify update
./scripts/deploy.sh status
```

#### Rollback Procedure
```bash
# 1. Stop current deployment
docker-compose down

# 2. Restore from backup
./scripts/restore.sh <backup_name>

# 3. Restart services
docker-compose up -d
```

## Monitoring & Alerting

### Key Metrics

#### System Metrics
- **CPU Usage**: < 80%
- **Memory Usage**: < 85%
- **Disk Usage**: < 90%
- **Network I/O**: Monitor for anomalies

#### Application Metrics
- **Response Time**: < 5 seconds
- **Success Rate**: > 95%
- **Error Rate**: < 5%
- **Query Throughput**: Monitor trends

#### RAG Metrics
- **Document Processing**: Success rate
- **Embedding Generation**: Performance
- **Vector Search**: Response time
- **Cache Hit Rate**: > 80%

### Alerting Rules

#### Critical Alerts
- **Service Down**: Any service unavailable
- **High Error Rate**: > 10% error rate
- **High Response Time**: > 10 seconds
- **Disk Space**: < 5% free space

#### Warning Alerts
- **High CPU**: > 80% CPU usage
- **High Memory**: > 85% memory usage
- **Low Cache Hit Rate**: < 60%
- **High Query Latency**: > 5 seconds

### Monitoring Dashboards

#### Grafana Dashboards
- **System Overview**: CPU, memory, disk, network
- **Application Performance**: Response times, throughput
- **RAG System**: Document processing, embeddings
- **Error Analysis**: Error rates, types, trends

#### Access URLs
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **MIRAGE Dashboard**: http://localhost:8080

## Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check container logs
docker-compose logs <service_name>

# Check container status
docker-compose ps

# Restart specific service
docker-compose restart <service_name>
```

#### API Not Responding
```bash
# Check API health
curl http://localhost:8000/health

# Check API logs
docker-compose logs mirage

# Check network connectivity
docker network ls
docker network inspect mirage-network
```

#### ChromaDB Issues
```bash
# Check ChromaDB status
curl http://localhost:8001/api/v1/heartbeat

# Check ChromaDB logs
docker-compose logs chromadb

# Restart ChromaDB
docker-compose restart chromadb
```

#### High Memory Usage
```bash
# Check memory usage
docker stats

# Check application logs for memory leaks
docker-compose logs mirage | grep -i memory

# Restart application
docker-compose restart mirage
```

### Performance Issues

#### Slow Query Response
1. Check system resources (CPU, memory)
2. Review query logs for patterns
3. Check ChromaDB performance
4. Verify Redis cache hit rate
5. Monitor Gemini API response times

#### High Error Rate
1. Check application logs
2. Verify API key validity
3. Check network connectivity
4. Review error patterns
5. Check system resources

### Log Analysis

#### Log Locations
- **Application**: `logs/mirage.log`
- **Docker**: `docker-compose logs`
- **System**: `/var/log/`

#### Log Analysis Commands
```bash
# View recent errors
docker-compose logs mirage | grep ERROR

# Monitor logs in real-time
docker-compose logs -f mirage

# Search for specific patterns
docker-compose logs mirage | grep "query_id"
```

## Maintenance Procedures

### Daily Tasks
- [ ] Check system health
- [ ] Review error logs
- [ ] Monitor performance metrics
- [ ] Verify backup completion

### Weekly Tasks
- [ ] Review performance trends
- [ ] Update security patches
- [ ] Clean up old logs
- [ ] Verify monitoring alerts

### Monthly Tasks
- [ ] Review capacity planning
- [ ] Update dependencies
- [ ] Security audit
- [ ] Performance optimization

### Log Rotation
```bash
# Configure log rotation
sudo nano /etc/logrotate.d/mirage

# Log rotation configuration
/var/log/mirage/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 mirage mirage
}
```

### Database Maintenance

#### ChromaDB Maintenance
```bash
# Check ChromaDB status
curl http://localhost:8001/api/v1/heartbeat

# Backup ChromaDB data
docker exec chromadb tar -czf /backup/chromadb_$(date +%Y%m%d).tar.gz /chroma/chroma

# Restore ChromaDB data
docker exec chromadb tar -xzf /backup/chromadb_20240101.tar.gz -C /
```

#### Redis Maintenance
```bash
# Check Redis status
docker exec redis redis-cli ping

# Clear Redis cache
docker exec redis redis-cli FLUSHALL

# Monitor Redis memory
docker exec redis redis-cli INFO memory
```

## Security Procedures

### Access Control
- **API Keys**: Rotate monthly
- **Passwords**: Strong passwords, 90-day rotation
- **SSH Keys**: Regular rotation
- **User Accounts**: Regular review

### Security Monitoring
- **Failed Login Attempts**: Monitor and alert
- **Unusual API Usage**: Monitor patterns
- **Network Traffic**: Monitor for anomalies
- **File Integrity**: Regular checksums

### Vulnerability Management
```bash
# Scan for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image mirage:v2

# Update dependencies
pip install --upgrade -r requirements.txt

# Security audit
bandit -r src/
```

### Incident Response
1. **Identify**: Detect security incident
2. **Contain**: Isolate affected systems
3. **Eradicate**: Remove threat
4. **Recover**: Restore normal operations
5. **Learn**: Post-incident review

## Backup & Recovery

### Backup Strategy
- **Daily**: Application data and configuration
- **Weekly**: Full system backup
- **Monthly**: Long-term archive

### Backup Procedures
```bash
# Create backup
./scripts/backup.sh

# List available backups
ls -la backups/

# Restore from backup
./scripts/restore.sh <backup_name>
```

### Recovery Procedures

#### Full System Recovery
1. Stop all services
2. Restore from backup
3. Verify data integrity
4. Restart services
5. Run health checks

#### Partial Recovery
1. Identify affected components
2. Restore specific data
3. Verify functionality
4. Monitor for issues

### Disaster Recovery
- **RTO**: 4 hours (Recovery Time Objective)
- **RPO**: 1 hour (Recovery Point Objective)
- **Backup Location**: Off-site storage
- **Recovery Site**: Secondary data center

## Performance Tuning

### System Optimization
```bash
# Optimize Docker settings
echo 'vm.max_map_count=262144' >> /etc/sysctl.conf
sysctl -p

# Optimize file limits
echo '* soft nofile 65536' >> /etc/security/limits.conf
echo '* hard nofile 65536' >> /etc/security/limits.conf
```

### Application Tuning
- **Cache Settings**: Optimize TTL values
- **Connection Pooling**: Tune pool sizes
- **Memory Allocation**: Optimize heap sizes
- **Thread Pools**: Tune thread counts

### Database Tuning
- **ChromaDB**: Optimize index settings
- **Redis**: Tune memory settings
- **Connection Limits**: Optimize pool sizes

### Monitoring Performance
- **Response Times**: Track trends
- **Throughput**: Monitor capacity
- **Resource Usage**: Optimize allocation
- **Error Rates**: Minimize failures

## Emergency Procedures

### Service Outage
1. **Assess**: Determine scope of outage
2. **Communicate**: Notify stakeholders
3. **Contain**: Prevent further issues
4. **Resolve**: Fix root cause
5. **Recover**: Restore full service
6. **Review**: Post-incident analysis

### Data Loss
1. **Stop**: Halt all operations
2. **Assess**: Determine data loss scope
3. **Restore**: Recover from backup
4. **Verify**: Validate data integrity
5. **Resume**: Restart operations
6. **Investigate**: Root cause analysis

### Security Breach
1. **Detect**: Identify breach
2. **Contain**: Isolate affected systems
3. **Assess**: Determine impact
4. **Eradicate**: Remove threat
5. **Recover**: Restore operations
6. **Report**: Notify authorities

### Contact Information
- **On-Call Engineer**: +1-XXX-XXX-XXXX
- **Security Team**: security@company.com
- **Management**: management@company.com
- **Vendor Support**: support@vendor.com

### Escalation Procedures
1. **Level 1**: On-call engineer (0-30 min)
2. **Level 2**: Senior engineer (30-60 min)
3. **Level 3**: Architecture team (60+ min)
4. **Level 4**: Vendor support (as needed)

## Conclusion

This runbook provides comprehensive operational procedures for MIRAGE v2. Regular review and updates ensure procedures remain current and effective.

For additional support or questions, refer to the documentation or contact the operations team.
