# 🐳 Docker Guide for AI Hedge Fund

## 📚 Table of Contents
1. [What is Docker?](#what-is-docker)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Detailed Usage](#detailed-usage)
5. [Common Commands](#common-commands)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Usage](#advanced-usage)

---

## 🤔 What is Docker?

Docker is like a **shipping container for your application**. Just like how shipping containers allow goods to be transported anywhere in the world without worrying about compatibility, Docker containers allow your application to run anywhere without worrying about different operating systems or dependencies.

### Key Concepts:

**🏗️ Image**: A blueprint/template for your application
- Like a recipe that contains all instructions and ingredients
- Built once, can be used many times

**📦 Container**: A running instance of an image
- Like an actual cake made from a recipe
- Can have multiple containers from one image

**🐳 Dockerfile**: Instructions to build an image
- Step-by-step recipe for creating your application environment

**🎼 docker-compose.yml**: Configuration for running containers
- Easy way to configure and run your application with one command

---

## 💻 Installation

### Windows:
1. Download **Docker Desktop** from: https://www.docker.com/products/docker-desktop
2. Run the installer
3. Restart your computer
4. Verify installation:
```bash
docker --version
docker-compose --version
```

### macOS:
1. Download **Docker Desktop** from: https://www.docker.com/products/docker-desktop
2. Drag to Applications folder
3. Open Docker Desktop
4. Verify installation:
```bash
docker --version
docker-compose --version
```

### Linux (Ubuntu/Debian):
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group (avoid using sudo)
sudo usermod -aG docker $USER

# Log out and back in, then verify
docker --version
docker-compose --version
```

---

## 🚀 Quick Start (Absolute Beginner)

### Step 1: Prepare Your Environment File

Create a `.env` file in the project root with your API keys:

```bash
# Windows Command Prompt:
copy .env.example .env

# Windows PowerShell / macOS / Linux:
cp .env.example .env
```

Edit `.env` file with your actual API keys:
```
OPENAI_API_KEY=sk-your-openai-key-here
GROQ_API_KEY=gsk_your-groq-key-here
ALPHA_VANTAGE_API_KEY=your-alphavantage-key-here
```

### Step 2: Build the Docker Image

```bash
# Navigate to project directory
cd "E:\AI Projects\ai-hedge-fund-main"

# Build the image (first time takes 3-5 minutes)
docker-compose build
```

**What's happening?**
- Docker reads `Dockerfile` and `docker-compose.yml`
- Downloads Python and installs all dependencies
- Creates an optimized image with your application

### Step 3: Run Your First Analysis

```bash
# Run with default settings (analyzes AAPL)
docker-compose up

# Or analyze specific stocks
docker-compose run --rm hedge-fund --ticker AAPL,MSFT --show-reasoning
```

**What's happening?**
- Docker creates a container from your image
- Runs the hedge fund analysis inside the container
- Shows results in your terminal
- Saves cache to your local drive

That's it! Your first Docker analysis is complete! 🎉

---

## 📖 Detailed Usage

### Understanding the Project Structure

```
ai-hedge-fund-main/
├── Dockerfile              # Blueprint for building your app
├── docker-compose.yml      # Easy configuration for running
├── .dockerignore          # Files to exclude from Docker
├── .env                   # Your API keys (DON'T commit to git!)
├── src/                   # Your Python code
├── cache/                 # Cached API responses (created automatically)
├── output/                # Analysis results (created automatically)
└── logs/                  # Log files (created automatically)
```

### Method 1: Using docker-compose (Recommended)

**Most common and easiest method!**

```bash
# Basic analysis
docker-compose run --rm hedge-fund --ticker AAPL

# Multiple stocks with reasoning
docker-compose run --rm hedge-fund --ticker AAPL,MSFT,NVDA --show-reasoning

# Custom date range
docker-compose run --rm hedge-fund \
  --ticker AAPL \
  --start-date 2024-01-01 \
  --end-date 2024-12-31

# Run backtester
docker-compose run --rm hedge-fund python src/backtester.py --ticker AAPL,MSFT
```

**Flag Explanation:**
- `--rm`: Remove container after it finishes (keeps things clean)
- `hedge-fund`: Name of the service from docker-compose.yml

### Method 2: Using Docker directly

```bash
# Build image
docker build -t ai-hedge-fund:latest .

# Run analysis
docker run --rm \
  --env-file .env \
  -v "$(pwd)/cache:/app/.cache" \
  ai-hedge-fund:latest \
  --ticker AAPL,MSFT --show-reasoning
```

---

## 🛠️ Common Commands

### Building

```bash
# Build image
docker-compose build

# Rebuild from scratch (if you change dependencies)
docker-compose build --no-cache

# Build and run in one command
docker-compose up --build
```

### Running

```bash
# Run and remove container after
docker-compose run --rm hedge-fund --ticker AAPL

# Run in background (detached mode)
docker-compose up -d

# Run with specific command
docker-compose run --rm hedge-fund python src/backtester.py --ticker AAPL
```

### Managing Containers

```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Stop running container
docker-compose down

# Stop and remove everything (containers, networks)
docker-compose down --remove-orphans

# View logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f
```

### Cleaning Up

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove everything unused (BE CAREFUL!)
docker system prune -a

# Check disk usage
docker system df
```

---

## 🔧 Advanced Usage

### 1. Interactive Shell Access

Sometimes you want to "get inside" the container:

```bash
# Open bash shell in container
docker-compose run --rm hedge-fund bash

# Once inside, you can run commands manually:
python src/main.py --ticker AAPL
python src/backtester.py --ticker MSFT
exit  # to leave
```

### 2. Custom Configurations

Edit `docker-compose.yml` to customize:

```yaml
# Example: Change default command
services:
  hedge-fund:
    command: ["--ticker", "TSLA,NVDA", "--show-reasoning"]
```

### 3. Environment Variables

You can pass environment variables in multiple ways:

**Method 1: .env file (Recommended)**
```bash
# .env file
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...
```

**Method 2: Command line**
```bash
docker-compose run --rm \
  -e OPENAI_API_KEY=sk-... \
  -e GROQ_API_KEY=gsk_... \
  hedge-fund --ticker AAPL
```

**Method 3: In docker-compose.yml**
```yaml
services:
  hedge-fund:
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GROQ_API_KEY=${GROQ_API_KEY}
```

### 4. Mounting Additional Volumes

Want to save results to a specific folder?

```bash
# Add to docker-compose.yml under volumes:
volumes:
  - ./my-results:/app/output
  - ./my-cache:/app/.cache
```

### 5. Resource Limits

Edit `docker-compose.yml` to change resource limits:

```yaml
deploy:
  resources:
    limits:
      cpus: '4'      # Allow up to 4 CPU cores
      memory: 8G     # Allow up to 8GB RAM
```

---

## 🐛 Troubleshooting

### Problem 1: "docker: command not found"
**Solution**: Docker is not installed or not in PATH
```bash
# Verify Docker is installed
docker --version

# If not found, reinstall Docker Desktop
```

### Problem 2: "permission denied" (Linux)
**Solution**: Your user is not in docker group
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

### Problem 3: Build fails with "no space left on device"
**Solution**: Docker ran out of disk space
```bash
# Clean up unused data
docker system prune -a
docker volume prune
```

### Problem 4: Container exits immediately
**Solution**: Check logs for errors
```bash
docker-compose logs

# Or run with interactive mode to see errors
docker-compose run --rm hedge-fund --ticker AAPL
```

### Problem 5: API keys not working
**Solution**: Check .env file format
```bash
# .env should NOT have quotes or spaces
# WRONG:
OPENAI_API_KEY = "sk-..."

# CORRECT:
OPENAI_API_KEY=sk-...
```

### Problem 6: Slow build times
**Solution**: 
1. Make sure Docker Desktop has enough resources (Settings → Resources)
2. Use build cache: `docker-compose build`
3. Don't use `--no-cache` unless necessary

### Problem 7: Can't access files created by container
**Solution**: Files are owned by container user
```bash
# Windows/Mac: Should work automatically
# Linux: Change ownership
sudo chown -R $USER:$USER cache/ output/ logs/
```

---

## 📊 Real-World Examples

### Example 1: Daily Analysis Routine

```bash
# Morning: Analyze your watchlist
docker-compose run --rm hedge-fund \
  --ticker AAPL,MSFT,GOOGL,AMZN,TSLA \
  --show-reasoning

# Check output in ./output/ folder
```

### Example 2: Backtesting Strategy

```bash
# Test strategy over last year
docker-compose run --rm hedge-fund \
  python src/backtester.py \
  --ticker AAPL,MSFT \
  --start-date 2024-01-01 \
  --end-date 2024-12-31
```

### Example 3: Automated Daily Analysis (Cron/Task Scheduler)

**Linux/Mac (cron):**
```bash
# Edit crontab
crontab -e

# Add this line to run daily at 9 AM
0 9 * * * cd /path/to/ai-hedge-fund-main && docker-compose run --rm hedge-fund --ticker AAPL,MSFT
```

**Windows (Task Scheduler):**
Create a batch file `daily-analysis.bat`:
```batch
cd "E:\AI Projects\ai-hedge-fund-main"
docker-compose run --rm hedge-fund --ticker AAPL,MSFT
```
Then schedule it in Task Scheduler.

---

## 🎯 Best Practices

1. **Always use .env file** for API keys (never commit to git)
2. **Use docker-compose** instead of plain docker commands
3. **Use `--rm` flag** to automatically clean up containers
4. **Mount volumes** for cache and output directories
5. **Set resource limits** to prevent system slowdown
6. **Clean up regularly** with `docker system prune`
7. **Keep images updated** by rebuilding periodically

---

## 📈 Performance Tips

### 1. Cache API Responses
```bash
# First run: slow (makes API calls)
docker-compose run --rm hedge-fund --ticker AAPL

# Second run: fast (uses cache)
docker-compose run --rm hedge-fund --ticker AAPL
```

### 2. Parallel Analysis
```bash
# Analyze multiple stocks in separate containers
docker-compose run -d hedge-fund --ticker AAPL &
docker-compose run -d hedge-fund --ticker MSFT &
docker-compose run -d hedge-fund --ticker NVDA &
```

### 3. Use Smaller Models for Testing
```bash
# Fast testing with llama-3.1 8b
docker-compose run --rm hedge-fund --ticker AAPL
# Select "llama-3.1 8b [groq]" when prompted

# Final analysis with GPT-5.1
docker-compose run --rm hedge-fund --ticker AAPL --show-reasoning
# Select "gpt-5.1 [openai]" when prompted
```

---

## 🔐 Security Notes

1. **Never commit .env file** to git (it's in .gitignore)
2. **Use non-root user** (already configured in Dockerfile)
3. **Keep Docker updated** for security patches
4. **Scan images** for vulnerabilities:
```bash
docker scan ai-hedge-fund:latest
```

---

## 📝 Cheat Sheet

```bash
# BUILD
docker-compose build                 # Build image
docker-compose build --no-cache      # Rebuild from scratch

# RUN
docker-compose run --rm hedge-fund --ticker AAPL          # Single analysis
docker-compose up                                          # Run with default command
docker-compose up -d                                       # Run in background

# MANAGE
docker ps                           # List running containers
docker-compose logs                 # View logs
docker-compose down                 # Stop and remove containers

# CLEAN
docker-compose down --volumes       # Stop and remove volumes
docker system prune -a              # Clean everything unused

# DEBUG
docker-compose run --rm hedge-fund bash                   # Open shell
docker-compose logs -f                                     # Follow logs
```

---

## 🎓 Learning Resources

- **Docker Official Tutorial**: https://docs.docker.com/get-started/
- **Docker Compose Docs**: https://docs.docker.com/compose/
- **Interactive Tutorial**: https://www.docker.com/play-with-docker/

---

## 🆘 Still Need Help?

If you encounter issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Run `docker-compose logs` to see error messages
3. Make sure .env file has correct API keys
4. Verify Docker Desktop is running
5. Try rebuilding: `docker-compose build --no-cache`

---

**Last Updated**: January 2025
**Docker Version**: 24.0+
**Docker Compose Version**: 2.0+

