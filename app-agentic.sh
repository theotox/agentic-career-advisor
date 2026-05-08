#!/bin/bash
nohup streamlit run app-agentic.py --server.port 8503 --server.address 0.0.0.0 > app-agentic.log 2>&1 &
