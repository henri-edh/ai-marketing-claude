#!/bin/bash
# AI Marketing Suite — Claude Code Skills Installer
# Installs marketing skills, agents, and scripts into Claude Code

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   AI Marketing Suite — Claude Code Skills    ║${NC}"
echo -e "${CYAN}║   15 Skills · 5 Agents · 7 Scripts · PDF     ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════╝${NC}"
echo ""

# Detect script directory
if [ -n "$BASH_SOURCE" ] && [ "$BASH_SOURCE" != "bash" ] && [ -f "$BASH_SOURCE" ]; then
    SCRIPT_DIR="$(cd "$(dirname "$BASH_SOURCE")" && pwd)"
else
    # Running via curl | bash — need to clone
    echo -e "${YELLOW}Running remote install — cloning repository...${NC}"
    TEMP_DIR=$(mktemp -d)
    git clone --depth 1 https://github.com/zubair-trabzada/ai-marketing-claude.git "$TEMP_DIR/ai-marketing-claude" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to clone repository.${NC}"
        exit 1
    fi
    SCRIPT_DIR="$TEMP_DIR/ai-marketing-claude"
fi

# Target directories
SKILLS_DIR="$HOME/.claude/skills"
AGENTS_DIR="$HOME/.claude/agents"
VENV_DIR="$SKILLS_DIR/market/.venv"

echo -e "${BLUE}Source:${NC}  $SCRIPT_DIR"
echo -e "${BLUE}Target:${NC} $SKILLS_DIR"
echo ""

# Check if Claude Code is available
if command -v claude &>/dev/null; then
    echo -e "${GREEN}✓ Claude Code detected${NC}"
else
    echo -e "${YELLOW}⚠ Claude Code not found in PATH${NC}"
    if [ -t 0 ]; then
        read -p "  Continue anyway? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Installation cancelled."
            exit 0
        fi
    else
        echo "  Continuing (non-interactive mode)..."
    fi
fi

# Create directories
echo -e "\n${BLUE}Creating directories...${NC}"
mkdir -p "$SKILLS_DIR"
mkdir -p "$AGENTS_DIR"

# Install main skill orchestrator
echo -e "${BLUE}Installing main skill...${NC}"
mkdir -p "$SKILLS_DIR/market"
cp "$SCRIPT_DIR/market/SKILL.md" "$SKILLS_DIR/market/SKILL.md"
echo -e "  ${GREEN}✓${NC} market/SKILL.md (orchestrator)"

# Install sub-skills
echo -e "\n${BLUE}Installing sub-skills...${NC}"
SKILLS=(
    "market-audit"
    "market-copy"
    "market-emails"
    "market-social"
    "market-ads"
    "market-funnel"
    "market-competitors"
    "market-landing"
    "market-launch"
    "market-proposal"
    "market-report"
    "market-report-pdf"
    "market-seo"
    "market-brand"
)

SKILL_COUNT=0
for skill in "${SKILLS[@]}"; do
    if [ -f "$SCRIPT_DIR/skills/$skill/SKILL.md" ]; then
        mkdir -p "$SKILLS_DIR/$skill"
        cp "$SCRIPT_DIR/skills/$skill/SKILL.md" "$SKILLS_DIR/$skill/SKILL.md"
        echo -e "  ${GREEN}✓${NC} $skill"
        SKILL_COUNT=$((SKILL_COUNT + 1))
    else
        echo -e "  ${YELLOW}⚠${NC} $skill (not found, skipping)"
    fi
done

# Install shared guardrails used by multiple skills and agents
echo -e "\n${BLUE}Installing shared skill resources...${NC}"
if [ -f "$SCRIPT_DIR/skills/ACCURACY-GUARDRAILS.md" ]; then
    cp "$SCRIPT_DIR/skills/ACCURACY-GUARDRAILS.md" "$SKILLS_DIR/ACCURACY-GUARDRAILS.md"
    echo -e "  ${GREEN}✓${NC} ACCURACY-GUARDRAILS.md"
else
    echo -e "  ${YELLOW}⚠${NC} ACCURACY-GUARDRAILS.md (not found, skipping)"
