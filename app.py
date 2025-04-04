import requests
import pandas as pd
from pulp import LpProblem, LpVariable, lpSum, LpBinary, LpMaximize, LpStatus

def fetch_fpl_data():
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    response = requests.get(url)
    return response.json()

def prepare_data(data):
    # Create DataFrames
    players = pd.DataFrame(data["elements"])
    teams_df = pd.DataFrame(data["teams"])
    element_types_df = pd.DataFrame(data["element_types"])

    # Map team IDs to team names
    team_mapping = {row["id"]: row["name"] for _, row in teams_df.iterrows()}
    players["team_name"] = players["team"].map(team_mapping)

    # Map element type IDs to position names (Goalkeeper, Defender, Midfielder, Forward)
    position_mapping = {row["id"]: row["singular_name"] for _, row in element_types_df.iterrows()}
    players["position"] = players["element_type"].map(position_mapping)

    # Convert cost (tenths of a million) to millions
    players["price"] = players["now_cost"] / 10.0

    # Compute adjusted expected points using total_points and current form.
    # (Here we add a bonus factor: 2 * current form, where form is given as a string.)
    players["expected_points"] = players["total_points"] + 2 * players["form"].astype(float)

    # Create a full name column
    players["name"] = players["first_name"] + " " + players["second_name"]

    return players

def optimize_squad(players, budget=100.0):
    # Create the optimization problem for a 15-player squad.
    prob = LpProblem("FPL_Squad_Selection", LpMaximize)
    
    # Create decision variables for each player (1 if selected)
    player_vars = {i: LpVariable(f"player_{i}", cat=LpBinary) for i in players.index}

    # Objective: maximize total expected points over all selected players
    prob += lpSum(player_vars[i] * players.loc[i, "expected_points"] for i in players.index), "Total_Expected_Points"
    
    # Budget constraint
    prob += lpSum(player_vars[i] * players.loc[i, "price"] for i in players.index) <= budget, "Budget"
    
    # Total squad size must be 15 players
    prob += lpSum(player_vars[i] for i in players.index) == 15, "Total_Players"
    
    # Positional constraints (FPL squad rules)
    prob += lpSum(player_vars[i] for i in players.index if players.loc[i, "position"] == "Goalkeeper") == 2, "Goalkeepers"
    prob += lpSum(player_vars[i] for i in players.index if players.loc[i, "position"] == "Defender") == 5, "Defenders"
    prob += lpSum(player_vars[i] for i in players.index if players.loc[i, "position"] == "Midfielder") == 5, "Midfielders"
    prob += lpSum(player_vars[i] for i in players.index if players.loc[i, "position"] == "Forward") == 3, "Forwards"
    
    # Constraint: Maximum of 3 players per club
    for team in players["team_name"].unique():
        prob += lpSum(player_vars[i] for i in players.index if players.loc[i, "team_name"] == team) <= 3, f"ClubLimit_{team}"

    # Solve the optimization problem
    prob.solve()
    print("Squad Optimization Status:", LpStatus[prob.status])
    
    # Extract selected players into a new DataFrame
    selected_squad = players[[player_vars[i].varValue == 1 for i in players.index]].copy()
    selected_squad = selected_squad.sort_values(by="position")
    return selected_squad

def optimize_starting11(squad):
    # Create an optimization problem to choose the starting 11 from the squad.
    prob_start = LpProblem("FPL_Starting11_Selection", LpMaximize)
    
    # Decision variables for starting 11 selection from the squad indices
    start_vars = {i: LpVariable(f"start_{i}", cat=LpBinary) for i in squad.index}
    
    # Objective: maximize total expected points of the starting lineup
    prob_start += lpSum(start_vars[i] * squad.loc[i, "expected_points"] for i in squad.index), "Starting_Expected_Points"
    
    # Must choose exactly 11 players for the starting lineup
    prob_start += lpSum(start_vars[i] for i in squad.index) == 11, "Total_Starters"
    
    # Formation constraints:
    # Exactly 1 goalkeeper in starting 11
    prob_start += lpSum(start_vars[i] for i in squad.index if squad.loc[i, "position"] == "Goalkeeper") == 1, "Start_Goalkeeper"
    # At least 3 defenders
    prob_start += lpSum(start_vars[i] for i in squad.index if squad.loc[i, "position"] == "Defender") >= 3, "Start_Defenders"
    # At least 2 midfielders
    prob_start += lpSum(start_vars[i] for i in squad.index if squad.loc[i, "position"] == "Midfielder") >= 2, "Start_Midfielders"
    # At least 1 forward
    prob_start += lpSum(start_vars[i] for i in squad.index if squad.loc[i, "position"] == "Forward") >= 1, "Start_Forwards"
    
    prob_start.solve()
    print("Starting 11 Optimization Status:", LpStatus[prob_start.status])
    
    # Extract starting 11 players
    starting11 = squad[[start_vars[i].varValue == 1 for i in squad.index]].copy()
    starting11 = starting11.sort_values(by="position")
    return starting11

def select_captain(starting11):
    # Choose the player with the highest expected points in the starting 11 as captain
    captain = starting11.loc[starting11["expected_points"].idxmax()]
    return captain

def main():
    # Step 1: Fetch and prepare data
    data = fetch_fpl_data()
    players = prepare_data(data)
    
    # Step 2: Optimize full 15-player squad
    squad = optimize_squad(players, budget=100.0)
    print("\nOptimized 15-Player Squad:")
    print(squad[["name", "position", "team_name", "price", "expected_points"]])
    
    # Step 3: From the squad, select the starting 11
    starting11 = optimize_starting11(squad)
    print("\nOptimized Starting 11:")
    print(starting11[["name", "position", "team_name", "price", "expected_points"]])
    
    # Step 4: Select a captain from the starting 11
    captain = select_captain(starting11)
    print("\nSelected Captain:")
    print(captain[["name", "position", "team_name", "price", "expected_points"]])
    
    # Additional summary information
    squad_cost = squad["price"].sum()
    starting_cost = starting11["price"].sum()
    total_expected = squad["expected_points"].sum()
    starting_expected = starting11["expected_points"].sum()
    
    print("\n--- Summary ---")
    print(f"Squad Total Cost: {squad_cost} million")
    print(f"Squad Total Expected Points: {total_expected}")
    print(f"Starting 11 Cost: {starting_cost} million")
    print(f"Starting 11 Expected Points: {starting_expected}")

if __name__ == "__main__":
    main()
