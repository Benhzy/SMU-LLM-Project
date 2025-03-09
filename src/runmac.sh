#!/bin/bash

echo "Legal Analysis Simulation System"
echo "================================"

# PARSE COMMAND LINE ARGUMENTS. EDIT HERE 
MODEL="deepseek-chat"
QUESTION="How has the principle of 'duty of care' evolved over time? Focus specifically on the legal frameworks used."

# UNUSED! flag for potential Q&A based on result
INTERACTIVE=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --model)
      MODEL="$2"
      shift 2
      ;;
    --interactive)
      INTERACTIVE="--interactive"
      shift
      ;;
    --question)
      QUESTION="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1"
      shift
      ;;
  esac
done

# If model not provided via command line, prompt the user
if [ -z "$MODEL" ]; then
  echo
  echo "Select a model:"
  echo "1. gpt-4o-mini"
  echo "2. gpt-4o"
  echo "3. claude-3-opus"
  echo "4. claude-3-sonnet"
  echo "5. command-r-plus"
  echo
  read -p "Enter your choice (1-5, or enter a custom model name): " MODEL_CHOICE
  
  case $MODEL_CHOICE in
    1) MODEL="gpt-4o-mini" ;;
    2) MODEL="gpt-4o" ;;
    3) MODEL="claude-3-opus" ;;
    4) MODEL="claude-3-sonnet" ;;
    5) MODEL="command-r-plus" ;;
    [1-5]) ;; # Do nothing for valid numbers already handled
    *)
      # If not a number 1-5, assume it's a custom model name
      if [ ! -z "$MODEL_CHOICE" ]; then
        MODEL="$MODEL_CHOICE"
      fi
      ;;
  esac
fi

# If question not provided via command line, prompt for it
if [ -z "$QUESTION" ]; then
  echo
  echo "You can provide your legal question now, or leave it blank to be prompted later."
  echo
  read -p "Enter your legal question (or press Enter to be prompted during execution): " QUESTION
fi

# Build the command
CMD="python3 main.py"

# Add model if specified
if [ ! -z "$MODEL" ]; then
  CMD="$CMD --model \"$MODEL\""
fi

# Add interactive flag if specified
if [ ! -z "$INTERACTIVE" ]; then
  CMD="$CMD $INTERACTIVE"
fi

# Add question if specified
if [ ! -z "$QUESTION" ]; then
  CMD="$CMD --question \"$QUESTION\""
fi

echo
echo "Running command: $CMD"
echo

# Execute the command - using eval to handle the quotes in the command
eval $CMD

echo
echo "Analysis completed."
