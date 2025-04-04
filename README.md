# FPL Fantasy Optimizer

FPL Fantasy Optimizer is a Python-based tool that fetches live data from the Fantasy Premier League (FPL) API and uses mathematical optimization to generate the best possible fantasy football squad. It not only selects an optimal 15-player squad under budget, positional, and club constraints, but also optimizes a starting 11 based on formation rules and selects a captain based on expected performance.

---

## Features

- **Live Data Retrieval:**  
  Fetches current player data from the FPL API.

- **Data Processing:**  
  Maps team and position IDs to readable names, converts player costs to millions, and calculates an adjusted expected points metric based on historical performance and recent form.

- **Advanced Optimization:**  
  - **Squad Selection:** Uses PuLP to select an optimal 15-player squad adhering to budget, positional, and club limitations.
  - **Starting 11 Optimization:** From the selected squad, optimizes a starting 11 lineup based on realistic formation constraints (e.g., exactly 1 goalkeeper, at least 3 defenders, 2 midfielders, and 1 forward).
  - **Captain Selection:** Automatically selects the captain from the starting 11 by choosing the player with the highest expected points.

- **Detailed Summary:**  
  Provides a breakdown of the squad's total cost and expected points along with similar metrics for the starting 11.

---

## Installation

### Prerequisites

- **Python 3.x**
- Required Python packages:
  - `requests`
  - `pandas`
  - `pulp`

### Installing Dependencies

Install the necessary packages using pip:

```bash
pip install requests pandas pulp
