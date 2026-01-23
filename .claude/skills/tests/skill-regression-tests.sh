#!/bin/bash
# Skill Regression Tests
# Run before merging any skill changes to main
# Usage: bash .claude/skills/tests/skill-regression-tests.sh

set -e
SKILL_DIR=".claude/skills"
FAIL=0
TESTS_RUN=0
TESTS_PASSED=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check() {
    TESTS_RUN=$((TESTS_RUN + 1))
    local file="$1"
    local pattern="$2"
    local description="$3"

    if grep -q "$pattern" "$file" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $description"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}✗ FAIL:${NC} $description"
        echo "  Missing pattern: '$pattern' in $file"
        FAIL=1
        return 1
    fi
}

check_line_count() {
    TESTS_RUN=$((TESTS_RUN + 1))
    local file="$1"
    local max_lines="$2"
    local description="$3"

    local actual=$(wc -l < "$file" | tr -d ' ')
    if [ "$actual" -le "$max_lines" ]; then
        echo -e "${GREEN}✓${NC} $description ($actual lines)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}✗ FAIL:${NC} $description ($actual > $max_lines lines)"
        FAIL=1
        return 1
    fi
}

echo "========================================"
echo "       SKILL REGRESSION TESTS"
echo "========================================"
echo ""

# ============================================
# /start SKILL TESTS
# ============================================
echo -e "${YELLOW}Testing /start skill...${NC}"

START_FILE="$SKILL_DIR/start/SKILL.md"

# Critical content that was lost in refactoring
check "$START_FILE" "Recommended workflow" "/start has 'Recommended workflow' statement"
check "$START_FILE" "git pull origin main" "/start has git pull command"
check "$START_FILE" "Step -1: Pull Updates" "/start has Step -1 section"
check "$START_FILE" "Intent Keywords" "/start has Intent Keywords table"
check "$START_FILE" "Help Mode" "/start has Help Mode section"
check "$START_FILE" "Context Awareness" "/start has Context Awareness section"
check "$START_FILE" "Router, not worker" "/start has philosophy reminder"

# References must exist
check "$START_FILE" "config-system.md" "/start references config-system.md"
check "$START_FILE" "mcp-preflight.md" "/start references mcp-preflight.md"

# Skills should be documented
check "$START_FILE" "/think" "/start documents /think skill"
check "$START_FILE" "/ads" "/start documents /ads skill"
check "$START_FILE" "/setup" "/start documents /setup skill"
check "$START_FILE" "/content" "/start documents /content skill"
check "$START_FILE" "/wiki" "/start documents /wiki skill"
check "$START_FILE" "/pull" "/start documents /pull skill"
check "$START_FILE" "/deck" "/start documents /deck skill"

# Line count check (skill-creator says max 500)
check_line_count "$START_FILE" 500 "/start is under 500 lines"

echo ""

# ============================================
# /setup SKILL TESTS
# ============================================
echo -e "${YELLOW}Testing /setup skill...${NC}"

SETUP_FILE="$SKILL_DIR/setup/SKILL.md"

# Must use new config system
check "$SETUP_FILE" "~/.config/vip/local.yaml" "/setup uses new config path"
check "$SETUP_FILE" "mkdir -p .vip" "/setup creates .vip folder"
check "$SETUP_FILE" "config.yaml" "/setup creates config.yaml"

# Must have MCP tracking
check "$SETUP_FILE" "mcps:" "/setup includes mcps section in config"
check "$SETUP_FILE" "youtube-transcript" "/setup documents youtube-transcript MCP"

# Content lifecycle folders
check "$SETUP_FILE" "content/drafts" "/setup creates content/drafts"
check "$SETUP_FILE" "content/scheduled" "/setup creates content/scheduled"
check "$SETUP_FILE" "content/published" "/setup creates content/published"

# Critical gathering docs
check "$SETUP_FILE" "context-gathering.md" "/setup references context-gathering"

check_line_count "$SETUP_FILE" 500 "/setup is under 500 lines"

echo ""

# ============================================
# /think REFERENCES TESTS
# ============================================
echo -e "${YELLOW}Testing /think references...${NC}"

THINK_RESEARCH="$SKILL_DIR/think/references/research-phase.md"

# YouTube transcript section
check "$THINK_RESEARCH" "YouTube Transcript Research" "/think has YouTube transcript section"
check "$THINK_RESEARCH" "mcp__youtube-transcript__get_transcript" "/think documents transcript MCP tool"
check "$THINK_RESEARCH" "pull down this YouTube video" "/think has trigger phrases"

# Synthesis requirements
check "$THINK_RESEARCH" "20 words maximum" "/think has 20-word summary constraint"
check "$THINK_RESEARCH" "5-10 bullets" "/think has bullet count constraint"

echo ""

# ============================================
# REFERENCE FILE EXISTENCE TESTS
# ============================================
echo -e "${YELLOW}Testing reference file existence...${NC}"

# /start references
if [ -f "$SKILL_DIR/start/references/config-system.md" ]; then
    echo -e "${GREEN}✓${NC} config-system.md exists"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ FAIL:${NC} config-system.md missing"
    FAIL=1
fi
TESTS_RUN=$((TESTS_RUN + 1))

if [ -f "$SKILL_DIR/start/references/mcp-preflight.md" ]; then
    echo -e "${GREEN}✓${NC} mcp-preflight.md exists"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ FAIL:${NC} mcp-preflight.md missing"
    FAIL=1
fi
TESTS_RUN=$((TESTS_RUN + 1))

# /setup references
if [ -f "$SKILL_DIR/setup/references/context-gathering.md" ]; then
    echo -e "${GREEN}✓${NC} context-gathering.md exists"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ FAIL:${NC} context-gathering.md missing"
    FAIL=1
fi
TESTS_RUN=$((TESTS_RUN + 1))

echo ""
echo "========================================"
echo "           TEST SUMMARY"
echo "========================================"
echo "Tests run:    $TESTS_RUN"
echo "Tests passed: $TESTS_PASSED"
echo "Tests failed: $((TESTS_RUN - TESTS_PASSED))"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. Fix before merging.${NC}"
    exit 1
fi
