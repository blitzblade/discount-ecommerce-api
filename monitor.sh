#!/bin/bash

# Application Monitoring Script
# This script monitors the health and performance of the deployed Django application

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[HEADER]${NC} $1"
}

# Get current timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "🔍 Application Monitoring Report - $TIMESTAMP"
echo "=================================================="

# Check Docker containers
print_header "Docker Container Status"
if docker-compose ps | grep -q "Up"; then
    print_status "All containers are running"
    docker-compose ps
else
    print_error "Some containers are not running"
    docker-compose ps
fi

# Check disk usage
print_header "Disk Usage"
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    print_warning "Disk usage is high: ${DISK_USAGE}%"
elif [ "$DISK_USAGE" -gt 90 ]; then
    print_error "Disk usage is critical: ${DISK_USAGE}%"
else
    print_status "Disk usage is normal: ${DISK_USAGE}%"
fi
df -h /

# Check memory usage
print_header "Memory Usage"
MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.2f", $3/$2 * 100.0}')
print_status "Memory usage: ${MEMORY_USAGE}%"
free -h

# Check CPU usage
print_header "CPU Usage"
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')
print_status "CPU usage: ${CPU_USAGE}%"

# Check application health
print_header "Application Health Check"
if curl -f -s https://localhost/admin/ > /dev/null; then
    print_status "Application is responding to HTTPS requests"
else
    print_error "Application is not responding to HTTPS requests"
fi

if curl -f -s http://localhost/admin/ > /dev/null; then
    print_status "Application is responding to HTTP requests"
else
    print_error "Application is not responding to HTTP requests"
fi

# Check SSL certificate
print_header "SSL Certificate Status"
if [ -f "ssl/cert.pem" ]; then
    CERT_EXPIRY=$(openssl x509 -enddate -noout -in ssl/cert.pem | cut -d= -f2)
    print_status "SSL certificate expires on: $CERT_EXPIRY"
    
    # Check if certificate expires within 30 days
    EXPIRY_DATE=$(date -d "$CERT_EXPIRY" +%s)
    CURRENT_DATE=$(date +%s)
    DAYS_LEFT=$(( ($EXPIRY_DATE - $CURRENT_DATE) / 86400 ))
    
    if [ "$DAYS_LEFT" -lt 30 ]; then
        print_warning "SSL certificate expires in $DAYS_LEFT days"
    else
        print_status "SSL certificate is valid for $DAYS_LEFT days"
    fi
else
    print_error "SSL certificate not found"
fi

# Check database connection
print_header "Database Connection"
if docker-compose exec -T db pg_isready -U elikem_user -d elikem_db > /dev/null 2>&1; then
    print_status "Database is accessible"
else
    print_error "Database is not accessible"
fi

# Check recent logs for errors
print_header "Recent Error Logs"
ERROR_COUNT=$(docker-compose logs --tail=100 | grep -i error | wc -l)
if [ "$ERROR_COUNT" -gt 0 ]; then
    print_warning "Found $ERROR_COUNT errors in recent logs"
    docker-compose logs --tail=50 | grep -i error | tail -5
else
    print_status "No recent errors found"
fi

# Check backup status
print_header "Backup Status"
if [ -d "/home/ubuntu/backups" ]; then
    LATEST_BACKUP=$(ls -t /home/ubuntu/backups/*.sql 2>/dev/null | head -1)
    if [ -n "$LATEST_BACKUP" ]; then
        BACKUP_AGE=$(( ($(date +%s) - $(stat -c %Y "$LATEST_BACKUP")) / 86400 ))
        print_status "Latest backup: $BACKUP_AGE days ago"
        if [ "$BACKUP_AGE" -gt 1 ]; then
            print_warning "Backup is older than 1 day"
        fi
    else
        print_warning "No database backups found"
    fi
else
    print_warning "Backup directory not found"
fi

# Check SSL renewal cron job
print_header "SSL Renewal Status"
if crontab -l 2>/dev/null | grep -q "certbot renew"; then
    print_status "SSL renewal cron job is configured"
else
    print_warning "SSL renewal cron job not found"
fi

# Performance metrics
print_header "Performance Metrics"
print_status "Docker container resource usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

# Network connectivity
print_header "Network Connectivity"
if ping -c 1 8.8.8.8 > /dev/null 2>&1; then
    print_status "Internet connectivity: OK"
else
    print_error "Internet connectivity: FAILED"
fi

# Security check
print_header "Security Status"
FIREWALL_STATUS=$(sudo ufw status | grep "Status")
print_status "Firewall: $FIREWALL_STATUS"

# Summary
echo ""
echo "📊 Monitoring Summary - $TIMESTAMP"
echo "=================================================="
print_status "Monitoring completed successfully"
print_status "Run this script regularly to monitor your application"
print_status "Consider setting up automated monitoring with cron"
echo ""
echo "🔧 Quick Commands:"
echo "   - View logs: docker-compose logs -f"
echo "   - Restart app: docker-compose restart"
echo "   - Backup: ./backup.sh"
echo "   - Update: git pull && docker-compose up -d --build"
echo "" 