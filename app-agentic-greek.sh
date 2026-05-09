#!/bin/bash
nohup streamlit run app-agentic-greek.py --server.port 8504 --server.address 0.0.0.0 > app-agentic.log 2>&1 &
