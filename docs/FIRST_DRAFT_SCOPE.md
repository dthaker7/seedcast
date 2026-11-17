# Seedcast first-draft product scope

## Finalized idea

Seedcast is an educational Django application that helps beginning investors decide what to do with a small monthly surplus. The product starts with the user's income, expenses, debt payments, emergency savings, goals, and risk comfort. It calculates the amount left over, converts that amount into a simple allocation plan, and later connects the plan to uncertainty-aware market forecasts and goal simulations.

Seedcast uses paper-money simulations only and does not provide investment advice.

## Problem and target users

Young earners may have $50-$100 left after monthly expenses but lack a clear way to decide whether they are ready to invest, how much to set aside, and how to interpret market forecasts. Existing budgeting tools, stock screeners, and general chatbots usually address these questions separately.

The primary users are students, recent graduates, and other beginning investors with limited disposable income and market knowledge.

## Core value proposition

Seedcast puts the user's money picture before the market. It combines an understandable surplus calculation, a simple allocation, and forecasts that display ranges, confidence, and past performance rather than buy or sell labels.

## Three planned core features

1. **Money Snapshot and Seed Split:** Collect a financial profile, calculate monthly surplus, and divide it into three initial buckets—emergency savings, extra debt payoff, and paper-money practice—based on risk comfort and emergency savings.
2. **Cast Explorer and Report Card:** Display cached 21-trading-day forecasts for a curated market universe with P10-P90 ranges, probability of a gain, confidence, drivers, and measured performance against a baseline.
3. **Goal Simulator and grounded Copilot:** Simulate progress toward a saved goal and explain saved Seedcast calculations in plain language without inventing financial values or giving stock picks.

## Changes from P2-A2

The startup concept and nine-screen wireframe flow remain unchanged. Development ownership has been clarified to match the Team Contribution Contract:

- Parul owns the user money workflow and allocation.
- Suriyavardhan owns market data, market-facing screens, evaluation support, and LLM integration.
- Dhruv owns the predictive model, goal simulations, and shared visual patterns.

The first-draft implementation intentionally focuses on one complete database-backed workflow before expanding into the remaining feature apps.

## Current working workflow

`Account creation -> financial profile -> monthly budget form -> related database records -> dashboard surplus`

This workflow is implemented in Django and covered by automated tests.

