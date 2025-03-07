#!/bin/bash
# Start backend applications
python3 worker1.py &
python3 worker2.py &
python3 worker3.py &
