#!/bin/bash

# Security Testing Orchestration Service Manager
# Manages Ollama LLM server and MCP containers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
OLLAMA_PORT=11434
MCP_SERVERS_DIR="mcp_servers"
REQUIRED_CONTAINERS=("mcp-kali" "mcp-websearch" "mcp-rag")

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Ollama is running
check_ollama() {
    if curl -s http://localhost:$OLLAMA_PORT/api/tags > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to check if Docker is running
check_docker() {
    if docker info > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to check if a container is running
check_container() {
    local container_name=$1
    if docker ps --format "table {{.Names}}" | grep -q "^$container_name$"; then
        return 0
    else
        return 1
    fi
}

# Function to start Ollama
start_ollama() {
    print_status "Starting Ollama server..."
    
    if check_ollama; then
        print_success "Ollama is already running"
        return 0
    fi
    
    # Check if Ollama is installed
    if ! command -v ollama &> /dev/null; then
        print_error "Ollama is not installed. Please install it first: https://ollama.ai/"
        return 1
    fi
    
    # Start Ollama in background
    ollama serve > /dev/null 2>&1 &
    local ollama_pid=$!
    
    # Wait for Ollama to start
    local attempts=0
    while [ $attempts -lt 30 ]; do
        if check_ollama; then
            print_success "Ollama started successfully (PID: $ollama_pid)"
            echo $ollama_pid > .ollama.pid
            return 0
        fi
        sleep 1
        attempts=$((attempts + 1))
    done
    
    print_error "Failed to start Ollama after 30 seconds"
    return 1
}

# Function to stop Ollama
stop_ollama() {
    print_status "Stopping Ollama server..."
    
    if [ -f .ollama.pid ]; then
        local pid=$(cat .ollama.pid)
        if kill -0 $pid 2>/dev/null; then
            kill $pid
            print_success "Ollama stopped (PID: $pid)"
        else
            print_warning "Ollama process not found"
        fi
        rm -f .ollama.pid
    else
        # Try to find and kill Ollama process
        local ollama_pid=$(pgrep ollama || true)
        if [ -n "$ollama_pid" ]; then
            kill $ollama_pid
            print_success "Ollama stopped (PID: $ollama_pid)"
        else
            print_warning "No Ollama process found"
        fi
    fi
}

# Function to start MCP containers
start_containers() {
    print_status "Starting MCP containers..."
    
    if ! check_docker; then
        print_error "Docker is not running. Please start Docker first."
        return 1
    fi
    
    if [ ! -d "$MCP_SERVERS_DIR" ]; then
        print_error "MCP servers directory not found: $MCP_SERVERS_DIR"
        return 1
    fi
    
    cd "$MCP_SERVERS_DIR"
    
    # Start containers
    docker-compose up -d
    
    # Wait for containers to be ready
    print_status "Waiting for containers to be ready..."
    local attempts=0
    while [ $attempts -lt 60 ]; do
        local all_running=true
        for container in "${REQUIRED_CONTAINERS[@]}"; do
            if ! check_container "$container"; then
                all_running=false
                break
            fi
        done
        
        if $all_running; then
            print_success "All MCP containers are running"
            cd ..
            return 0
        fi
        
        sleep 1
        attempts=$((attempts + 1))
    done
    
    print_error "Some containers failed to start after 60 seconds"
    cd ..
    return 1
}

# Function to stop MCP containers
stop_containers() {
    print_status "Stopping MCP containers..."
    
    if [ ! -d "$MCP_SERVERS_DIR" ]; then
        print_error "MCP servers directory not found: $MCP_SERVERS_DIR"
        return 1
    fi
    
    cd "$MCP_SERVERS_DIR"
    docker-compose down
    print_success "MCP containers stopped"
    cd ..
}

# Function to check all services
check_services() {
    print_status "Checking service status..."
    
    local all_ok=true
    
    # Check Ollama
    if check_ollama; then
        print_success "Ollama: Running"
    else
        print_error "Ollama: Not running"
        all_ok=false
    fi
    
    # Check Docker
    if check_docker; then
        print_success "Docker: Running"
    else
        print_error "Docker: Not running"
        all_ok=false
    fi
    
    # Check containers
    for container in "${REQUIRED_CONTAINERS[@]}"; do
        if check_container "$container"; then
            print_success "Container $container: Running"
        else
            print_error "Container $container: Not running"
            all_ok=false
        fi
    done
    
    if $all_ok; then
        print_success "All services are running correctly"
        return 0
    else
        print_error "Some services are not running"
        return 1
    fi
}

# Function to show logs
show_logs() {
    local service=$1
    
    case $service in
        "ollama")
            print_status "Ollama logs:"
            if [ -f .ollama.pid ]; then
                local pid=$(cat .ollama.pid)
                if kill -0 $pid 2>/dev/null; then
                    print_warning "Ollama is running but logs are not captured. Use 'ollama serve' directly for logs."
                else
                    print_error "Ollama is not running"
                fi
            else
                print_error "Ollama is not running"
            fi
            ;;
        "containers")
            print_status "Container logs:"
            if [ -d "$MCP_SERVERS_DIR" ]; then
                cd "$MCP_SERVERS_DIR"
                docker-compose logs --tail=50
                cd ..
            else
                print_error "MCP servers directory not found"
            fi
            ;;
        *)
            print_error "Unknown service: $service. Use 'ollama' or 'containers'"
            ;;
    esac
}

# Function to show usage
show_usage() {
    echo "Security Testing Orchestration Service Manager"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       Start all services (Ollama + MCP containers)"
    echo "  stop        Stop all services"
    echo "  restart     Restart all services"
    echo "  status      Check status of all services"
    echo "  logs [service] Show logs (service: ollama|containers)"
    echo "  clean       Stop all services and clean up"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 status"
    echo "  $0 logs containers"
    echo "  $0 clean"
}

# Main script logic
case "${1:-}" in
    "start")
        print_status "Starting all services..."
        start_ollama
        start_containers
        print_success "All services started successfully"
        ;;
    "stop")
        print_status "Stopping all services..."
        stop_containers
        stop_ollama
        print_success "All services stopped"
        ;;
    "restart")
        print_status "Restarting all services..."
        stop_containers
        stop_ollama
        sleep 2
        start_ollama
        start_containers
        print_success "All services restarted"
        ;;
    "status")
        check_services
        ;;
    "logs")
        show_logs "$2"
        ;;
    "clean")
        print_status "Cleaning up all services..."
        stop_containers
        stop_ollama
        rm -f .ollama.pid
        print_success "Cleanup completed"
        ;;
    *)
        show_usage
        exit 1
        ;;
esac 