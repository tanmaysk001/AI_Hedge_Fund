# 🚀 Docker Quick Start (5 Minutes)

**Never used Docker before? This guide gets you running in 5 minutes!**

---

## ⚡ Super Quick Start

### Step 1: Install Docker (2 minutes)

**Windows/Mac:**
1. Download Docker Desktop: https://www.docker.com/products/docker-desktop
2. Install and restart your computer
3. Open Docker Desktop (wait for it to start)

**Linux:**
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Log out and back in
```

### Step 2: Set Up Your Project (1 minute)

```bash
# Go to project directory
cd "E:\AI Projects\ai-hedge-fund-main"

# Create .env file with your API keys
# Windows:
copy .env.example .env

# Mac/Linux:
cp .env.example .env

# Edit .env and add your API keys:
# OPENAI_API_KEY=sk-your-key-here
# GROQ_API_KEY=gsk-your-key-here
# ALPHA_VANTAGE_API_KEY=your-key-here
```

### Step 3: Run Your First Analysis (2 minutes)

**Option A: Using the helper scripts (EASIEST)**

**Windows:**
```batch
docker-run.bat AAPL
```

**Mac/Linux:**
```bash
chmod +x docker-run.sh
./docker-run.sh AAPL
```

**Option B: Using docker-compose directly**

```bash
# First time: Build the image (takes 3-5 minutes)
docker-compose build

# Run analysis
docker-compose run --rm hedge-fund --ticker AAPL
```

**That's it!** 🎉 You just ran your first Docker-based hedge fund analysis!

---

## 🎯 Common Commands

```bash
# Analyze one stock
docker-compose run --rm hedge-fund --ticker AAPL

# Analyze multiple stocks
docker-compose run --rm hedge-fund --ticker AAPL,MSFT,NVDA

# Show detailed reasoning
docker-compose run --rm hedge-fund --ticker AAPL --show-reasoning

# Run backtester
docker-compose run --rm hedge-fund python src/backtester.py --ticker AAPL

# Get into the container (for debugging)
docker-compose run --rm hedge-fund bash
```

---

## 🆘 Troubleshooting

### "docker: command not found"
- Docker is not installed
- Install Docker Desktop and restart

### "permission denied" (Linux only)
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

### "Cannot connect to Docker daemon"
- Docker Desktop is not running
- Open Docker Desktop and wait for it to start

### Analysis exits immediately
```bash
# Check if .env file has correct API keys
cat .env  # Linux/Mac
type .env # Windows

# View error logs
docker-compose logs
```

---

## 📚 Want to Learn More?

Read the complete guide: **DOCKER_GUIDE.md**

Contains:
- Detailed explanations
- Advanced usage
- Performance tips
- Security best practices
- Real-world examples

---

## 💡 Pro Tips

1. **First run is slow** (builds image) - subsequent runs are fast
2. **Cache is saved** - API responses are cached locally
3. **Results persist** - Output saved to `./output/` directory
4. **Clean up** - Run `docker system prune` occasionally

---

## 🎓 What's Happening Behind the Scenes?

```
You run: docker-compose run --rm hedge-fund --ticker AAPL
         ↓
Docker creates an isolated container with:
  ✓ Python 3.11
  ✓ All dependencies installed
  ✓ Your code
  ✓ Your API keys
         ↓
Runs the analysis inside the container
         ↓
Saves results to your local machine
         ↓
Removes the container (--rm flag)
```

**Benefits:**
- ✅ No Python installation needed on your machine
- ✅ No dependency conflicts
- ✅ Same environment on any computer
- ✅ Easy to share and deploy

---

**You're all set!** 🚀 For more details, see **DOCKER_GUIDE.md**

