#!/bin/bash
pkill -f "uvicorn main:app" 2>/dev/null || true
pkill -f "python main.py" 2>/dev/null || true
sleep 1
exec python main.py