fi

# Install agents
echo -e "\n${BLUE}Installing agents...${NC}"
AGENTS=(
    "market-content"
    "market-conversion"
    "market-competitive"
    "market-technical"
    "market-strategy"
)

AGENT_COUNT=0
for agent in "${AGENTS[@]}"; do
    if [ -f "$SCRIPT_DIR/agents/$agent.md" ]; then
        cp "$SCRIPT_DIR/agents/$agent.md" "$AGENTS_DIR/$agent.md"
        echo -e "  ${GREEN}✓${NC} $agent"
        AGENT_COUNT=$((AGENT_COUNT + 1))
    else
        echo -e "  ${YELLOW}⚠${NC} $agent (not found, skipping)"
    fi
done

# Install scripts
echo -e "\n${BLUE}Installing scripts...${NC}"
SCRIPTS_TARGET="$SKILLS_DIR/market/scripts"
mkdir -p "$SCRIPTS_TARGET"

SCRIPT_FILES=(
    "analyze_page.py"
    "collect_seo_evidence.py"
    "competitor_scanner.py"
    "generate_pdf_report.py"
    "generate_seo_audit_report.py"
    "social_calendar.py"
    "verify_rendered_seo.py"
)

SCRIPT_COUNT=0
for script in "${SCRIPT_FILES[@]}"; do
    if [ -f "$SCRIPT_DIR/scripts/$script" ]; then
        cp "$SCRIPT_DIR/scripts/$script" "$SCRIPTS_TARGET/$script"
        chmod +x "$SCRIPTS_TARGET/$script"
        echo -e "  ${GREEN}✓${NC} $script"
        SCRIPT_COUNT=$((SCRIPT_COUNT + 1))
    else
        echo -e "  ${YELLOW}⚠${NC} $script (not found, skipping)"
    fi
done

# Install templates
echo -e "\n${BLUE}Installing templates...${NC}"
TEMPLATES_TARGET="$SKILLS_DIR/market/templates"
mkdir -p "$TEMPLATES_TARGET"

