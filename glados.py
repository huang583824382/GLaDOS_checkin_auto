.github/workflows/checkin.yml
name: GLaDOS 2026 Checkin

on:
  workflow_dispatch:
    inputs:
      dispatch_source:
        description: 'manual or external'
        required: false
        default: 'manual'
      diagnose_only:
        description: 'Only check login status'
        required: false
        type: boolean
        default: false
  schedule:
    - cron: '30 1 * * *'
  watch:
    types: [started]

jobs:
  checkin:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install requests

      - name: Run GLaDOS checkin
        run: python3 glados.py
        env:
          GLADOS_COOKIE: ${{ secrets.GLADOS_COOKIE }}
          GLADOS_USER_AGENT: ${{ vars.GLADOS_USER_AGENT }}
          PUSHPLUS_TOKEN: ${{ secrets.PUSHPLUS_TOKEN }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
          PUSH_LEVEL: ${{ vars.PUSH_LEVEL }}
          EXCHANGE_PLAN: ${{ vars.EXCHANGE_PLAN }}
          CHECKIN_DIAGNOSTIC_ONLY: ${{ github.event.inputs.diagnose_only }}
          CHECKIN_MAX_ATTEMPTS: '3'
          CHECKIN_RETRY_DELAY_SECONDS: '60'

      - name: Keepalive workflow
        uses: gautamkrishnar/keepalive-workflow@master

"}]} ivoq