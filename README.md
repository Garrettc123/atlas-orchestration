# ATLAS Orchestration ⚙️

> **LangGraph Workflow Engine + Redis Agent Coordination**  
> Garcar Enterprise — ATLAS Platform

[![CI](https://github.com/Garrettc123/atlas-orchestration/actions/workflows/ci.yml/badge.svg)](https://github.com/Garrettc123/atlas-orchestration/actions/workflows/ci.yml)

## Overview

Orchestrates all 7 ATLAS agents using a LangGraph state machine. Agents communicate via Redis pub/sub. The state graph enforces the lead pipeline and routes based on score and engagement.

## Flow

```
Lead In → Prospect → Qualify → Route
                                  ├─ hot/warm → Outreach → Converse → Schedule → Revenue → Analytics
                                  └─ cold     → Nurture Queue → Analytics
```

## Installation

```bash
pip install -r requirements.txt
```

## Testing

```bash
pytest tests/ -v
```