TEMPLATE_COUNT=0
if [ -d "$SCRIPT_DIR/templates" ]; then
    for template in "$SCRIPT_DIR/templates"/*.md; do
        if [ -f "$template" ]; then
            cp "$template" "$TEMPLATES_TARGET/$(basename "$template")"
            echo -e "  ${GREEN}✓${NC} $(basename "$template")"
            TEMPLATE_COUNT=$((TEMPLATE_COUNT + 1))
        fi
    done
fi

# Install Python dependencies with UV
echo -e "\n${BLUE}Setting up Python environment with UV...${NC}"

# Check for UV
if ! command -v uv &>/dev/null; then
    echo -e "${YELLOW}⚠${NC} UV not found. Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install UV. Please install manually: https://github.com/astral-sh/uv${NC}"
        echo -e "${YELLOW}Falling back to system Python...${NC}"
        UV_AVAILABLE=false
    else
        UV_AVAILABLE=true
        echo -e "  ${GREEN}✓${NC} UV installed"
    fi
else
    UV_AVAILABLE=true
    UV_VERSION=$(uv --version 2>/dev/null)
    echo -e "  ${GREEN}✓${NC} UV $UV_VERSION detected"
fi

# Set up Python environment
if [ "$UV_AVAILABLE" = true ]; then
    # Create virtual environment with UV
    echo -e "${BLUE}Creating Python virtual environment...${NC}"
    if [ -f "$SCRIPT_DIR/.python-version" ]; then
        PYTHON_VERSION=$(cat "$SCRIPT_DIR/.python-version")
        uv venv --python "$PYTHON_VERSION" "$VENV_DIR" 2>/dev/null || uv venv "$VENV_DIR"
    else
        uv venv "$VENV_DIR"
    fi
    echo -e "  ${GREEN}✓${NC} Virtual environment created at $VENV_DIR"

    # Install dependencies with UV
    echo -e "${BLUE}Installing Python dependencies...${NC}"
    if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
        UV_PYTHON="$VENV_DIR/bin/python"
        "$VENV_DIR/bin/uv" pip install -r "$SCRIPT_DIR/requirements.txt" --python "$UV_PYTHON" 2>/dev/null || true
        echo -e "  ${GREEN}✓${NC} Dependencies installed with UV"
    fi

    # Check for reportlab
    if "$VENV_DIR/bin/python" -c "import reportlab" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} reportlab installed (PDF reports ready)"
    else
        echo -e "  ${YELLOW}⚠${NC} reportlab not installed (needed for PDF reports)"
        echo -e "    Install with: ${CYAN}uv pip install reportlab --python $VENV_DIR/bin/python${NC}"
    fi
else
    echo -e "  ${YELLOW}⚠${NC} UV not available — scripts will use system Python"
    if command -v python3 &>/dev/null; then
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
        echo -e "  ${GREEN}✓${NC} Python $PYTHON_VERSION detected (system)"
    else
        echo -e "  ${RED}✗${NC} Python 3 not found — scripts won't work"
        echo -e "    Install Python: ${CYAN}https://python.org${NC}"
    fi
fi

# Create Python helper script for UV environment
echo -e "\n${BLUE}Creating Python helper script...${NC}"
cat > "$SKILLS_DIR/market/python-env.sh" << 'ENVEOF'
#!/bin/bash
# Python environment helper for AI Marketing Suite
# This script ensures Python scripts run with the correct UV-managed virtual environment

MARKET_SKILLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$MARKET_SKILLS_DIR/.venv"

# Use UV venv if available, otherwise fall back to system Python
if [ -f "$VENV_DIR/bin/python" ]; then
    exec "$VENV_DIR/bin/python" "$@"
elif command -v uv &>/dev/null; then
    exec uv run python "$@"
elif command -v python3 &>/dev/null; then
    exec python3 "$@"
else
    echo "Error: No Python environment found" >&2
    exit 1
fi
ENVEOF
chmod +x "$SKILLS_DIR/market/python-env.sh"
echo -e "  ${GREEN}✓${NC} Python helper script created"

# Cleanup temp directory if used
if [ -n "$TEMP_DIR" ] && [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
fi

# Summary
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           Installation Complete!              ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Skills installed:    ${GREEN}$SKILL_COUNT${NC}"
echo -e "  Agents installed:    ${GREEN}$AGENT_COUNT${NC}"
echo -e "  Scripts installed:   ${GREEN}$SCRIPT_COUNT${NC}"
echo -e "  Templates installed: ${GREEN}$TEMPLATE_COUNT${NC}"
if [ "$UV_AVAILABLE" = true ]; then
    echo -e "  Python environment:  ${GREEN}UV (managed)${NC}"
else
    echo -e "  Python environment:  ${YELLOW}System Python${NC}"
fi
echo ""
echo -e "${CYAN}Available Commands:${NC}"
echo "  /market audit <url>        Full marketing audit (5 parallel agents)"
echo "  /market quick <url>        60-second marketing snapshot"
echo "  /market copy <url>         Generate optimized copy"
echo "  /market emails <topic>     Generate email sequences"
echo "  /market social <topic>     Social media content calendar"
echo "  /market ads <url>          Ad creative and copy"
echo "  /market funnel <url>       Sales funnel analysis"
echo "  /market competitors <url>  Competitive intelligence"
echo "  /market landing <url>      Landing page CRO"
echo "  /market launch <product>   Launch playbook"
echo "  /market proposal <client>  Client proposal generator"
echo "  /market report <url>       Marketing report (Markdown)"
echo "  /market report-pdf <url>   Marketing report (PDF)"
echo "  /market seo <url>          SEO content audit"
echo "  /market brand <url>        Brand voice analysis"
echo ""
echo -e "${CYAN}SEO Rendered Verification:${NC}"
echo "  Default provider: Browserless"
echo "  Set BROWSERLESS_TOKEN before running scripts/verify_rendered_seo.py directly"
echo "  Use --provider local-playwright-cli as a local fallback"
echo ""
echo -e "  ${YELLOW}Start a new Claude Code session to use the skills.${NC}"
echo ""
