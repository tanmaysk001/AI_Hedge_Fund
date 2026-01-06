#!/bin/bash
# Easy Docker runner script for AI Hedge Fund
# Usage: ./docker-run.sh AAPL,MSFT

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐳 AI Hedge Fund Docker Runner${NC}"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker is not installed!${NC}"
    echo "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found!${NC}"
    echo "Creating .env from template..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ Created .env file${NC}"
        echo -e "${YELLOW}⚠️  Please edit .env and add your API keys before running again!${NC}"
        exit 1
    else
        echo -e "${YELLOW}⚠️  Please create a .env file with your API keys${NC}"
        exit 1
    fi
fi

# Build image if it doesn't exist
if ! docker images | grep -q "ai-hedge-fund"; then
    echo -e "${BLUE}📦 Building Docker image (first time, takes 3-5 minutes)...${NC}"
    docker-compose build
    echo -e "${GREEN}✓ Build complete!${NC}"
    echo ""
fi

# Get tickers from command line or use default
TICKERS=${1:-AAPL}
EXTRA_ARGS="${@:2}"

echo -e "${GREEN}📊 Analyzing: ${TICKERS}${NC}"
echo ""

# Run the analysis
docker-compose run --rm hedge-fund --ticker "${TICKERS}" ${EXTRA_ARGS}

echo ""
echo -e "${GREEN}✓ Analysis complete!${NC}"
echo -e "Check the ${BLUE}output/${NC} directory for results"

