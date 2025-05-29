# team_locations.py

import os
# Pro Leagues
from nfl_coords import NFL_COORDS
from nba_coords import NBA_COORDS
from mlb_coords import MLB_COORDS

#College Leagues
from fbs_coords import FBS_COORDS
from fcs_coords import FCS_COORDS
from d2_coords import dII_COORDS
from ncaa_basketball_coords import NCAA_BASKETBALL_COORDS

# Combined base dictionary
TEAM_COORDS = {}

TEAM_COORDS.update(NFL_COORDS)
TEAM_COORDS.update(NBA_COORDS)
TEAM_COORDS.update(MLB_COORDS)
TEAM_COORDS.update(FBS_COORDS)
TEAM_COORDS.update(FCS_COORDS)
TEAM_COORDS.update(DII_COORDS)
TEAM_COORDS.update(NCAA_BASKETBALL_COORDS)

# Alias mappings
TEAM_ALIASES = {
    "WSU": "Washington State",
    "FSU": "Florida State",
    "BAMA": "Alabama",
    "UCLA": "UCLA",
    "USC": "Southern California",
    "UNC": "North Carolina",
    "UCONN": "Connecticut",
    "UCF": "Central Florida",
    "UF": "Florida",
    "UGA": "Georgia",
    "LSU": "Louisiana State",
    "Ole Miss": "Mississippi",
    "Miss St": "Mississippi State",
    "BYU": "Brigham Young",
    "TCU": "Texas Christian",
    "UTEP": "Texas El Paso",
    "UTSA": "Texas San Antonio",
    "UMass": "Massachusetts",
    "UMD": "Maryland",
    "UM": "Miami FL",
    "UNC Charlotte": "Charlotte",
    "UNLV": "Nevada Las Vegas",
    "USF": "South Florida",
    "SDSU": "San Diego State",
    "ND": "Notre Dame",
    "Zona": "Arizona",
    "Zona State": "Arizona State",
    "OK State": "Oklahoma State",
    "UK": "Kentucky",
    "IU": "Indiana",
    "CU": "Colorado",
    "UVA": "Virginia",
    "VT": "Virginia Tech",
    "MSU": "Michigan State",
    "UMich": "Michigan",
    "OSU": "Ohio State",
    "NCSU": "NC State",
    "TAMU": "Texas A&M",
}

# Extended alias support for FBS, FCS, DII, and NCAA Basketball teams
TEAM_ALIASES.update({
    "Penn": "Pennsylvania",
    "Cal": "California",
    "ASU": "Arizona State",
    "ISU": "Iowa State",
    "PSU": "Penn State",
    "CSU": "Colorado State",
    "ECU": "East Carolina",
    "GSU": "Georgia State",
    "TSU": "Texas Southern",
    "GS": "Georgia Southern",
    "SIU": "Southern Illinois",
    "JMU": "James Madison",
    "NDSU": "North Dakota State",
    "SFA": "Stephen F. Austin",
    "UTA": "Texas Arlington",
    "UT": "Tennessee",
    "UTK": "Tennessee",
    "UWM": "Wisconsin Milwaukee",
    "WIU": "Western Illinois",
    "WVU": "West Virginia",
    "SJSU": "San Jose State",
    "NM State": "New Mexico State",
    "WI": "Wisconsin",
    "Mizzou": "Missouri",
})

def normalize_team_name(team_name: str) -> str:
    if not team_name:
        return ""
    name = team_name.strip()
    return TEAM_ALIASES.get(name, name)

def has_coordinates(team_name: str) -> bool:
    normalized_name = normalize_team_name(team_name)
    return normalized_name in TEAM_COORDS

def get_team_coordinates(team_name: str) -> tuple[float, float] | None:
    """
    Given a team name, normalize it and return (latitude, longitude).
    If not found, return None.
    """
    if not team_name:
        return None

    normalized_name = normalize_team_name(team_name)
    return TEAM_COORDS.get(normalized_name)

# Debugging aid
if __name__ == "__main__":
    test_teams = ["Tennessee", "FSU", "Washington State", "JMU", "USC", "UCLA"]
    for team in test_teams:
        coords = get_team_coordinates(team)
        print(f"{team} → {coords if coords else 'Not found'}")

